# -*- coding: utf-8 -*-
"""build_ai_page.py の GENRE_LABEL に gourmet を足す（改行コードを実物に合わせる）。"""
import io
import os
import shutil
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

P = r"C:\Users\user\oshinavi\tools\build_ai_page.py"
raw = open(P, "rb").read()
crlf, lf = raw.count(b"\r\n"), raw.count(b"\n")
NL = "\r\n" if crlf else "\n"
print("build_ai_page.py 改行: CRLF %d / 単独LF %d → NL=%r" % (crlf, lf - crlf, NL))
bak = P + ".bak_0807"
if not os.path.exists(bak):
    shutil.copyfile(P, bak)

t = raw.decode("utf-8")
old = '    "art": "イベントアート", "kaidan": "怪談",' + NL
new = '    "art": "イベントアート", "kaidan": "怪談", "gourmet": "グルメ",' + NL
c = t.count(old)
print("ヒット数 %d" % c)
if c != 1:
    print("🚨 1でないので中止")
    sys.exit(1)
t = t.replace(old, new)
b = t.encode("utf-8")
assert (b.count(b"\n") - b.count(b"\r\n")) == (lf - crlf), "改行が変わった"
open(P, "wb").write(b)
print("✅ build_ai_page.py の GENRE_LABEL に gourmet を追加")
