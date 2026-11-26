#!/usr/bin/env python3
"""Pass 4 gap check: which numbers-with-units and named concepts in the raw
notes never appear anywhere in the course data? Prints misses per chapter.
Usage: python3 course/gap_check.py [--chapter ch12]"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
notes = open(os.path.join(ROOT, "..", "notes", "raw-notes.md"), encoding="utf8").read()
course = json.load(open(os.path.join(ROOT, "site", "course.json"), encoding="utf8"))
corpus = json.dumps(course, ensure_ascii=False).lower()

STOP = set("""The This That These Those When What Why How Who Which Not And But For With From Into Over Under After Before
Part Chapter Fig Figure Table Example Argument Interview Note Notes Read Use Each Every One Two Three Four Five Six Seven
Practice Key Main Most Many Some Also If It In On Of To At By As Or An A Is Are Was Be Do No Yes All Any Both Then Than
Good Bad New Old Fast Slow Real True False Not Only Just Very Much More Less Same Different Book Authors Book's Then
Guest Honeycomb Charity Liz George Austin Pass Raw I We You They He She Interview Angles Q A""".split())

num_re = re.compile(r"\b\d[\d,.]*\s?(?:%|ms|s\b|min|minutes|hours?|h\b|days?|weeks?|months?|years?|GB|TB|PB|MB|x\b|k\b|M\b|B\b|vCPU|cores?|ppm|LOC)", re.I)
name_re = re.compile(r"\b(?:[A-Z][a-z]+(?:[A-Z][a-z]+)+|[A-Z]{2,}[a-z]*\d*|[A-Z][a-z]+(?:\s[A-Z][a-z]+)+)\b")

chapters = re.split(r"\n## (Ch\d+[^\n]*)", notes)
only = sys.argv[sys.argv.index("--chapter") + 1] if "--chapter" in sys.argv else None
total = 0
for i in range(1, len(chapters), 2):
    head, body = chapters[i], chapters[i + 1]
    cid = "ch%02d" % int(re.match(r"Ch(\d+)", head).group(1))
    if only and cid != only:
        continue
    nums = sorted({m.group(0).strip() for m in num_re.finditer(body)})
    names = sorted({m.group(0) for m in name_re.finditer(body)} - STOP)
    miss_n = [n for n in nums if n.lower().replace(" ", "") not in corpus.replace(" ", "")]
    miss_c = [n for n in names if n.lower() not in corpus and n.split()[0] not in STOP]
    total += len(miss_n) + len(miss_c)
    print(f"\n{cid} {head[:60]}\n  numbers missing ({len(miss_n)}/{len(nums)}): {', '.join(miss_n[:40])}\n  names missing ({len(miss_c)}/{len(names)}): {', '.join(miss_c[:60])}")
print("\nTOTAL MISSES:", total)
