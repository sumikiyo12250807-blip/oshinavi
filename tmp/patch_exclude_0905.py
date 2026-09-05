# -*- coding: utf-8 -*-
"""ゲートでFAILした id6979（New Acoustic Camp 2026）を投入から外す。

実ページに「先着一般発売 2026-07-16〜2026-09-18」がまったく同じ文言で2〜3行あり、
ビルドは1本に潰していた（＝券種違いが見えなくなっている）。
文言が同じなので機械では券種を区別できない → **投入しない**で保留にする。
"""
import io
P = 'tmp/apply_batch2_0905.py'
s = io.open(P, encoding='utf-8').read()
OLD = "for i in sorted(built):\n    if i in LINK:\n        continue\n"
NEW = ("EXCLUDE = {6979}   # ゲートA FAIL（同じ文言の券種が実ページに2〜3行・ビルドが1本に潰した）\n"
       "for i in sorted(built):\n    if i in LINK or i in EXCLUDE:\n        continue\n")
assert OLD in s, 'target not found'
io.open(P, 'w', encoding='utf-8', newline='\n').write(s.replace(OLD, NEW, 1))
print('PATCHED')
