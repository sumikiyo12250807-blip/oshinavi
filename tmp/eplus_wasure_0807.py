# -*- coding: utf-8 -*-
"""925 忘れらんねえよ：3公演ページを全部開いて日付・会場・券種状態を確定する。"""
import html
import re
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

URLS = [
    "https://eplus.jp/sf/detail/0753900001-P0030159P021001",
    "https://eplus.jp/sf/detail/0753900001-P0030160P021001",
    "https://eplus.jp/sf/detail/0753900001-P0030161P021001",
]


def clean(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


for i, u in enumerate(URLS):
    if i:
        time.sleep(5)
    h = urllib.request.urlopen(
        urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=60
    ).read().decode("utf-8", "replace")
    m = re.search(r"<title>(.*?)</title>", h, re.S)
    print("=" * 74)
    print(u)
    print("  title: " + (clean(m.group(1))[:110] if m else "?"))
    mv = re.search(r'"kaijo_name":"([^"]*)"', h)
    print("  会場: " + (mv.group(1) if mv else "?"))
    for p in re.split(r'<header class="block-ticket__header"', h)[1:]:
        seg = p[:6000]
        head = clean(seg.split("</header>")[0])
        sts = [x.strip() for x in re.findall(r"ticket-status__item[^>]*>([^<]{1,30})<", seg)]
        print("   ・%s → %s" % (head[:130], " / ".join(dict.fromkeys(sts)) or "(取れず)"))
