# -*- coding: utf-8 -*-
"""各枠が「どのぴあページから来たか」を特定して ticket.url に刻む。

なぜ＝build_pia_entries に複数URLを渡すと2本目以降の枠に url が付かない
（feedback_build_pia_multiurl_loses_ticket_url）。刻まないと
 ①カードがその枠を売っていないページに飛ぶ ②reconcile がそのページしか見ず「0枠」と誤報する。

やり方＝そのエントリの全ぴあURLを **1本ずつ** build にかけ、出てきた枠のバッジ文言で対応を取る。
「県＋M/D が一致したら刻む」式の自動当てはめはしない（既存の別枠を巻き込む・2026-08-23の反省）。
バッジ文言が**完全一致**した枠だけ刻む。

  python tmp/trace_slot_url_0826.py 571,761,1098          # 調べるだけ
  python tmp/trace_slot_url_0826.py 571,761,1098 --apply  # url を刻む
"""
import json
import re
import sys

sys.path.insert(0, "tools")
sys.stdout.reconfigure(encoding="utf-8")

import build_pia_entries as bpe
import heal_stale_deadlines as heal

APPLY = "--apply" in sys.argv
IDS = [int(x) for x in sys.argv[1].split(",")]

h = open("index.html", encoding="utf-8").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))
by_id = {e["id"]: e for e in EVENTS}

# --urls-from <html> ＝そのファイル（統合前のバックアップ等）に刻まれていたURLも探索対象に足す。
# 統合で url が落ちると pia_urls が縮んで、枠の出どころが追えなくなるため。
EXTRA = {}
if "--urls-from" in sys.argv:
    _p = sys.argv[sys.argv.index("--urls-from") + 1]
    _src = open(_p, encoding="utf-8").read()
    _mm = re.search(r"(  const EVENTS = )(\[.*?\])(;)", _src, re.S)
    for e in json.loads(_mm.group(2)):
        EXTRA[e["id"]] = heal.pia_urls(e)

fixed = 0
for eid in IDS:
    ev = by_id.get(eid)
    if not ev:
        print("id=%d が無い" % eid)
        continue
    urls = heal.pia_urls(ev)
    for u in EXTRA.get(eid, []):
        if u not in urls:
            urls.append(u)
    print("=" * 70)
    print("id=%d %s （枠%d / URL%d本）" % (eid, ev.get("artist"), len(ev.get("tickets") or []), len(urls)))
    # バッジ文言 → そのURL
    origin = {}
    for u in urls:
        try:
            ne = bpe.build({"newid": eid, "artist": ev.get("artist", ""), "urls": [u]})
        except Exception as ex:
            print("   ⚠️%s … %s" % (u, type(ex).__name__))
            continue
        if not ne:
            print("   －%s … このページには買える枠が無い" % u)
            continue
        for t in (ne.get("tickets") or []):
            origin.setdefault(t.get("type"), u)
    for t in ev.get("tickets") or []:
        ty = t.get("type")
        src = origin.get(ty)
        if not src:
            print("   ?  %s … どのページからも出ない（要目視）" % ty)
            continue
        if t.get("url") == src:
            print("   ✅ %s … 既に正しいURL" % ty)
            continue
        print("   🔧 %s\n        %s → %s" % (ty, t.get("url"), src))
        t["url"] = src
        fixed += 1

print("")
if APPLY and fixed:
    open("index.html.bak_0826_trace", "w", encoding="utf-8").write(h)
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    open("index.html", "w", encoding="utf-8").write(
        h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
    print("%d枠に刻んだ (backup: index.html.bak_0826_trace)" % fixed)
else:
    print("%d枠が対象（--apply で書き込む）" % fixed)
