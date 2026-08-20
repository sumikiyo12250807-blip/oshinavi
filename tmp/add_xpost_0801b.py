# -*- coding: utf-8 -*-
"""8/1にX投稿した5件（8/2発売分）に xPost 印を付ける。
並び順ロジックには触らない＝同点決着のデータを足すだけ（feedback_display_order 2026-08-01ブロック）。
index.html はバイナリで読み書きし、挿入行もCRLFで書く＝改行に一切触らない。"""
import io
import os
import shutil
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

P = r"C:\Users\user\oshinavi\index.html"
BAK = r"C:\Users\user\oshinavi\index.html.bak_0801_xpost"
XDATE = "2026-08-01"
IDS = [2525, 2665, 2885, 2425, 2664]

b = open(P, "rb").read()
crlf0, lf0 = b.count(b"\r\n"), b.count(b"\n")
print("修正前: CRLF %d / 単独LF %d / xPost %d件" % (crlf0, lf0 - crlf0, b.count(b'"xPost"')))

if not os.path.exists(BAK):
    shutil.copyfile(P, BAK)
    print("バックアップ: %s" % BAK)

added, skipped = [], []
for i in IDS:
    id_line = ('    "id": %d,\r\n' % i).encode("utf-8")
    pos = b.find(id_line)
    if pos < 0:
        print("  🚨 id=%d の行が見つからない（書式違い）" % i)
        continue
    after = pos + len(id_line)
    # すでに xPost が付いていないか（直後の1行を見る）
    nxt = b[after:after + 40]
    if b'"xPost"' in nxt:
        skipped.append(i)
        continue
    ins = ('    "xPost": "%s",\r\n' % XDATE).encode("utf-8")
    b = b[:after] + ins + b[after:]
    added.append(i)

crlf1, lf1 = b.count(b"\r\n"), b.count(b"\n")
# 追加した行数ぶんだけCRLFが増え、単独LFは0のままであること
assert lf1 - crlf1 == lf0 - crlf0 == 0, "単独LFが混入した"
assert crlf1 - crlf0 == len(added), "CRLFの増分が追加行数と一致しない"

open(P, "wb").write(b)

print("付与 %d件: %s" % (len(added), added))
if skipped:
    print("既に印あり %d件: %s" % (len(skipped), skipped))
print("修正後: CRLF %d / 単独LF %d / xPost %d件" % (crlf1, lf1 - crlf1, b.count(b'"xPost"')))
