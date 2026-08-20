# -*- coding: utf-8 -*-
"""3926 ジャパン・ビアフェスティバル横浜2026 の e+ 全券種を確定する（2026-08-07）。
ぴあは「8/19 10:00発売」だけだが e+ は 8/1 から受付中＝今すぐ買える枠がある。"""
import html
import io
import re
import sys
import time
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def clean(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


for n in ["P021001", "P021002", "P021003", "P021004", "P021005", "P021006"]:
    u = "https://eplus.jp/sf/detail/4576960001-P0030001%s" % n
    try:
        h = urllib.request.urlopen(
            urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=60
        ).read().decode("utf-8", "replace")
    except Exception as e:
        print("%s → %s" % (n, e))
        time.sleep(4)
        continue
    m = re.search(r"<title>(.*?)</title>", h, re.S)
    print("=" * 74)
    print("%s  %s" % (n, u))
    print("  title: " + (clean(m.group(1))[:110] if m else "?"))
    for p in re.split(r'<header class="block-ticket__header"', h)[1:]:
        seg = p[:6000]
        head = clean(seg.split("</header>")[0])
        sts = [x.strip() for x in re.findall(r"ticket-status__item[^>]*>([^<]{1,30})<", seg)]
        print("   ・%s → %s" % (head[:150], " / ".join(dict.fromkeys(sts)) or "(取れず)"))
    time.sleep(4)
