# -*- coding: utf-8 -*-
import re, json, io

SRC = r"C:\Users\user\oshinavi\index.html"
OUT = r"C:\Users\user\oshinavi\tmp\_agentA_deep.txt"
TODAY = (2026, 8, 31)

with io.open(SRC, "r", encoding="utf-8") as f:
    html = f.read()
EVENTS = json.loads(re.search(r"const EVENTS\s*=\s*(\[.*?\]);", html, re.S).group(1))

DATE_RE = re.compile(r"(20\d{2})[-/](\d{1,2})[-/](\d{1,2})")
def norm(d):
    mm = DATE_RE.search(str(d)) if d else None
    return "%04d-%02d-%02d" % tuple(int(x) for x in mm.groups()) if mm else None

out = []
def W(s): out.append(s)

# 0) キー一覧の把握
keys = {}
tkeys = {}
for e in EVENTS:
    for k in e: keys[k] = keys.get(k, 0) + 1
    for t in (e.get("tickets") or []):
        for k in t: tkeys[k] = tkeys.get(k, 0) + 1
W("エントリのキー: " + ", ".join("%s=%d" % kv for kv in sorted(keys.items(), key=lambda x: -x[1])))
W("チケットのキー: " + ", ".join("%s=%d" % kv for kv in sorted(tkeys.items(), key=lambda x: -x[1])))
W("")

# 1) date が無い / パース不能
nodate = [e for e in EVENTS if not norm(e.get("date"))]
W("date がパース不能なエントリ: %d 件" % len(nodate))
for e in nodate[:30]:
    W("   id=%s date=%r artist=%r" % (e.get("id"), e.get("date"), (e.get("artist") or "")[:40]))
W("")

past = [e for e in EVENTS if norm(e.get("date")) and norm(e.get("date")) < "2026-08-31"]
W("date < 2026-08-31 のエントリ: %d 件" % len(past))
W("")

# 2) 過去エントリの全文字列を走査して 2026-08-31 以降を指しうる M/D を洗う
MD = re.compile(r"(\d{1,2})\s*/\s*(\d{1,2})")
def walk(o, path, acc):
    if isinstance(o, dict):
        for k, v in o.items(): walk(v, path + "." + str(k), acc)
    elif isinstance(o, list):
        for i, v in enumerate(o): walk(v, path + "[%d]" % i, acc)
    elif isinstance(o, str):
        acc.append((path, o))

W("=== 過去エントリ内の「8/31以降」を指す文字列 ===")
hits_by_id = {}
for e in past:
    acc = []
    walk(e, "", acc)
    hs = []
    for p, s in acc:
        if p.endswith(".url") or p.endswith(".officialUrl") or "url" in p.lower(): continue
        for m in MD.finditer(s):
            mo, da = int(m.group(1)), int(m.group(2))
            if not (1 <= mo <= 12 and 1 <= da <= 31): continue
            if (mo, da) >= TODAY or mo <= 7:  # 9-12月/8/31以降、または翌年扱いになりうる1-7月
                hs.append("%s=%r [%d/%d]" % (p, s[:80], mo, da))
                break
    if hs:
        hits_by_id[e.get("id")] = hs
for eid, hs in hits_by_id.items():
    W("id=%s" % eid)
    for h in hs: W("    " + h)
W("(該当 %d 件)" % len(hits_by_id))
W("")

# 3) 過去エントリの ticket 日付フィールドの分布
W("=== 過去エントリで startDate/date が 2026-08-31 以降のチケット ===")
n = 0
for e in past:
    for i, t in enumerate(e.get("tickets") or []):
        td, ts = norm(t.get("date")), norm(t.get("startDate"))
        if (td and td >= "2026-08-31") or (ts and ts >= "2026-08-31"):
            n += 1
            W("id=%s 枠#%d start=%s end=%s type=%r soldOut=%r saleEnded=%r status=%r"
              % (e.get("id"), i, ts, td, (t.get("type") or "")[:70], t.get("soldOut"), t.get("saleEnded"), t.get("status")))
W("(該当 %d 枠)" % n)
W("")

# 4) 過去エントリの表示に関わるフラグ
W("=== 過去エントリのフラグ (verified/soldOut/saleEnded/hidden 等) ===")
for e in past:
    flags = {k: e.get(k) for k in ("verified", "soldOut", "saleEnded", "hidden", "soldoutSince", "status", "endDate", "dateEnd", "showDates") if k in e}
    if flags:
        W("id=%s %s" % (e.get("id"), flags))
W("")

with io.open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("wrote", OUT)
