# -*- coding: utf-8 -*-
"""3065 栄ミナミ音楽祭 12/1以降の4公演を状態フィルタ無しで全部出す。"""
import html
import re
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def clean(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


for n in ["P0030053", "P0030054", "P0030055", "P0030056"]:
    u = "https://eplus.jp/sf/detail/3658480001-%sP021001" % n
    h = urllib.request.urlopen(
        urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=60
    ).read().decode("utf-8", "replace")
    m = re.search(r"<title>(.*?)</title>", h, re.S)
    print("=" * 70)
    print(u)
    print(" title: " + (clean(m.group(1))[:110] if m else "?"))
    parts = re.split(r'<header class="block-ticket__header"', h)
    print(" 券種ブロック数=%d" % (len(parts) - 1))
    for p in parts[1:]:
        seg = p[:6000]
        head = clean(seg.split("</header>")[0])
        sts = [x.strip() for x in re.findall(r"ticket-status__item[^>]*>([^<]{1,30})<", seg)]
        print("   ・%s → %s" % (head[:130], " / ".join(dict.fromkeys(sts)) or "(取れず)"))
    for t in set(re.findall(r"受付期間[^<]{0,60}", h)):
        print("   受付期間: " + clean(t))
    time.sleep(4)
