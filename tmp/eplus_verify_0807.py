# -*- coding: utf-8 -*-
"""e+候補を /sf/detail/ で1件ずつ開き、公演日・券種・ステータスを確定する（2026-08-07）。
一覧のラベルは券種名であって販売中ではない（feedback_delete_nonpia_blindspot）。"""
import html
import io
import re
import sys
import time
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

TARGETS = [
    (3877, "androp 東京10/31", "https://eplus.jp/sf/detail/3285650002-P0030012P021001"),
    (3878, "海援隊 長野12/19", "https://eplus.jp/sf/detail/4577280001-P0030001P021001"),
    (3879, "カキンツハルカ 東京R9年1/13-14", "https://eplus.jp/sf/detail/4181730001-P0030004P021001"),
    (3880, "語りのバンドマン 大阪11/7", "https://eplus.jp/sf/detail/4192180001-P0030003P021001"),
    (3885, "TenTwenty 東京10/20", "https://eplus.jp/sf/detail/3156680001-P0030072P021001"),
    (3886, "トンボコープ 宮城9/27", "https://eplus.jp/sf/detail/4037240001-P0030022P021001"),
    (3889, "Maverick Mom 東京10/6", "https://eplus.jp/sf/detail/4346090001-P0030002P021001"),
    (3898, "有頂天 東京10/22", "https://eplus.jp/sf/detail/4582530001-P0030001P021001"),
    (3899, "MISIA 宮城8/28", "https://eplus.jp/sf/detail/0006410001-P0030524P021001"),
    (3909, "劇団わらび座 大阪12/6", "https://eplus.jp/sf/detail/4571480001-P0030001P021001"),
    (3914, "大河ドラマ豊臣兄弟 東京11/7", "https://eplus.jp/sf/detail/4583250001-P0030001P021001"),
    (3926, "ジャパンビアフェス 神奈川9/12", "https://eplus.jp/sf/detail/4576960001-P0030001P021001"),
    (3926, "ジャパンビアフェス 神奈川9/13", "https://eplus.jp/sf/detail/4576960001-P0030001P021004"),
]


def clean(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


for i, (eid, label, u) in enumerate(TARGETS):
    if i:
        time.sleep(5)
    try:
        h = urllib.request.urlopen(
            urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=60
        ).read().decode("utf-8", "replace")
    except Exception as e:
        print("id%d %s → 取得失敗 %s" % (eid, label, e))
        continue
    m = re.search(r"<title>(.*?)</title>", h, re.S)
    print("=" * 76)
    print("id%d %s" % (eid, label))
    print("   title: " + (clean(m.group(1))[:110] if m else "?"))
    for p in re.split(r'<header class="block-ticket__header"', h)[1:]:
        seg = p[:6000]
        head = clean(seg.split("</header>")[0])
        sts = [x.strip() for x in re.findall(r"ticket-status__item[^>]*>([^<]{1,30})<", seg)]
        print("    ・%s → %s" % (head[:140], " / ".join(dict.fromkeys(sts)) or "(取れず)"))
