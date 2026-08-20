# -*- coding: utf-8 -*-
"""id3571 HIRAETH を index.html の EVENTS 末尾に投入し、NEW_ORDER にも追加する。
🚨 json.dumps の出力は LF なので、必ず CRLF に直してから差し込む
   （feedback_index_html_crlf_preserve の第2の罠）。"""
import io
import json
import os
import re
import shutil
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

P = r"C:\Users\user\oshinavi\index.html"
BAK = r"C:\Users\user\oshinavi\index.html.bak_0801_add3571"
E = r"C:\Users\user\oshinavi\tmp\entry_2628520.json"

entries = json.load(open(E, encoding="utf-8"))
assert len(entries) == 1 and entries[0]["id"] == 3571, "投入対象が1件でない"
ent = entries[0]

b = open(P, "rb").read()
crlf0, lf0 = b.count(b"\r\n"), b.count(b"\n")
print("投入前: CRLF %d / 単独LF %d / エントリ数 %d" % (
    crlf0, lf0 - crlf0, b.decode("utf-8").count('\n    "id": ')))

if b.count(b'"id": 3571,') or b.count(b"2628520"):
    print("🚨 既に3571か2628520が存在する。中止。")
    sys.exit(1)

if not os.path.exists(BAK):
    shutil.copyfile(P, BAK)
    print("バックアップ: %s" % BAK)

# --- エントリ本体を既存の字下げ（オブジェクト2sp／フィールド4sp）に合わせて整形 ---
body = json.dumps(ent, ensure_ascii=False, indent=1)
body = "\n".join("  " + ln for ln in body.split("\n"))   # 全体を2スペース下げる
body = body.replace("\n", "\r\n")                        # 🚨LF→CRLF

TAIL = "\r\n  }\r\n];"
NEW = "\r\n  },\r\n" + body + "\r\n];"
if b.count(TAIL.encode("utf-8")) != 1:
    print("🚨 配列終端のヒット数が1でない。中止。")
    sys.exit(1)
b = b.replace(TAIL.encode("utf-8"), NEW.encode("utf-8"))

# --- NEW_ORDER に 3571 を追加（末尾＝投入順を守る） ---
old_no = b", 3570];"
if b.count(old_no) != 1:
    print("🚨 NEW_ORDER 終端のヒット数が1でない。中止。")
    sys.exit(1)
b = b.replace(old_no, b", 3570, 3571];")

crlf1, lf1 = b.count(b"\r\n"), b.count(b"\n")
assert lf1 - crlf1 == 0, "🚨 単独LFが混入した（json.dumpsのLF残り）"
open(P, "wb").write(b)

print("✅ 3571 HIRAETH を投入 / NEW_ORDER に追加")
print("投入後: CRLF %d / 単独LF %d" % (crlf1, lf1 - crlf1))
