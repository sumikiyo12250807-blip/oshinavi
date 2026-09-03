# -*- coding: utf-8 -*-
import re, io

ids = [1782, 2072, 2359, 2630, 2631]
out = io.open(r"C:\Users\user\oshinavi\tmp\check6_detail_out.txt", "w", encoding="utf-8")

def strip(h):
    h = re.sub(r"<script.*?</script>", " ", h, flags=re.S)
    h = re.sub(r"<style.*?</style>", " ", h, flags=re.S)
    h = re.sub(r"<[^>]+>", "\n", h)
    h = re.sub(r"[ \t\u3000]+", " ", h)
    lines = [l.strip() for l in h.split("\n")]
    return [l for l in lines if l]

for eid in ids:
    raw = io.open(r"C:\Users\user\oshinavi\tmp\pia_%s.html" % eid, encoding="utf-8").read()
    out.write("########## id=%s\n" % eid)
    # region around each __status
    for m in re.finditer(r'__status (is-[\w-]+)">', raw):
        s = max(0, m.start() - 2500)
        e = min(len(raw), m.end() + 1500)
        out.write("---- status block ----\n")
        out.write(" | ".join(strip(raw[s:e])) + "\n")
    # performance date list section
    for key in ["公演日", "日程", "会場"]:
        pass
    idx = raw.find("perf")
    out.write("---- lines containing 2026/ ----\n")
    for l in strip(raw):
        if re.search(r"2026[/年]", l):
            out.write("  " + l + "\n")
    out.write("\n\n")
out.close()
print("ok")
