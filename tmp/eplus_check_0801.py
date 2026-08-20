# -*- coding: utf-8 -*-
"""e+詳細ページの販売枠を生HTMLから列挙する（結果はASCIIブールで出す）"""
import re
import sys
import urllib.request

url = sys.argv[1]
req = urllib.request.Request(url, headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
})
html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")

ACCEPTING = "受付中"        # 受付中
CLOSED = "受付終了"     # 受付終了
SOLDOUT = "予定枚数終了"  # 予定枚数終了
BEFORE = "受付前"           # 受付前

print("URL:", url)
print("len:", len(html))
print("page_has_ACCEPTING:", ACCEPTING in html)

blocks = re.split(r'<header class="block-ticket__header"', html)[1:]
print("blocks:", len(blocks))
for i, b in enumerate(blocks, 1):
    chunk = b[:4000]
    status = re.findall(r'ticket-status__item[^>]*>\s*([^<]+)', chunk)
    st = [x.strip() for x in status]
    flags = []
    for x in st:
        if ACCEPTING in x:
            flags.append("ACCEPTING")
        elif SOLDOUT in x:
            flags.append("SOLDOUT")
        elif CLOSED in x:
            flags.append("CLOSED")
        elif BEFORE in x:
            flags.append("BEFORE")
        else:
            flags.append("OTHER:" + repr(x))
    print("  block%02d status=%s" % (i, ",".join(flags) if flags else "NONE"))
