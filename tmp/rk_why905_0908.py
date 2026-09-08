# -*- coding: utf-8 -*-
"""カードが19枚あるのに「解析不能」になった日向坂46のページを、パーサに実際に通して原因を見る。"""
import io, re, sys
sys.path.insert(0, "tools")
sys.stdout.reconfigure(encoding="utf-8")
import rakuten_harvest as R

U = "https://ticket.rakuten.co.jp/music/rtzp905/"
h = R.fetch(U)
io.open("tmp/rk_905.html", "w", encoding="utf-8").write(h)

o = io.open("tmp/rk_why905_0908.txt", "w", encoding="utf-8")
o.write("URL: %s\nHTML長: %d\n\n" % (U, len(h)))

rec = R.parse_page(U, h)
o.write("name  = %r\n" % rec["name"])
o.write("perfs = %d件\n" % len(rec["perfs"]))
o.write("wins  = %d件\n" % len(rec["windows"]))
o.write("shape = %s\n\n" % rec.get("shape"))

o.write("--- CARD 正規表現のヒット数: %d ---\n" % len(list(R.CARD.finditer(h))))
o.write("--- parse_perfs: %d件 ---\n" % len(R.parse_perfs(h)))
o.write("--- parse_perfs_text: %d件 ---\n" % len(R.parse_perfs_text(h)))
for p in R.parse_perfs(h)[:4]:
    o.write("   %s\n" % p)

# 実際のカードの書き方を見る
o.write("\n--- performance を含むタグの実物（先頭3つ）---\n")
for m in list(re.finditer(r"<div[^>]*performance[^>]*>", h))[:3]:
    o.write("   %s\n" % m.group(0)[:220])

o.write("\n--- column-N の実物（先頭6つ）---\n")
for m in list(re.finditer(r"<div[^>]*column-\d[^>]*>", h))[:6]:
    o.write("   %s\n" % m.group(0)[:160])
o.close()
print("wrote tmp/rk_why905_0908.txt  perfs=%d cards=%d" % (len(rec["perfs"]), len(list(R.CARD.finditer(h)))))
