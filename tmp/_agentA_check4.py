# -*- coding: utf-8 -*-
import re, json, io
SRC = r"C:\Users\user\oshinavi\index.html"
with io.open(SRC, "r", encoding="utf-8") as f:
    html = f.read()
EVENTS = json.loads(re.search(r"const EVENTS\s*=\s*(\[.*?\]);", html, re.S).group(1))
DATE_RE = re.compile(r"(20\d{2})[-/](\d{1,2})[-/](\d{1,2})")
def norm(d):
    mm = DATE_RE.search(str(d)) if d else None
    return "%04d-%02d-%02d" % tuple(int(x) for x in mm.groups()) if mm else None
past = [e for e in EVENTS if norm(e.get("date")) and norm(e.get("date")) < "2026-08-31"]
TODAY = (8, 31)

def walk(o, path, acc):
    if isinstance(o, dict):
        for k, v in o.items(): walk(v, path + "." + str(k), acc)
    elif isinstance(o, list):
        for i, v in enumerate(o): walk(v, path + "[%d]" % i, acc)
    elif isinstance(o, str):
        acc.append((path, o))

# M/D と M月D日 の両方
MD = re.compile(r"(\d{1,2})\s*[/月]\s*(\d{1,2})")
print("== 過去67件の全文字列中、8/31以降(9〜12月含む)を指す日付表記 ==")
hit_ids = []
for e in past:
    acc = []; walk(e, "", acc)
    hs = []
    for p, s in acc:
        if "url" in p.lower() or "amazon" in s or s.startswith("http"): continue
        for m in MD.finditer(s):
            mo, da = int(m.group(1)), int(m.group(2))
            if not (1 <= mo <= 12 and 1 <= da <= 31): continue
            if (mo, da) >= TODAY and mo >= 8:
                hs.append("%s = %r  →[%d/%d]" % (p, s[:90], mo, da))
    if hs:
        hit_ids.append(e.get("id"))
        print("id=%s  date=%s  %s" % (e.get("id"), norm(e.get("date")), (e.get("artist") or "")[:40]))
        for h in sorted(set(hs)): print("     " + h)
print("該当 %d 件: %s" % (len(hit_ids), hit_ids))
