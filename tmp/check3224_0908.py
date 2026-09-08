# -*- coding: utf-8 -*-
"""id3224 MATSURI の楽天ページに、登録している「東京 12/2・10/3発売」の枠があるか実物で確かめる。
   🚨WebFetchは楽天の販売状況を誤読する常習犯なので、生HTMLを機械パースする
      （feedback_rakuten_webfetch_soldout）。"""
import sys, io

sys.path.insert(0, "tools")
sys.stdout.reconfigure(encoding="utf-8")
import rakuten_harvest as R

U = "https://ticket.rakuten.co.jp/music/rtax088/"
b = R.fetch(U)
perfs = R.parse_perfs(b)
wins = R.parse_windows(b)

print("公演カード %d件" % len(perfs))
for p in perfs:
    print("  %s %s / %s / 販売 %s 〜 %s"
          % (p.get("date"), p.get("end") or "", p.get("pref"),
             p.get("sale_start"), p.get("sale_end")))
print("販売枠 %d件" % len(wins))
for w in wins:
    print("  %s | %s" % (w.get("name"), w.get("timming")))

body = b if isinstance(b, str) else b.decode("utf-8", "replace")
for kw in ("12/2", "12月2日", "10/3", "10月3日", "Zepp DiverCity", "東京"):
    print("本文に %-14s : %s" % (kw, "ある" if kw in body else "ない"))
io.open("tmp/rakuten_3224.html", "w", encoding="utf-8").write(body)
print("生HTMLを tmp/rakuten_3224.html に置いた（%d文字）" % len(body))
