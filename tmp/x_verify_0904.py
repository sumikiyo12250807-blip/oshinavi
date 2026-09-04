# -*- coding: utf-8 -*-
"""X投稿7本のリスト行が、素材（tmp/x_bundles_0904.txt）と一致しているかを機械で照合する。

見るもの：
  ① 投稿にあるのに素材に無い行＝**勝手に足した疑い**（いちばん危ない）
  ② 素材にあるのに投稿に無い行＝**名前を削った疑い**（台本で禁止）
   ※2〜3日後の分は5件に絞る決まりなので、9/5(明日)のぶんだけ厳密に見る。
"""
import re, io, glob

MAT = io.open("tmp/x_bundles_0904.txt", encoding="utf-8").read()
# 素材の「明日発売」ブロックだけを集める
mat_lines = set()
for blk in re.findall(r"■ 9/5\(土\)発売.*?(?=\n■|\n=====|\Z)", MAT, re.S):
    for m in re.finditer(r"^\s*(\d{1,2}:\d{2}) (.+?)／(.+?)(（先行）)?$", blk, re.M):
        mat_lines.add((m.group(1), m.group(2).strip(), m.group(3).strip()))

post_lines = {}
for p in sorted(glob.glob("tmp/x0905/post*.txt")):
    t = io.open(p, encoding="utf-8").read()
    blk = re.search(r"【9/5\(土\)発売】(.*?)(?=\n【|\n\n)", t, re.S)
    if not blk:
        continue
    s = set()
    for m in re.finditer(r"^(\d{1,2}:\d{2}) (.+?)／(.+?)(（先行）)?$", blk.group(1), re.M):
        s.add((m.group(1), m.group(2).strip(), m.group(3).strip()))
    post_lines[p] = s

allpost = set()
for s in post_lines.values():
    allpost |= s

extra = sorted(allpost - mat_lines)
missing = sorted(mat_lines - allpost)

buf = ["X投稿と素材の照合（9/5発売ぶん）", ""]
buf.append("素材の行=%d / 投稿の行=%d" % (len(mat_lines), len(allpost)))
buf.append("")
buf.append("【投稿にあるが素材に無い＝足した疑い】%d件" % len(extra))
for x in extra:
    buf.append("  %s %s／%s" % x)
buf.append("")
buf.append("【素材にあるが投稿に無い＝削った疑い】%d件" % len(missing))
for x in missing:
    buf.append("  %s %s／%s" % x)
buf.append("")
for p, s in post_lines.items():
    buf.append("%s … 9/5の行 %d" % (p, len(s)))
io.open("tmp/x0905/verify.txt", "w", encoding="utf-8").write("\n".join(buf))

print("素材=%d 投稿=%d" % (len(mat_lines), len(allpost)))
print("足した疑い=%d  削った疑い=%d" % (len(extra), len(missing)))
