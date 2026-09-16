# -*- coding: utf-8 -*-
"""総ざらい（完全版）の候補URLを index.html の売り場番号で当てる（2026-09-16 夜）。
名前照合より強い＝「名前が出ないだけで対バン名・まとめ名で登録済み」の罠を外せる。
出すのは「候補の見出し／公演日／eventCd／index.htmlにその番号があるか」。
使い方: python tmp/x0917/cdcheck.py tmp/x0917/audit_posts.txt
"""
import io
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

src = io.open('index.html', encoding='utf-8').read()
txt = io.open(sys.argv[1], encoding='utf-8', errors='replace').read()

head = None
date = None
rows = []
for line in txt.splitlines():
    s = line.strip()
    if s.startswith('● '):
        head = s[2:].split('（')[0].strip()
    elif s.startswith('公演日:'):
        date = s.replace('公演日:', '').split('／')[0].strip()
    elif s.startswith('URL'):
        m = re.search(r'(event(?:Bundle)?Cd)=(b?\d+)', s)
        if m:
            rows.append((head, date, m.group(1), m.group(2)))

miss = 0
for head, date, key, cd in rows:
    inx = ('%s=%s' % (key, cd)) in src
    if not inx:
        miss += 1
    print('%s %-30s %-34s %s=%s' % ('OK ' if inx else '⚠ ', (head or '')[:30], (date or '')[:34], key, cd))
print('\n候補 %d 件／index.html に売り場番号が無い（本当の抜けの疑い） %d 件' % (len(rows), miss))
