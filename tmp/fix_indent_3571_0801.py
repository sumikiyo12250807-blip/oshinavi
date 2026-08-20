# -*- coding: utf-8 -*-
"""id3571 のインデントを既存エントリと同じ（オブジェクト2sp／フィールド4sp）に直す。
投入時に json.dumps(indent=1)+2sp を使ったため 3sp になっていた。"""
import io
import json
import os
import re
import shutil
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

P = r"C:\Users\user\oshinavi\index.html"
BAK = r"C:\Users\user\oshinavi\index.html.bak_0801_indent3571"

raw = open(P, "rb").read()
s = raw.decode("utf-8")
crlf0, lf0 = raw.count(b"\r\n"), raw.count(b"\n")
print("修正前: CRLF %d / 単独LF %d" % (crlf0, lf0 - crlf0))

# 3571 のエントリ範囲を特定（3スペース版）
start = s.find('  {\r\n   "id": 3571,\r\n')
if start < 0:
    print("🚨 3スペース版の3571が見つからない。中止。")
    sys.exit(1)
end = s.find('\r\n  }\r\n];', start)
if end < 0:
    print("🚨 終端が見つからない。中止。")
    sys.exit(1)
end += len('\r\n  }')

block = s[start:end]
ent = json.loads(block.replace("\r\n", "\n"))
assert ent["id"] == 3571, "3571でない"

body = json.dumps(ent, ensure_ascii=False, indent=2)          # フィールド2sp
body = "\n".join("  " + ln for ln in body.split("\n"))        # 全体+2sp → フィールド4sp
body = body.replace("\n", "\r\n")                             # 🚨LF→CRLF

if not os.path.exists(BAK):
    shutil.copyfile(P, BAK)

s = s[:start] + body + s[end:]
out = s.encode("utf-8")
crlf1, lf1 = out.count(b"\r\n"), out.count(b"\n")
assert lf1 - crlf1 == 0, "🚨 単独LFが混入した"
open(P, "wb").write(out)
print("✅ 3571 のインデントを4スペースに統一")
print("修正後: CRLF %d / 単独LF %d" % (crlf1, lf1 - crlf1))
