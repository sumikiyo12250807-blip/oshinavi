# -*- coding: utf-8 -*-
"""id3519 OGRE YOU ASSHOLE の期限切れ枠（オフィシャル先行〜7/31 23:59）を削除。
昨日で受付終了＝載せない（feedback_remove_expired）。並びは NEW_ORDER 固定で動かない。"""
import io
import os
import shutil
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

P = r"C:\Users\user\oshinavi\index.html"
BAK = r"C:\Users\user\oshinavi\index.html.bak_0801_3519_expired"

b = open(P, "rb").read()
crlf0, lf0 = b.count(b"\r\n"), b.count(b"\n")
print("修正前: CRLF %d / 単独LF %d" % (crlf0, lf0 - crlf0))

BLOCK = (
    '      {\r\n'
    '        "type": "オフィシャル先行（北海道・東京・愛知・大阪 9/27〜R9年 1/10公演）〜7/31 23:59",\r\n'
    '        "date": "2026-07-31"\r\n'
    '      },\r\n'
)
o = BLOCK.encode("utf-8")
c = b.count(o)
print("対象ブロックのヒット数: %d" % c)
if c != 1:
    print("🚨 1でないので中止（実物を確認して）")
    sys.exit(1)

if not os.path.exists(BAK):
    shutil.copyfile(P, BAK)
    print("バックアップ: %s" % BAK)

b = b.replace(o, b"")
crlf1, lf1 = b.count(b"\r\n"), b.count(b"\n")
assert lf1 - crlf1 == lf0 - crlf0 == 0, "単独LFが混入した"
assert crlf0 - crlf1 == 4, "消えた行数が4行でない"
open(P, "wb").write(b)
print("✅ 期限切れ枠を削除")
print("修正後: CRLF %d / 単独LF %d" % (crlf1, lf1 - crlf1))
