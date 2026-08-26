# -*- coding: utf-8 -*-
"""統合で足した枠に「売り場のURL」を刻む。

なぜ＝build_pia_entries は複数URLを渡すと2本目以降の枠に ticket.url を付けない
（feedback_build_pia_multiurl_loses_ticket_url）。刻まないと
 ①カードが links.pia（その枠を売っていないページ）に飛ぶ
 ②reconcile_pia がそのページしか見ないので、生きた枠を「0枠」と誤報する
今日の統合で reconcile が STALE を出した4件がこれ。実ページで枠の実在を確認済み。

🚨「県＋M/D が一致したら刻む」式の自動当てはめはしない（既存の別枠を巻き込む）。
　 対象は (id, バッジ文言の先頭一致, URL) で手で列挙する。
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

FIX = [
    (503, "2次プレリザーブ（京都・大阪", "https://t.pia.jp/pia/event/event.do?eventCd=2628173"),
    (503, "一般発売（京都・大阪", "https://t.pia.jp/pia/event/event.do?eventCd=2628173"),
    (650, "一般発売（神奈川 11/28公演）", "https://t.pia.jp/pia/event/event.do?eventCd=2633430"),
    (2500, "5次プリセール（栃木 12/6公演）", "https://t.pia.jp/pia/event/event.do?eventBundleCd=b2669435"),
    (2500, "一般発売（栃木 12/6公演）", "https://t.pia.jp/pia/event/event.do?eventBundleCd=b2669435"),
    (4041, "プレリザーブ（秋田・神奈川", "https://t.pia.jp/pia/event/event.do?eventBundleCd=b2670131"),
]

h = open("index.html", encoding="utf-8").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))
by_id = {e["id"]: e for e in EVENTS}

n = 0
for eid, prefix, url in FIX:
    ev = by_id.get(eid)
    if not ev:
        print("id=%d が無い" % eid)
        continue
    hit = [t for t in (ev.get("tickets") or []) if (t.get("type") or "").startswith(prefix)]
    if len(hit) != 1:
        print("id=%-5d ⚠️「%s」に前方一致する枠が %d 件＝触らない" % (eid, prefix, len(hit)))
        continue
    t = hit[0]
    print("id=%-5d %s | url %s → %s" % (eid, t.get("type"), t.get("url"), url))
    t["url"] = url
    n += 1

if "--apply" in sys.argv:
    open("index.html.bak_0826_fixurl", "w", encoding="utf-8").write(h)
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    open("index.html", "w", encoding="utf-8").write(
        h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
    print("")
    print("%d枠に刻んだ (backup: index.html.bak_0826_fixurl)" % n)
else:
    print("")
    print("%d枠が対象（--apply で書き込む）" % n)
