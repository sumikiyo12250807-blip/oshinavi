# -*- coding: utf-8 -*-
"""ぴあの券種個別ページ(ticketInformation.do?rlsCd=)から販売期間まわりの生テキストを出す。"""
import urllib.request, re, io, sys, html as _html

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
url = sys.argv[1]
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
h = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
t = _html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h)))
for kw in ["受付期間", "販売期間", "発売日", "受付中", "発売前", "受付終了", "予定枚数"]:
    for m in re.finditer(kw, t):
        print("[%s] %s" % (kw, t[max(0, m.start() - 60):m.start() + 120].strip()))
