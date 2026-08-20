# -*- coding: utf-8 -*-
"""3876 平成中村座 十月大歌舞伎：e+の全公演を総当たりして「買える公演」が1つでもあるか確定する。
ぴあは全券種 受付終了。e+一覧の「一般発売」は券種名なので、個別ページのステータスで判定する。
"""
import html
import io
import re
import sys
import time
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def clean(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


alive, dead, miss = [], [], 0
for n in range(1, 45):
    u = "https://eplus.jp/sf/detail/0649000001-P0030031P0210%02d" % n
    try:
        h = urllib.request.urlopen(
            urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=60
        ).read().decode("utf-8", "replace")
    except Exception:
        miss += 1
        time.sleep(2)
        continue
    m = re.search(r"<title>(.*?)</title>", h, re.S)
    title = clean(m.group(1)) if m else "?"
    d = re.search(r"\((\d{4}/\d{1,2}/\d{1,2})", title)
    day = d.group(1) if d else "?"
    got = []
    for p in re.split(r'<header class="block-ticket__header"', h)[1:]:
        seg = p[:6000]
        head = clean(seg.split("</header>")[0])
        sts = [x.strip() for x in re.findall(r"ticket-status__item[^>]*>([^<]{1,30})<", seg)]
        st = " / ".join(dict.fromkeys(sts))
        got.append((head[:90], st))
        if "受付中" in st:
            alive.append((day, head[:90], st, u))
    if got and not any("受付中" in g[1] for g in got):
        dead.append((day, got[0][1]))
    print("P0210%02d %s → %s" % (n, day, " ｜ ".join("%s=%s" % g for g in got)[:150]))
    time.sleep(3)

print("\n=== 買える公演 %d件 / 売切・終了 %d件 / ページ無し %d ===" % (len(alive), len(dead), miss))
for a in alive:
    print("  🎉 %s %s (%s)\n     %s" % a)
