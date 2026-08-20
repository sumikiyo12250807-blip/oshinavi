# -*- coding: utf-8 -*-
"""新着プール取りこぼし修正・第2弾（3523と3539の先行枠を追加）。
第1弾で文字列不一致/複数ヒットにより中止した2件を、一意なアンカーでやり直す。"""
import io
import os
import shutil
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

P = r"C:\Users\user\oshinavi\index.html"
BAK = r"C:\Users\user\oshinavi\index.html.bak_0801_newpool_miss2"

b = open(P, "rb").read()
crlf0, lf0 = b.count(b"\r\n"), b.count(b"\n")
print("修正前: CRLF %d / 単独LF %d" % (crlf0, lf0 - crlf0))
if not os.path.exists(BAK):
    shutil.copyfile(P, BAK)

changes = []


def rep(old, new, label):
    global b
    o, n = old.encode("utf-8"), new.encode("utf-8")
    c = b.count(o)
    if c != 1:
        print("  🚨 %s: ヒット数 %d（1でないので中止）" % (label, c))
        return False
    b = b.replace(o, n)
    changes.append(label)
    return True


# ---- 3523 神戸国際taiko音楽祭2027 ----
rep(
    '        "type": "一般発売（兵庫 R9年 1/31公演）8/29 10:00発売",\r\n',
    '        "type": "先行（兵庫 R9年 1/31公演）〜8/12 11:00",\r\n'
    '        "date": "2026-08-12"\r\n'
    '      },\r\n'
    '      {\r\n'
    '        "type": "一般発売（兵庫 R9年 1/31公演）8/29 10:00発売",\r\n',
    "3523 先行枠を追加",
)

# ---- 3539 関取花（amazonリンクで一意化してから tickets 先頭に挿入）----
SEKI = "%E9%96%A2%E5%8F%96%E8%8A%B1"  # URLエンコードされた「関取花」
anchor = (
    '      "amazon": "https://www.amazon.co.jp/s?k=' + SEKI + '%20CD'
    '&i=specialty-aps&srs=26200021051&tag=oshinavi0a-22"\r\n'
    '    },\r\n'
    '    "tickets": [\r\n'
    '      {\r\n'
)
rep(
    anchor,
    anchor.replace(
        '    "tickets": [\r\n      {\r\n',
        '    "tickets": [\r\n'
        '      {\r\n'
        '        "type": "先行（宮城・東京・新潟・愛知・大阪・広島・香川・愛媛・福岡 10/10〜12/27公演）〜8/5 23:59",\r\n'
        '        "date": "2026-08-05"\r\n'
        '      },\r\n'
        '      {\r\n',
    ),
    "3539 先行枠を追加",
)

crlf1, lf1 = b.count(b"\r\n"), b.count(b"\n")
assert lf1 - crlf1 == lf0 - crlf0 == 0, "単独LFが混入した"
open(P, "wb").write(b)

print("\n適用 %d件:" % len(changes))
for c in changes:
    print("  ✅ %s" % c)
print("修正後: CRLF %d / 単独LF %d" % (crlf1, lf1 - crlf1))
