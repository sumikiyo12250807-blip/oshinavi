# -*- coding: utf-8 -*-
"""144 新宿羅生門の券種状態 ＋ 3065 栄ミナミ音楽祭の公演別URLと券種状態（2026-08-07）。"""
import html
import re
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def get(u):
    return urllib.request.urlopen(
        urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=60
    ).read().decode("utf-8", "replace")


def clean(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def dump(u):
    h = get(u)
    m = re.search(r"<title>(.*?)</title>", h, re.S)
    print("  " + u)
    print("   title: " + (clean(m.group(1))[:110] if m else "?"))
    for p in re.split(r'<header class="block-ticket__header"', h)[1:]:
        seg = p[:6000]
        head = clean(seg.split("</header>")[0])
        sts = [x.strip() for x in re.findall(r"ticket-status__item[^>]*>([^<]{1,30})<", seg)]
        print("    ・%s → %s" % (head[:130], " / ".join(dict.fromkeys(sts)) or "(取れず)"))
    return h


for label, top in [("144 舞台「新宿羅生門」", "https://eplus.jp/sf/detail/3897440001"),
                   ("3065 栄ミナミ音楽祭パートナーズライブ", "https://eplus.jp/sf/detail/3658480001")]:
    print("#" * 74)
    print("### " + label)
    h = get(top)
    urls = []
    for m in re.findall(r"/sf/detail/[0-9A-Za-z\-]{14,}", h):
        if m not in urls:
            urls.append(m)
    print("  公演別URL %d件" % len(urls))
    for i, u in enumerate(urls):
        time.sleep(4)
        dump("https://eplus.jp" + u)
    time.sleep(4)
