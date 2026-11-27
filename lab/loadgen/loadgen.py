"""Traffic for the lab: many distinct users, a few tiers and payment methods, and a small
share of requests using the new discount-code format (the one the fault hits).

  python loadgen.py --url http://localhost:8080 --rps 20 --seconds 600
"""
import argparse
import random
import time

import requests

TIERS = ["free"] * 6 + ["pro"] * 3 + ["enterprise"]
METHODS = ["card"] * 6 + ["paypal"] * 2 + ["gift_card", "bank_transfer"]
PLATFORMS = ["web"] * 5 + ["ios"] * 3 + ["android"] * 2


def one_request(rng: random.Random) -> dict:
    user = f"u-{rng.randrange(20000):05d}"
    r = rng.random()
    code = f"NEW-{rng.randrange(10**6):06d}" if r < 0.08 else (f"SAVE{rng.randrange(100)}" if r < 0.30 else "")
    return {"user_id": user, "email": f"{user}@example.com", "tier": rng.choice(TIERS), "items": rng.randint(1, 6),
            "payment_method": rng.choice(METHODS), "platform": rng.choice(PLATFORMS), "discount_code": code}


def run(url: str, count=None, rps: float = 0, seconds: float = 0, seed=None) -> dict:
    rng, session, stats = random.Random(seed), requests.Session(), {"ok": 0, "error": 0}
    deadline = time.monotonic() + seconds if seconds else None
    n = 0
    while (count is None or n < count) and (deadline is None or time.monotonic() < deadline):
        try:
            ok = session.post(f"{url}/checkout", json=one_request(rng), timeout=10).status_code == 200
        except requests.RequestException:
            ok = False
        stats["ok" if ok else "error"] += 1
        n += 1
        if rps:
            time.sleep(rng.expovariate(rps))
    return stats


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:8080")
    ap.add_argument("--rps", type=float, default=20)
    ap.add_argument("--seconds", type=float, default=0, help="0 = run until stopped")
    ap.add_argument("--count", type=int, default=None)
    a = ap.parse_args()
    print(run(a.url, a.count, a.rps, a.seconds))
