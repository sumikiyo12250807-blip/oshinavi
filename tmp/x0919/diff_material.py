# -*- coding: utf-8 -*-
"""作り直した素材と、書いてある投稿のリストを突き合わせて「足りない行」を出す（2026-09-18 夜）。

振り分け（2,032件）とぴあの足し込みのあとで素材が増えたので、post04〜09のリストに
入っていない行が出る。**投稿に無い行＝着地しても見つからない行**なので必ず足す
（[[feedback_existing_entries_miss_new_windows]]の主旨）。

  python tmp/x0919/diff_material.py
"""
import io
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

LINE = re.compile(r'^((?:\d{1,2}:\d{2})|時刻未定|\?) (.+)／([^／]+?)(（先行）)?$')
MAP = {1: 'post04', 2: 'post05', 3: 'post06', 4: 'post07', 5: 'post08', 6: 'post09'}

mat = io.open('tmp/x0919/material.md', encoding='utf-8').read()
blocks = {}
cur = None
day = None
for ln in mat.split('\n'):
    m = re.match(r'## まとめ枠 (\d+)：', ln)
    if m:
        cur = int(m.group(1))
        blocks[cur] = {}
        continue
    m = re.match(r'【(\d+/\d+)\([日月火水木金土]\)発売】', ln)
    if m:
        day = m.group(1)
        if cur:
            blocks[cur][day] = []
        continue
    if cur and day and LINE.match(ln):
        blocks[cur][day].append(ln)

out = io.open('tmp/x0919/diff_material.txt', 'w', encoding='utf-8')
total = 0
for gi, days in sorted(blocks.items()):
    f = 'tmp/x0919/%s.txt' % MAP[gi]
    post = io.open(f, encoding='utf-8').read()
    have = {ln for ln in post.split('\n') if LINE.match(ln)}
    for d, rows in days.items():
        miss = [r for r in rows if r not in have]
        if not miss:
            continue
        total += len(miss)
        out.write('%s 【%s発売】に足りない %d行\n' % (MAP[gi], d, len(miss)))
        for r in miss:
            out.write('    %s\n' % r)
        out.write('\n')
out.write('=== 足りない行 %d ===\n' % total)
out.close()
print('足りない行 %d → tmp/x0919/diff_material.txt' % total)
