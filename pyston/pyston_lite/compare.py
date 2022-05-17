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

full = defaultdict(int)
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

full = parse("perf_baseline.data")
lite = parse("perf_lite.data")

full_total = sum(full.values())
lite_total = sum(lite.values())

print("%d\t%d\t" % (full_total, lite_total), "%+.2f%%" % ((lite_total - full_total) / full_total * 100.0))
print("="*40)

'''
full['frame_dealloc'] += full.pop('frame_dealloc_notrashcan', 0)
full['_PyObject_Free'] += full.pop('PyObject_Free')
full['unicode_decode_utf8.constprop.0'] += full.pop('unicode_decode_utf8')
lite["_PyObject_Malloc"] += lite.pop('pymalloc_alloc.isra.0.part.0')
for d in (lite, full):
    d["PyObject_RichCompare"] += d.pop("PyObject_RichCompareBool")
    d["PyObject_GenericGetAttr"] += d.pop("_PyObject_GenericGetAttrWithDict")
    d["PyObject_GenericSetAttr"] += d.pop("_PyObject_GenericSetAttrWithDict", 0)
'''

all = set(full)
all.update(lite)

diffs = []
for k in all:
    diffs.append((abs(full.setdefault(k, 0) - lite.setdefault(k, 0)), k))

diffs.sort(reverse=True)
for t in diffs[:10]:
    k = t[-1]
    f = full[k]
    l = lite[k]
    print("%d\t%d\t" % (f, l), "%+.2f%%" % ((l - f) / full_total * 100.0), k)
