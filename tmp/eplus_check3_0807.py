# -*- coding: utf-8 -*-
"""8/7 三段目の裏取り＝タイトル＋券種ごとのステータスを一緒に出す。
一覧ラベルでも「受付期間だけ」でもなく、券種ブロックの status と対にして読む。
"""
import io
import re
import sys
import time
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

TARGETS = [
    (185, "斉藤朱夏 神奈川8/16", "https://eplus.jp/sf/detail/3011010001-P0030079P021001"),
    (185, "斉藤朱夏 神奈川8/16(2)", "https://eplus.jp/sf/detail/3011010001-P0030079P021002"),
    (717, "Damian Hamada 東京8/15 Veats", "https://eplus.jp/sf/detail/3616590001-P0030020P021001"),
    (813, "時速36km 石川8/15", "https://eplus.jp/sf/detail/3362390001-P0030053P021001"),
    (144, "新宿羅生門 東京", "https://eplus.jp/sf/detail/3897440001"),
]


def txt(s):
    s = re.sub(r"<[^>]+>", " ", s)
    s = s.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return re.sub(r"\s+", " ", s).strip()


for i, (eid, label, url) in enumerate(TARGETS):
    if i:
        time.sleep(5)
    h = urllib.request.urlopen(
        urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=60
    ).read().decode("utf-8", "replace")
    print("=" * 74)
    print("id=%d %s" % (eid, label))
    print("   " + url)
    m = re.search(r"<title>(.*?)</title>", h, re.S)
    print("   title: " + (txt(m.group(1))[:120] if m else "(なし)"))
    for key in ["kogyo_name_1", "kogyo_name_2", "koen_start_datetime", "kaijo_name"]:
        mm = re.search(r'"%s":"([^"]*)"' % key, h)
        if mm:
            print("   %s: %s" % (key, mm.group(1)[:80]))
    # 券種ブロック（受付期間とステータスの対）
    print("   --- 券種ブロック ---")
    for blk in re.findall(r'<li[^>]*class="[^"]*ticket[^"]*"[^>]*>.*?</li>', h, re.S)[:12]:
        t = txt(blk)
        if "受付期間" in t or "予定枚数" in t or "受付" in t:
            print("     " + t[:170])
    # ステータスバッジをまとめて
    st = [txt(x) for x in re.findall(r'<[^>]*class="[^"]*(?:status|state|label)[^"]*"[^>]*>(.*?)<', h, re.S)]
    st = [s for s in st if s]
    print("   ステータス群: " + " / ".join(dict.fromkeys(st))[:200])
