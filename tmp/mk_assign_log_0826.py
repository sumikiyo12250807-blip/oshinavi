# -*- coding: utf-8 -*-
"""振り分けログを作る。ユーザーが後から「何をどこへ入れたか」を追えるようにする
（feedback_new_pool_ok_before_assign＝公演名＋ジャンル＋URLをlogsに残す）。"""
import json
import re
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")

ok = json.load(open("tmp/assign_ok_0826.json", encoding="utf-8"))
src = open("index.html", encoding="utf-8").read()
m = re.search(r"const EVENTS = (\[.*?\]);\n", src, re.S)
by_id = {e["id"]: e for e in json.loads(m.group(1))}

rows = [by_id[i] for i in ok if i in by_id]
cnt = Counter(e.get("genre") for e in rows)

out = []
out.append("# 振り分けログ 2026-08-26（夜）")
out.append("")
out.append("新着プール **115件** のうち **%d件** を正式ジャンルへ振り分けた（残り43件）。" % len(rows))
out.append("判定は「ぴあが付けているサブジャンルをそのまま写す」原則（project_vendor_genre_autoassign）。")
out.append("**別エージェントに下書きを見せずゼロから判定させ、一致したものだけ**を適用した。")
out.append("")
out.append("内訳: " + " / ".join("%s %d" % (k, v) for k, v in cnt.most_common()))
out.append("")
out.append("| id | 公演名 | ジャンル | ぴあの区分 | 確認用URL |")
out.append("|---|---|---|---|---|")
for e in sorted(rows, key=lambda x: x["id"]):
    out.append("| %d | %s | %s | %s | %s |" % (
        e["id"], (e.get("artist") or "").replace("|", "／"), e.get("genre"),
        e.get("_piaSub") or "-", (e.get("links") or {}).get("pia") or "-"))

open("logs/assigned_2026-08-26.md", "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
print("logs/assigned_2026-08-26.md に %d件を記録" % len(rows))
print("内訳: " + " / ".join("%s %d" % (k, v) for k, v in cnt.most_common()))
