# -*- coding: utf-8 -*-
"""e+ /sf/detail/ の販売枠を「券種名＋受付期間＋ステータス」の対で読む（2026-08-07 新設）。
既存 tmp/eplus_detail_0803.py は status を set() で拾うので枠との対応が取れなかった。
"""
import html
import re
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def clean(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def show(label, url):
    h = urllib.request.urlopen(
        urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=60
    ).read().decode("utf-8", "replace")
    print("=" * 74)
    m = re.search(r"<title>(.*?)</title>", h, re.S)
    print("%s\n  title: %s\n  %s" % (label, clean(m.group(1))[:110] if m else "?", url))
    parts = re.split(r'<header class="block-ticket__header"', h)
    for p in parts[1:]:
        seg = p[:6000]
        head = clean(seg.split("</header>")[0])
        sts = [x.strip() for x in re.findall(r"ticket-status__item[^>]*>([^<]{1,30})<", seg)]
        print("   ・%s\n      → 状態: %s" % (head[:150], " / ".join(dict.fromkeys(sts)) or "(取れず)"))


TARGETS = [
    ("id=185 斉藤朱夏 神奈川8/16", "https://eplus.jp/sf/detail/3011010001-P0030079P021001"),
    ("id=717 Damian Hamada 東京8/15", "https://eplus.jp/sf/detail/3616590001-P0030020P021001"),
    ("id=813 時速36km 石川8/15", "https://eplus.jp/sf/detail/3362390001-P0030053P021001"),
    ("id=925 忘れらんねえよ 大阪8/11", "https://eplus.jp/sf/detail/0753900001-P0030160P021001"),
]

for i, (label, url) in enumerate(TARGETS):
    if i:
        time.sleep(5)
    show(label, url)
