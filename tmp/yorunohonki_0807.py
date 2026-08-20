# -*- coding: utf-8 -*-
"""3892 夜の本気ダンス：先行枠の対象県がぴあ実ページで何県なのか生HTMLで確かめる。
登録バッジは15県だがpia_ticketsのregionは6県＝どちらが実態か。"""
import html
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

u = "https://t.pia.jp/pia/event/event.do?eventBundleCd=b2669055"
h = urllib.request.urlopen(
    urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=60
).read().decode("utf-8", "replace")
print("len=%d" % len(h))


def clean(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


# 券種カードを丸ごと出す（先行の対象県が全部書いてあるか見る）
cards = re.findall(r'<li class="[^"]*eventList[^"]*".*?</li>', h, re.S)
if not cards:
    cards = re.split(r'(?=<li[^>]*class="[^"]*item)', h)
print("カード候補 %d" % len(cards))
for c in cards:
    t = clean(c)
    if "先行" in t or "一般発売" in t:
        print("-" * 70)
        print(t[:600])
