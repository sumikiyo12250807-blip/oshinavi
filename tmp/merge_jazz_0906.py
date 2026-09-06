# -*- coding: utf-8 -*-
"""『ジャズ大名』が4エントリに割れているのを1本に畳む（2026-09-05 から保留だった件）。

証拠＝今朝ぴあから拾った 7046 の eventBundleCd=b2670869 が、既存3エントリの枠を全部束ねていた。
  5568 神奈川 12/19〜12/29（eventCd=2623801）
  5439 富山  R9年 1/23〜1/24（eventCd=2632133）
  5436 愛知  R9年 1/30〜1/31（eventCd=2630689）
さらに bundle にしか無い「先行（神奈川 12/20〜12/26公演）〜9/9 23:59」がある＝取りこぼし。

残すのは id が最小の 5436。
🚨各枠には会場別の eventCd を焼き込む（feedback_tour_per_ticket_url）。
　bundle 1本に潰すと、どの会場の売り場に飛べばいいか分からなくなる。
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

APPLY = "--apply" in sys.argv
KEEP = 5436
DROP = {5439, 5568, 7046}
KANAGAWA = "https://t.pia.jp/pia/event/event.do?eventCd=2623801"   # 5568 の売り場

h = open("index.html", encoding="utf-8").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))
byid = {e["id"]: e for e in EVENTS}


def pia(e):
    return ((e.get("links") or {}).get("pia") or "")


# 既存3エントリの (券種名, 締切) → 会場別URL を作る
urlmap = {}
for eid in (5436, 5439, 5568):
    e = byid[eid]
    for t in e.get("tickets") or []:
        urlmap[(t.get("type"), t.get("date"))] = t.get("url") or pia(e)

keep = byid[KEEP]
merged = []
seen = set()
for eid in (5568, 5439, 5436, 7046):          # 公演日の早い順に並べる
    for t in byid[eid].get("tickets") or []:
        k = (t.get("type"), t.get("date"))
        if k in seen:
            continue
        seen.add(k)
        t = dict(t)
        if not t.get("url"):
            t["url"] = urlmap.get(k) or (KANAGAWA if "神奈川" in (t.get("type") or "") else pia(byid[eid]))
        merged.append(t)

oldvenue, olddate = keep.get("venue"), keep.get("date")
keep["tickets"] = merged
keep["venue"] = "全国ツアー（KAAT 神奈川芸術劇場 ホール／富山 オーバード・ホール 中ホール／刈谷市総合文化センター アイリス 大ホール）"
keep["date"] = "2027-01-31"

print("残す id=%d 『ジャズ大名』" % KEEP)
print("  公演日 %s → %s" % (olddate, keep["date"]))
print("  会場   %s → %s" % (oldvenue, keep["venue"]))
for t in merged:
    print("  枠 %s （〜%s）→ %s" % (t.get("type"), t.get("date"), t.get("url")))
print("  欠番にする: %s" % sorted(DROP))

nourl = [t.get("type") for t in merged if not t.get("url")]
if nourl:
    print("🚨 飛び先が空の枠がある＝止める: %s" % nourl)
    sys.exit(1)
print("✅ 飛び先が空の枠はゼロ／枠 %d本（畳む前は 1+1+1+4=7本、重複を外して %d本）" % (len(merged), len(merged)))

kept = [e for e in EVENTS if e["id"] not in DROP]
if APPLY:
    open("index.html.bak_0906_jazz", "w", encoding="utf-8").write(h)
    new_arr = json.dumps(kept, ensure_ascii=False, indent=2)
    out = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]
    mo = re.search(r"(  const NEW_ORDER = \[)([^\]]*)(\];)", out)
    ids = [int(x) for x in mo.group(2).replace("\n", "").split(",") if x.strip()]
    left = [i for i in ids if i not in DROP]
    out = out[:mo.start()] + mo.group(1) + ", ".join(str(i) for i in left) + mo.group(3) + out[mo.end():]
    open("index.html", "w", encoding="utf-8").write(out)
    print("書き込み完了 (backup: index.html.bak_0906_jazz)")
else:
    print("（--apply で書き込む）")
