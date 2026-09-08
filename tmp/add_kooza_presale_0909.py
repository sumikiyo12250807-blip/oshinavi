# -*- coding: utf-8 -*-
"""id3674 クーザ＝ぴあの「プリセール」7枠が丸ごと登録に無かったので足す。

🚨見つかり方＝reconcile_pia が「登録7枠 / ぴあ買える14枠」と言うのに **MISSINGは0** だった。
   フジテレビダイレクト2次先行とプリセールが**まったく同じ締切(〜9/18 23:59)**なので、
   照合が枠の対を確定できず skip に落ちていた（QCカバレッジ 0/7・skip7）。
   ＝**「MISSING 0」は「取りこぼし無し」ではない。枠数が合わない時は必ず中身を見る。**
実ページで確認（2026-09-09・tools/build_pia_entries.parse_cards で全カードを列挙）
   2626484 … プリセール【2/24〜28】
   2626485 … プリセール【3/1〜9】【3/11〜20】【3/21〜30】
   2626487 … プリセール【4/2〜10】【4/11〜20】【4/21〜25】
   どれも [受付中] ・ 受付期間「～ 2026/9/18(金) 23:59」
使い方: python tmp/add_kooza_presale_0909.py [--apply]
"""
import io, json, re, sys

sys.stdout.reconfigure(encoding="utf-8")
U = "https://t.pia.jp/pia/event/event.do?eventCd=%s"
ROWS = [
    ("プリセール【2/24（水）～28（日）公演】（東京 R9年 2/24〜2/28公演）〜9/18 23:59", "2626484"),
    ("プリセール【3/1（月）～9（火）公演】（東京 R9年 3/1〜3/9公演）〜9/18 23:59", "2626485"),
    ("プリセール【3/11（木）～20（土）公演】（東京 R9年 3/11〜3/20公演）〜9/18 23:59", "2626485"),
    ("プリセール【3/21（日）～30（火）公演】（東京 R9年 3/21〜3/30公演）〜9/18 23:59", "2626485"),
    ("プリセール【4/2（金）～10（土）公演】（東京 R9年 4/2〜4/10公演）〜9/18 23:59", "2626487"),
    ("プリセール【4/11（日）～20（火）公演】（東京 R9年 4/11〜4/20公演）〜9/18 23:59", "2626487"),
    ("プリセール【4/21（水）～25（日）公演】（東京 R9年 4/21〜4/25公演）〜9/18 23:59", "2626487"),
]

h = io.open("index.html", encoding="utf-8", newline="").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
events = json.loads(m.group(2))
e = next(x for x in events if x["id"] == 3674)
have = {t.get("type") for t in e.get("tickets") or []}

# 楽天の枠より前（＝ぴあの枠のかたまりの最後）に差し込む
pia = [t for t in e["tickets"] if "pia.jp" in (t.get("url") or "")]
oth = [t for t in e["tickets"] if "pia.jp" not in (t.get("url") or "")]
add = [{"type": ty, "date": "2026-09-18", "url": U % cd} for ty, cd in ROWS if ty not in have]
e["tickets"] = pia + add + oth
e["verifiedAt"] = "2026-09-09"
print("id3674 に プリセール %d枠 を足した（合計 %d枠）" % (len(add), len(e["tickets"])))
for t in add:
    print("   ＋%s" % t["type"])

if "--apply" not in sys.argv:
    print("(--apply で書き込み)")
    sys.exit(0)
out = h[:m.start(2)] + json.dumps(events, ensure_ascii=False, indent=2).replace("\n", "\r\n") + h[m.end(2):]
io.open("index.html", "w", encoding="utf-8", newline="").write(out)
print("書き込み完了")
