# -*- coding: utf-8 -*-
"""8/7 追加確認＝①0件だった3件を別キーワードで再検索 ②生きて見えた枠を /sf/detail/ で裏取り。
一覧の「一般発売」は券種名であって販売中ではない（feedback_delete_nonpia_blindspot）。
"""
import io
import subprocess
import sys
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

RESEARCH = [
    (717, "Damian Hamada"),
    (717, "デイミアン"),
    (1456, "木梨憲武"),
    (2988, "ふぉ"),
    (2988, "ふぉ～ゆ～"),
]

DETAILS = [
    (185, "斉藤朱夏 神奈川8/16", "https://eplus.jp/sf/detail/3011010001-P0030079P021001"),
    (813, "時速36km 石川8/15", "https://eplus.jp/sf/detail/3362390001-P0030053P021001"),
    (925, "忘れらんねえよ 大阪8/11", "https://eplus.jp/sf/detail/0753900001-P0030160P021001"),
    (144, "新宿羅生門 東京8/16", "https://eplus.jp/sf/detail/3897440001"),
]

print("########## ① 再検索 ##########")
for i, (eid, kw) in enumerate(RESEARCH):
    if i:
        time.sleep(4)
    r = subprocess.run([sys.executable, "tmp/eplus_search2_0803.py", kw], capture_output=True)
    txt = r.stdout.decode("utf-8", "replace")
    lines = [ln for ln in txt.splitlines() if ln.strip() and not ln.startswith("len=")]
    print("=" * 70)
    print("id=%d 検索語「%s」" % (eid, kw))
    for ln in lines[:14]:
        print("   " + ln)

print("\n########## ② 個別ページ裏取り ##########")
for i, (eid, label, url) in enumerate(DETAILS):
    time.sleep(4)
    r = subprocess.run([sys.executable, "tmp/eplus_detail_0803.py", url], capture_output=True)
    txt = r.stdout.decode("utf-8", "replace")
    print("=" * 70)
    print("id=%d %s\n   %s" % (eid, label, url))
    for ln in txt.splitlines()[:25]:
        print("   " + ln)
