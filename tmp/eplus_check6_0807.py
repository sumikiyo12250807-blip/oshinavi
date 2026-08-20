# -*- coding: utf-8 -*-
"""3065 栄ミナミ音楽祭の残り公演(52〜56)と 144 新宿羅生門の全公演を洗う（2026-08-07）。"""
import html
import re
import subprocess
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def clean(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def dump(u):
    try:
        h = urllib.request.urlopen(
            urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=60
        ).read().decode("utf-8", "replace")
    except Exception as e:
        print("  %s → %s" % (u, e))
        return
    m = re.search(r"<title>(.*?)</title>", h, re.S)
    print("  " + u)
    print("   title: " + (clean(m.group(1))[:110] if m else "?"))
    for p in re.split(r'<header class="block-ticket__header"', h)[1:]:
        seg = p[:6000]
        head = clean(seg.split("</header>")[0])
        sts = [x.strip() for x in re.findall(r"ticket-status__item[^>]*>([^<]{1,30})<", seg)]
        if "受付中" in " ".join(sts) or "予定枚数" in " ".join(sts):
            print("    ・%s → %s" % (head[:130], " / ".join(dict.fromkeys(sts))))


print("### 3065 栄ミナミ音楽祭 残り公演")
for n in ["P0030052", "P0030053", "P0030054", "P0030055", "P0030056"]:
    dump("https://eplus.jp/sf/detail/3658480001-%sP021001" % n)
    time.sleep(4)

print("\n### 144 新宿羅生門 全公演URLを検索から拾う")
r = subprocess.run([sys.executable, "tmp/eplus_search2_0803.py", "新宿羅生門"], capture_output=True)
txt = r.stdout.decode("utf-8", "replace")
urls = []
for m in re.findall(r"https://eplus\.jp/sf/detail/3897440001-[0-9A-Za-z\-]+", txt):
    if m not in urls:
        urls.append(m)
print("  検索から %d件" % len(urls))
for u in urls:
    time.sleep(4)
    dump(u)
