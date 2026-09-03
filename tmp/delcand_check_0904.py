# -*- coding: utf-8 -*-
"""check_expired の削除候補(公演終了済)について、
「本当に全公演が終わっているか」を枠のtypeに書かれた公演日から機械で確かめる。
DELETE_GATE「公演当日は残して翌朝消す」に引っかかる子を弾く。"""
import json, re, io, datetime

TODAY = "2026-09-04"
IDS = [1782, 2072, 2359, 2630, 2631, 3114, 6192]

html = io.open("index.html", encoding="utf-8").read()
events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\s*\n", html, re.S).group(1))
by_id = {e.get("id"): e for e in events}

# type の中の「M/D公演」「M/D〜M/D公演」を全部拾って最遅の公演日を出す
def show_dates(text, year=2026):
    out = []
    for m in re.finditer(r"(\d{1,2})/(\d{1,2})(?:〜(\d{1,2})/(\d{1,2}))?公演", text):
        out.append("%04d-%02d-%02d" % (year, int(m.group(1)), int(m.group(2))))
        if m.group(3):
            out.append("%04d-%02d-%02d" % (year, int(m.group(3)), int(m.group(4))))
    return out

buf = []
flag = []
for i in IDS:
    e = by_id.get(i)
    if not e:
        buf.append("id=%s NOTFOUND" % i); continue
    all_sd = []
    lines = []
    for t in e.get("tickets", []):
        sds = show_dates(t.get("type", ""))
        all_sd += sds
        lines.append("    type=%s\n      枠の公演日=%s  受付終了=%s soldout=%s url=%s" % (
            t.get("type"), ",".join(sds) or "(なし)", t.get("date"), t.get("soldout"), (t.get("url") or "")[:90]))
    latest = max(all_sd) if all_sd else None
    ok = (latest is None) or (latest < TODAY)
    buf.append("=" * 66)
    buf.append("id=%s  %s" % (i, e.get("name")))
    buf.append("  entry.date=%s  枠から読める最遅公演日=%s  -> %s" % (
        e.get("date"), latest, "終了済み" if ok else "🚨まだ未来/当日の公演がある"))
    buf += lines
    if not ok:
        flag.append((i, e.get("name"), latest))

io.open("tmp/delcand_check_0904.txt", "w", encoding="utf-8").write("\n".join(buf))
print("WROTE tmp/delcand_check_0904.txt")
print("HOLD=%d" % len(flag))
for i, n, l in flag:
    print("  HOLD id=%s latest_show=%s" % (i, l))
