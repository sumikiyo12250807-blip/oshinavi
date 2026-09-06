# -*- coding: utf-8 -*-
"""e+の「チケットの関連ジャンル」を OSHINAVI の下書きジャンル(_genre)に写す。

🚨 自分で決めない。売り場の区分をそのまま機械で写す
   （[[feedback_genre_pia_asis_and_other]]＝「ぴあの言う通り」をe+にも当てる。
     売り場が**カテゴリとして**「フェス」と言うなら fes ＝名前だけ見て判断する
     [[feedback_fes_definition]] とは軸が違う）。

🚨 罠（2026-09-06に踏んだ）＝エントリは末尾に `"_genre": null` を**すでに持っている**。
   先頭側に行を挿し込むと JSON の重複キーになり、**後ろの null が勝つ**ので効かない。
   json.loads は黙って後勝ちするから、パースして確かめないと気づけない。
   ✅ 既存の `"_genre": null` の行を**書き換える**。

🚨 行ベース。EVENTS配列は作り直さない。
"""
import io
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

PATH = "index.html"
SRC = "tmp/eplus_genre_src_0906.txt"

MAP = {
    "ヴィジュアル系": "rock",
    "ロック･バンド･インディーズ": "rock",
    "J-POP": "jpop",
    "声優ライブ": "seiyuu",
    "フェス": "fes",
    "演歌･民謡": "enka",
    "ミュージカル": "musical",
}

want, skipped = {}, []
for ln in io.open(SRC, encoding="utf-8"):
    m = re.match(r"id=(\d+)\s+.*?\|\s*(.*)$", ln.rstrip("\n"))
    if not m:
        continue
    eid, g = int(m.group(1)), m.group(2).strip()
    sub = g.split(" ")[-1] if g else ""
    if sub in MAP:
        want[eid] = (MAP[sub], g)
    else:
        skipped.append((eid, g))

with io.open(PATH, encoding="utf-8", newline="") as f:
    lines = f.read().split("\n")

cur = None
done = {}
for i, ln in enumerate(lines):
    m = re.match(r'^\s*"id":\s*(\d+),\s*\r?$', ln)
    if m:
        cur = int(m.group(1))
        continue
    if cur in want and cur not in done:
        mg = re.match(r'^(\s*"_genre":\s*)null(,?\s*\r?)$', ln)
        if mg:
            lines[i] = mg.group(1) + '"%s"' % want[cur][0] + mg.group(2)
            done[cur] = want[cur]

with io.open(PATH, "w", encoding="utf-8", newline="") as f:
    f.write("\n".join(lines))

for eid in sorted(done):
    g, raw = done[eid]
    print("id=%-5d %-10s ← e+「%s」" % (eid, g, raw))
print("")
print("下書きジャンルを付けた = %d / 指定 %d" % (len(done), len(want)))
miss = sorted(set(want) - set(done))
if miss:
    print("🚨 当てられなかった id:", miss)
for eid, g in skipped:
    print("⏸ 保留 id=%d （e+の区分が取れなかった: %s）" % (eid, g[:60]))
