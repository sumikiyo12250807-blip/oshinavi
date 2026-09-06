# -*- coding: utf-8 -*-
"""7045 劇団四季「オペラ座の怪人」／名古屋 の「本日発売のまま締切が入っていない枠」を差し替える。

ヒールは安全弁で丸ごと止まった＝ぴあのパーサーが券種名を潰すので、
置き換えると「愛知 R9年 2/11〜2/27公演」のような登録側にしか無い枠が消えるから。
（feedback_pia_parser_flattens_slots）

だから **公演期間の文字が一致する枠だけ** 締切を当てる。
一致しない枠（スペシャルシート1月・2/11〜2/27）は触らずに残して、後日ぴあで再確認する。
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

APPLY = "--apply" in sys.argv

built = {e["id"]: e for e in json.load(open("tmp/rebuilt2_0906.json", encoding="utf-8"))}
b = built[7045]
BUNDLE = (b.get("links") or {}).get("pia")

# ぴあ側の「公演期間 → 締切」表を作る
pat = re.compile(r"（(.+?)公演）")
piamap = {}
for t in b.get("tickets") or []:
    mm = pat.search(t.get("type") or "")
    if mm:
        piamap[mm.group(1)] = (t.get("type"), t.get("date"))

h = open("index.html", encoding="utf-8").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))

for e in EVENTS:
    if e["id"] != 7045:
        continue
    for t in e.get("tickets") or []:
        if t.get("startDate") != "2026-09-06" or t.get("date") != "2026-09-06":
            continue
        mm = pat.search(t.get("type") or "")
        key = mm.group(1) if mm else None
        if key in piamap and "スペシャルシート" not in (t.get("type") or ""):
            newtype, newdate = piamap[key]
            print("差し替え  %s" % t.get("type"))
            print("      → %s （〜%s）" % (newtype, newdate))
            t["type"] = newtype
            t["date"] = newdate
        elif key in piamap and "スペシャルシート" in (t.get("type") or ""):
            # スペシャルシートは、ぴあ側に同じ公演期間のスペシャルシート枠がある時だけ当てる
            print("そのまま  %s（ぴあ側に同じ券種の枠が見当たらない＝後日再確認）" % t.get("type"))
        else:
            print("そのまま  %s（ぴあ側に対応する公演期間が無い＝後日再確認）" % t.get("type"))
        if not t.get("url"):
            t["url"] = BUNDLE
    for t in e.get("tickets") or []:
        if not t.get("url"):
            t["url"] = BUNDLE

if APPLY:
    open("index.html.bak_0906_shiki", "w", encoding="utf-8").write(h)
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    out = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]
    open("index.html", "w", encoding="utf-8").write(out)
    print("\n書き込み完了 (backup: index.html.bak_0906_shiki)")
else:
    print("\n（--apply で書き込む）")
