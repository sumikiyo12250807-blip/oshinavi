# -*- coding: utf-8 -*-
"""投稿の「他にも◯件」の行が、作り直した素材と合っているかを見る（2026-09-18 夜）。

🚨 refresh_lists.py はリストの行だけ入れ替えるので、**「他にも◯件」の行は古いまま残る**。
   9/20・9/21は「大物5件＋他にも◯件」の形なので、件数が増えたのに数字が古いと**嘘になる**。

  python tmp/x0919/check_more.py [--apply]
"""
import io
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
APPLY = '--apply' in sys.argv

DAYHEAD = re.compile(r'^【(\d+/\d+)\([日月火水木金土]\)発売】')
MORE = re.compile(r'^[（(]?他にも.+あるわ[）)]?。?$')
MAP = {1: 'post04', 2: 'post05', 3: 'post06', 4: 'post07', 5: 'post08', 6: 'post09'}

mat = io.open('tmp/x0919/material.md', encoding='utf-8').read()
want, cur, day = {}, None, None
for ln in mat.split('\n'):
    m = re.match(r'## まとめ枠 (\d+)：', ln)
    if m:
        cur, day = int(m.group(1)), None
        continue
    m = DAYHEAD.match(ln)
    if m:
        day = m.group(1)
        continue
    if cur and day and MORE.match(ln.strip()):
        want[(cur, day)] = ln.strip().strip('（）()')

bad = 0
for gi in sorted(MAP):
    path = 'tmp/x0919/%s.txt' % MAP[gi]
    lines = io.open(path, encoding='utf-8').read().split('\n')
    day = None
    for i, ln in enumerate(lines):
        m = DAYHEAD.match(ln)
        if m:
            day = m.group(1)
            continue
        if day and MORE.match(ln.strip()):
            w = want.get((gi, day))
            cur_txt = ln.strip()
            if w and cur_txt.rstrip('。') != w.rstrip('。'):
                bad += 1
                print('%s 【%s】 投稿「%s」 ← 正しくは「%s」' % (MAP[gi], day, cur_txt, w))
                if APPLY:
                    lines[i] = w + '。' if not w.endswith('。') else w
            elif not w:
                bad += 1
                print('%s 【%s】 投稿「%s」 ← 素材には「他にも」の行が無い（残りゼロ）' % (MAP[gi], day, cur_txt))
                if APPLY:
                    lines[i] = None
    if APPLY:
        io.open(path, 'w', encoding='utf-8', newline='').write(
            '\n'.join(l for l in lines if l is not None))

print('\n食い違い %d件%s' % (bad, '（書き込み済み）' if APPLY else '（--apply で直す）'))
