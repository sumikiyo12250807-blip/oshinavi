# -*- coding: utf-8 -*-
"""reconcile の STALE が「本当に販売終了」か「別の売り場から統合した枠」かを見分ける。
[[feedback_build_pia_multiurl_loses_ticket_url]]＝STALEには2種類ある。
reconcile はエントリの links.pia ＋ 全 ticket.url を見るので、url が刻まれていれば
その売り場は見ているはず＝刻まれているのに STALE なら本当に終了した疑いが濃い。
"""
import json, re, io

LOG = "tmp/recon_missing_0904.txt"
html = io.open("index.html", encoding="utf-8", newline="").read()
events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", html, re.S).group(1))
by_id = {e.get("id"): e for e in events}

cur = None
rows = []
for ln in io.open(LOG, encoding="utf-8"):
    m = re.match(r"^[^\s]*\s*id=(\d+)\s", ln)
    if m:
        cur = int(m.group(1)); continue
    m2 = re.search(r"STALE 登録「(.+?)」\((\d{4}-\d{2}-\d{2})\)", ln)
    if m2 and cur:
        rows.append((cur, m2.group(1), m2.group(2)))

buf = []
for eid, ty, dt in rows:
    e = by_id.get(eid)
    hit = None
    for t in (e or {}).get("tickets", []):
        if t.get("type") == ty and t.get("date") == dt:
            hit = t; break
    buf.append("id=%s %s" % (eid, (e or {}).get("name")))
    buf.append("   枠: %s (〜%s)" % (ty, dt))
    if hit is None:
        buf.append("   -> 🚨その枠が見つからない（文言が変わった？）")
    else:
        buf.append("   -> url=%s" % (hit.get("url") or "(url無し＝links.piaしか見ていない＝偽陽性の疑い)"))
    buf.append("   links.pia=%s" % ((e or {}).get("links") or {}).get("pia"))
io.open("tmp/check_stale_missing_0904.txt", "w", encoding="utf-8").write("\n".join(buf))
print("STALE_ROWS=%d" % len(rows))
n_nourl = sum(1 for eid, ty, dt in rows
              if not next((t.get("url") for t in (by_id.get(eid) or {}).get("tickets", [])
                           if t.get("type") == ty and t.get("date") == dt), None))
print("url無し（偽陽性の疑い）=%d / url有り（本当に終了の疑い）=%d" % (n_nourl, len(rows) - n_nourl))
