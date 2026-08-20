# -*- coding: utf-8 -*-
"""e+ がどのルートなら読めるか当たりを取る（503対策）。"""
import sys, io, time, urllib.request, urllib.parse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
kw = sys.argv[1] if len(sys.argv) > 1 else "Arche"
q = urllib.parse.quote(kw)
urls = [
    "https://eplus.jp/sf/detail/3658480001-P0030044P021001",
    "https://eplus.jp/sf/search?keyword=" + q,
    "https://eplus.jp/sf/search?keyword=" + q + "&block=true",
]
for u in urls:
    try:
        req = urllib.request.Request(u, headers={
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "ja,en;q=0.8",
        })
        h = urllib.request.urlopen(req, timeout=40).read()
        print("OK  len=%6d  %s" % (len(h), u))
    except Exception as e:
        print("NG  %s  %s" % (e, u))
    time.sleep(3)
