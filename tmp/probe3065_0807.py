# -*- coding: utf-8 -*-
"""3065 のヘッダ行を生バイト表現で見る（置換が0ヒットの原因調べ）。"""
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
b = open(r"C:\Users\user\oshinavi\index.html", "rb").read().decode("utf-8")
i = b.find('"id": 3065')
seg = b[i - 8:i + 340]
print(repr(seg))
print("---")
for ch in seg:
    if ord(ch) > 0x2000 and ch not in "　":
        print("  U+%04X %s" % (ord(ch), ch))
