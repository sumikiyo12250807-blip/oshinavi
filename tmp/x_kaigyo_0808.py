# -*- coding: utf-8 -*-
"""X投稿の本文を「。」で改行する形に直す（2026-08-08・ユーザー指摘）。
ユーザーが毎回手で直していた＝「。」のあとに文が続いていると読みにくい。
段落の空行はそのまま残し、1行の中にある「。＋続き」だけを割る。
"""
import io
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

FILES = [r"C:\Users\user\oshinavi\tmp\x_posts_20260808.txt",
         r"C:\Users\user\oshinavi\tmp\x_posts_20260809_10.txt"]

for f in FILES:
    t = io.open(f, encoding="utf-8").read()
    out = []
    for line in t.split("\n"):
        # 見出し行・URL行・タグ行・署名は触らない
        if line.startswith("===") or "http" in line or line.startswith("#") or not line.strip():
            out.append(line)
            continue
        # 「。」の直後に文字が続くところで割る（行末の。は残す）
        new = re.sub(r"。(?=[^\s])", "。\n", line)
        out.append(new)
    io.open(f, "w", encoding="utf-8", newline="\n").write("\n".join(out))
    print("直した: %s" % f)
