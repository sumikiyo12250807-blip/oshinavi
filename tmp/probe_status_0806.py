# -*- coding: utf-8 -*-
"""券種カードの status 部分の生HTMLをそのまま出す（正規表現が外れている箇所の特定）。"""
import urllib.request, re, io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
u = sys.argv[1]
req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
h = urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "replace")
for i, m in enumerate(re.finditer(r"ticketSalesCard-2024__status", h), 1):
    s = max(0, m.start() - 120)
    print("--- %d ---" % i)
    print(repr(h[s:m.start() + 420]))
    if i >= 3:
        break
