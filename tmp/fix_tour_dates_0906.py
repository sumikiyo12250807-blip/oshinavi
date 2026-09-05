# -*- coding: utf-8 -*-
"""483 羊文学 / 1305 サバシスター の「公演日が千秋楽になっていない」を直し、
ぴあの実ページから作り直した枠のうち未登録のものを足す。

なぜ必要か＝どちらも entry.date が 2026-09-04（＝もう過ぎた公演日）のままで、
チケットはまだ売っているのに翌朝の削除ルートでカードごと消える状態だった。
裏取り＝ぴあのツアーページを開いて全公演日を列挙（羊文学11公演・サバシスター6公演）。

既存の枠は1つも消さない（DELETE_GATE 1.）。足すだけ・日付と会場を直すだけ。
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

APPLY = "--apply" in sys.argv

built = {e["id"]: e for e in json.load(open("tmp/rebuilt_0906.json", encoding="utf-8"))}

h = open("index.html", encoding="utf-8").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))

# 会場も直す（既存は終わった公演の会場になっている）
VENUE_FIX = {1305: built[1305].get("venue")}

changed = []
for e in EVENTS:
    b = built.get(e["id"])
    if not b:
        continue
    olddate, newdate = e.get("date"), b.get("date")
    have = {(t.get("type"), t.get("date")) for t in (e.get("tickets") or [])}
    added = [t for t in (b.get("tickets") or []) if (t.get("type"), t.get("date")) not in have]
    e["tickets"] = (e.get("tickets") or []) + added
    e["date"] = newdate
    oldvenue = e.get("venue")
    if e["id"] in VENUE_FIX and VENUE_FIX[e["id"]]:
        e["venue"] = VENUE_FIX[e["id"]]
    changed.append((e["id"], e.get("artist"), olddate, newdate, added, oldvenue, e.get("venue")))

for i, a, od, nd, added, ov, nv in changed:
    print("id=%d %s" % (i, a))
    print("   公演日 %s → %s" % (od, nd))
    if ov != nv:
        print("   会場   %s → %s" % (ov, nv))
    if added:
        for t in added:
            print("   ＋枠   %s （〜%s）" % (t.get("type"), t.get("date")))
    else:
        print("   ＋枠   なし（ぴあの買える枠は全部登録済み）")

if APPLY:
    open("index.html.bak_0906_tourdate", "w", encoding="utf-8").write(h)
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    out = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]
    open("index.html", "w", encoding="utf-8").write(out)
    print("\n書き込み完了 (backup: index.html.bak_0906_tourdate)")
else:
    print("\n（--apply で書き込む）")
