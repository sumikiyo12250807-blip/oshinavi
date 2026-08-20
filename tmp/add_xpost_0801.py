# -*- coding: utf-8 -*-
"""X紹介済みエントリに "xPost" 印を入れる。
index.html はバイナリで読み、該当 "id": N, の直後に1行だけ挿入する
（EVENTS全体を json.dumps で作り直さない＝CRLFを壊さない）。
[[feedback_index_html_crlf_preserve]]"""
import io
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PATH = r"C:\Users\user\oshinavi\index.html"

# 2026-08-01 にXへ投稿した5件
TODAY_X = [3150, 3174, 2544, 2776, 3481]
# 2026-07-31 にXへ投稿した11件
YDAY_X = [1637, 2900, 3191, 2151, 3118, 2153, 2159, 2178, 2185, 2188, 2311]

MARK = {}
for i in TODAY_X:
    MARK[i] = "2026-08-01"
for i in YDAY_X:
    MARK[i] = "2026-07-31"

data = open(PATH, "rb").read()
before_crlf = data.count(b"\r\n")

added, skipped = [], []
for eid, day in sorted(MARK.items()):
    if ('"id": %d,\r\n    "xPost"' % eid).encode("utf-8") in data:
        skipped.append(eid)
        continue
    needle = ('"id": %d,\r\n' % eid).encode("utf-8")
    if data.count(needle) != 1:
        print("!! id=%d が %d 箇所ヒット（スキップ）" % (eid, data.count(needle)))
        skipped.append(eid)
        continue
    ins = ('"id": %d,\r\n    "xPost": "%s",\r\n' % (eid, day)).encode("utf-8")
    data = data.replace(needle, ins, 1)
    added.append(eid)

open(PATH, "wb").write(data)
after_crlf = data.count(b"\r\n")
stray = data.count(b"\n") - after_crlf

print("印を入れた: %d件 %s" % (len(added), added))
print("スキップ  : %d件 %s" % (len(skipped), skipped))
print("CRLF %d → %d (+%d) / stray_LF=%d" % (before_crlf, after_crlf, after_crlf - before_crlf, stray))
