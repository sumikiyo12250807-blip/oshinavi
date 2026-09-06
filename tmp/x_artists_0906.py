# -*- coding: utf-8 -*-
"""今夜のX投稿に名前を出した公演を、登録側から一覧にする（取りこぼし点検の対象決め）。
🚨ツアーまとめページ(bundle)だけ見ない＝そこに出てこない公演がある（feedback_pia_bundle_hides_shows）。
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

# 投稿の【9/7(月)発売】に名前を出した組（＝いちばん人が飛んでくる分）
NAMES = [
    "log you", "めろめろぱんち", "CHAPTERHOUSE", "chilldspot", "wacci", "古内東子",
    "esq", "山本彩", "LiLi", "WILD BLUE",
    "川村章仁", "仲道郁代", "横山幸雄", "武満徹", "EVAコンサート", "東京シティ・フィル",
    "天満天神繁昌亭", "三遊亭鬼丸", "七代目三遊亭円楽", "桃月庵白酒", "SMAホープ大賞",
    "SHOWMAN", "星の王子さま", "多聞くん",
    "修斗", "東京ヤクルトスワローズ", "STARDOM",
    "おかあさんといっしょ", "DJ OSSHY", "あさうた", "須田亜香里", "吉良花火", "6300系",
    "埼玉西武ライオンズ",
]

h = open("index.html", encoding="utf-8").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))

for n in NAMES:
    hits = [e for e in EVENTS
            if n.lower() in ((e.get("artist") or "") + (e.get("name") or "")).lower()]
    if not hits:
        print("🚨 %-24s 登録に見つからない" % n)
        continue
    for e in hits:
        pia = (e.get("links") or {}).get("pia") or "-"
        print("%-24s id=%-5d 枠%2d  %s" % (n, e["id"], len(e.get("tickets") or []), pia))
