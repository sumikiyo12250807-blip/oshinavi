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

print("== 公演日が entry.date より後を指す ticket 文言（初日/千秋楽ズレ検査） ==")
# 「（... M/D公演）」「（... M/D〜M/D公演）」の“公演”直前の日付群を抜く
PAT = re.compile(r"（([^（）]*?)公演[^（）]*?）")
MD = re.compile(r"(\d{1,2})/(\d{1,2})")
found = 0
for e in past:
    ed = norm(e.get("date")); em, edd = int(ed[5:7]), int(ed[8:10])
    for i, t in enumerate(e.get("tickets") or []):
        txt = t.get("type") or ""
        for seg in PAT.findall(txt):
            for m in MD.finditer(seg):
                mo, da = int(m.group(1)), int(m.group(2))
                if not (1 <= mo <= 12 and 1 <= da <= 31): continue
                if (mo, da) > (em, edd):
                    print("  id=%s 枠#%d entry.date=%s / 文言の公演日 %d/%d :: %r" % (e.get("id"), i, ed, mo, da, txt[:90]))
                    found += 1
print("  該当 %d 件" % found)

print()
print("== 過去エントリの soldout / saleEnded / saleUntilSoldOut / saleEndUnknown / longrun / showSalePeriod ==")
for e in past:
    ef = {k: e[k] for k in ("longrun","saleEndUnknown","showSalePeriod","unverifiedNote") if k in e}
    tf = []
    for i, t in enumerate(e.get("tickets") or []):
        f = {k: t[k] for k in ("soldout","soldoutSince","saleEnded","saleEndedSince","saleUntilSoldOut","saleEndUnknown") if k in t}
        if f: tf.append((i, f))
    if ef or tf:
        print("  id=%s entry=%s tickets=%s" % (e.get("id"), ef, tf))

print()
print("== 疑義3件の全文 ==")
for e in EVENTS:
    if e.get("id") in (1242, 1637, 1904, "1242", "1637", "1904"):
        print(json.dumps(e, ensure_ascii=False, indent=1))
