import random
import time
import unittest

from colstore import Column, Store, hedged_map, tsdb_series_count


def events(n, t_start, seed=0):
    rng = random.Random(seed)
    for i in range(n):
        yield {"ts": t_start + i, "service": rng.choice(["api", "web"]), "status": rng.choice([200, 200, 200, 500]),
               "duration_ms": rng.randint(5, 500), "user_id": f"u{rng.randint(0, 99999)}"}


class ColumnTests(unittest.TestCase):
    def test_dictionary_encoding_and_nulls(self):
        c = Column()
        for v in ["GET", "GET", None, "POST", "GET"]:
            c.append(v)
        self.assertEqual(c.rev, ["GET", "POST"])
        self.assertEqual(c.codes, [0, 0, -1, 1, 0])


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.s = Store(max_rows=1000)
        for e in events(5000, 0):
            self.s.ingest(e)

    def test_segments_finalised_by_row_count(self):
        self.assertEqual(len(self.s.segments), 5)
        self.assertTrue(all(seg.finalized for seg in self.s.segments))

    def test_time_pruning_reads_only_overlapping_segments(self):
        res, scanned = self.s.query(1500, 2400, columns=("status",), group_by=("status",))
        self.assertEqual(scanned, 2)
        self.assertEqual(sum(v for _, v in res), 901)
        untouched = [seg for seg in self.s.segments if seg.reads == 0]
        self.assertEqual(len(untouched), 3)

    def test_group_by_aggregate_top_k(self):
        res, _ = self.s.query(0, 5000, columns=(), group_by=("service", "status"), agg="count", top_k=2)
        self.assertEqual(len(res), 2)
        self.assertTrue(all(k[1] == 200 for k, _ in res))

    def test_only_referenced_columns_are_read(self):
        seg = self.s.segments[0]
        before = seg.reads
        self.s.query(0, 999, columns=("status",), group_by=("status",))
        self.assertEqual(seg.reads - before, 2)  # status + ts, never user_id or duration

    def test_calculated_field_coalesce_for_rename(self):
        s = Store()
        s.ingest({"ts": 1, "session_id": "old"})
        s.ingest({"ts": 2, "session.id": "new"})
        res, _ = s.query(0, 3, columns=(), group_by=("session_migration",),
                         calculated={"session_migration": (("session.id", "session_id"),
                                                            lambda a, b: a if a is not None else b)})
        self.assertEqual(sorted(k[0] for k, _ in res), ["new", "old"])

    def test_parallel_with_hedging_matches_serial(self):
        serial, _ = self.s.query(0, 5000, columns=(), group_by=("status",), agg="avg", field_="duration_ms")
        par, _ = self.s.query(0, 5000, columns=(), group_by=("status",), agg="avg", field_="duration_ms",
                              parallel=True)
        self.assertEqual(dict(serial), dict(par))


class HedgingTests(unittest.TestCase):
    def test_straggler_is_rescued(self):
        calls = {}

        def work(i):
            calls[i] = calls.get(i, 0) + 1
            if i == 9 and calls[i] == 1:  # first attempt hangs
                time.sleep(2)
            return i * 2

        t = time.time()
        out = hedged_map(work, list(range(10)))
        self.assertEqual(out, [i * 2 for i in range(10)])
        self.assertLess(time.time() - t, 1.5)
        self.assertEqual(calls[9], 2)


class CardinalityTests(unittest.TestCase):
    def test_adding_user_id_explodes_series(self):
        evs = list(events(5000, 0))
        low = tsdb_series_count(evs, ("service", "status"))
        high = tsdb_series_count(evs, ("service", "status", "user_id"))
        self.assertEqual(low, 4)
        self.assertGreater(high, 1000 * low)


if __name__ == "__main__":
    unittest.main()
