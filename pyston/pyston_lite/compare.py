"""
Testing script, for identifying opportunities to make pyston-lite faster

Usage:
    make perf_report
    make perf_report_baseline
    python3 compare.py

Will try to identify the largest differences between the two perf reports
"""

from collections import defaultdict
import subprocess

baseline = defaultdict(int)
lite = defaultdict(int)

def parse(fn):
    r = defaultdict(int)
    for l in subprocess.check_output(["perf", "report", "-n", "-i", fn]).decode("utf8").split('\n'):
        if l.startswith("#"):
            continue
        if '%' not in l:
            continue

        l = l.split()
        if '[k]' in l:
            l[-1] = "kernel"
        r[l[-1]] = int(l[1])
    return r

baseline = parse("perf_baseline.data")
lite = parse("perf_lite.data")

baseline_total = sum(baseline.values())
lite_total = sum(lite.values())

print("%d\t%d\t" % (baseline_total, lite_total), "%+.2f%%" % ((lite_total - baseline_total) / baseline_total * 100.0))
print("="*40)

for d in (lite, baseline):
    for k, v in list(d.items()):
        if "EvalFrame" in k:
            d["_EvalFrame"] += d.pop(k)

all = set(baseline)
all.update(lite)

diffs = []
for k in all:
    diffs.append((abs(baseline.setdefault(k, 0) - lite.setdefault(k, 0)), k))

diffs.sort(reverse=True)
for t in diffs[:10]:
    k = t[-1]
    f = baseline[k]
    l = lite[k]
    print("%d\t%d\t" % (f, l), "%+.2f%%" % ((l - f) / baseline_total * 100.0), k)
