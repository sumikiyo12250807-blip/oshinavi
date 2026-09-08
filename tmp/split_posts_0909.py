# -*- coding: utf-8 -*-
"""下書き12本を1本ずつのファイルに割る。
🚨本文は type で打たずクリップボード経由で貼る（feedback_x_browser_operation 2026-09-05）。
   type だと文字が分解されて壊れた実績がある。"""
import io, os, re

s = io.open("tmp/x_drafts_0909.md", encoding="utf-8").read()
posts = re.findall(r"```(?:text)?\n(.*?)\n```", s, re.S)
os.makedirs("tmp/posts0909", exist_ok=True)

TIMES = ["20:01", "20:06", "20:11", "20:16", "20:21", "20:26",
         "20:31", "20:36", "20:41", "20:46", "20:51", "20:56"]
NAMES = ["ポムポムプリン", "モーニング娘。’26", "矢野顕子", "宇都宮隆", "JPOP",
         "クラシック", "スポーツ", "お笑い", "演歌", "演劇", "伝統芸能", "展覧会"]

for i, p in enumerate(posts):
    io.open("tmp/posts0909/%02d.txt" % (i + 1), "w", encoding="utf-8").write(p)

o = io.open("tmp/posts0909/_plan.md", "w", encoding="utf-8")
o.write("# 予約の並び（%d本・5分おき）\n\n" % len(posts))
o.write("🚨本数が多い日は間隔を詰める（feedback_x_schedule_interval 2026-09-05）\n\n")
o.write("| # | 時刻 | 中身 | 字数 | 動画 |\n|---|---|---|---|---|\n")
for i, p in enumerate(posts):
    o.write("| %02d | %s | %s | %d | %s |\n"
            % (i + 1, TIMES[i], NAMES[i], len(p), "🎬" if i == 4 else ""))
o.close()
print("%d本を tmp/posts0909/ に割った" % len(posts))
