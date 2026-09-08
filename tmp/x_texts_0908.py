# -*- coding: utf-8 -*-
"""クリック上位と、インプ大なのにクリック0の投稿を全文で並べる（比較用）"""
import csv, io, re, datetime

CSV = "tmp/x_content_0907.csv"
OUT = "tmp/x_texts_0908.md"
TODAY = datetime.date(2026, 9, 8)
MON = {m: i + 1 for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])}

rows = []
with io.open(CSV, encoding="utf-8-sig", newline="") as f:
    for r in csv.DictReader(f):
        d = (r.get("Date") or "").strip()
        m1 = re.search(r"([A-Z][a-z]{2})\s+(\d{1,2}),\s*(\d{4})", d)
        if not m1 or m1.group(1) not in MON:
            continue
        dt = datetime.date(int(m1.group(3)), MON[m1.group(1)], int(m1.group(2)))
        if (TODAY - dt).days < 2:
            continue
        def num(k):
            v = (r.get(k) or "0").replace(",", "").strip()
            try: return int(float(v))
            except Exception: return 0
        rows.append({"date": dt, "text": (r.get("Post text") or "").strip(),
                     "imp": num("Impressions"), "clk": num("URL Clicks"),
                     "rt": num("Reposts"), "like": num("Likes")})

o = io.open(OUT, "w", encoding="utf-8")
o.write("# 実物の文章を並べて見る\n\n## A. クリックが多かった投稿 上位6本（全文）\n\n")
for r in sorted(rows, key=lambda x: -x["clk"])[:6]:
    o.write("### %s ｜ インプ%d ／ クリック**%d** ／ RT%d ／ いいね%d\n\n```\n%s\n```\n\n"
            % (r["date"].strftime("%m/%d"), r["imp"], r["clk"], r["rt"], r["like"], r["text"]))

o.write("\n## B. インプが大きいのにクリック0だった投稿 上位5本（全文）\n\n")
big0 = sorted([r for r in rows if r["clk"] == 0 and r["imp"] >= 1000], key=lambda x: -x["imp"])
for r in big0[:5]:
    o.write("### %s ｜ インプ%d ／ クリック**0** ／ RT%d ／ いいね%d\n\n```\n%s\n```\n\n"
            % (r["date"].strftime("%m/%d"), r["imp"], r["rt"], r["like"], r["text"]))
o.close()
print("wrote", OUT)
