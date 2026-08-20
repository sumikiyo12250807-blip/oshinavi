# -*- coding: utf-8 -*-
"""ぴあページの券種カードのマークアップを確認する（パーサーが0件になる原因の切り分け）。"""
import urllib.request, re, io, sys, html as _html

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
u = sys.argv[1]
req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
h = urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "replace")
print("len=%d" % len(h))
print("sorry?", "sorry.pia" in h)
for kw in ["ticketSalesList-2024__item", "ticketSalesCard-2024__status",
           "本日発売初日", "予定枚数", "受付中", "発売前"]:
    print("  %-32s %d回" % (kw, h.count(kw)))
m = re.search(r'<li class="ticketSalesList[^"]*"[\s\S]{0,1200}', h)
if m:
    t = _html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(0))))
    print("最初のカード:", t[:400])
