# -*- coding: utf-8 -*-
"""データを足したあとの素材と、予約済みの投稿のリストを比べて「投稿に無い行」を出す（読むだけ）。
使い方: python tmp/x0912/diff_after_fix.py  （先に python tmp/x_posts_material_0912.py で素材を作り直す）"""
import io, re, sys
sys.path.insert(0, 'tmp/x0912')
sys.stdout.reconfigure(encoding='utf-8')
import group_lists as G  # noqa
mat = io.open('tmp/x0912/material.md', encoding='utf-8').read()
secs = re.split(r'\n---\n', mat)
for i, sec in enumerate(secs[1:], 4):
    post = io.open('tmp/x0912/post%02d.txt' % i, encoding='utf-8-sig').read()
    # 9/12 のブロックだけ比べる
    m1 = re.search(r'【9/12\(土\)発売】[^\n]*\n(.*?)\n\n', sec, re.S)
    m2 = re.search(r'【9/12\(土\)発売】\n(.*?)\n\n', post, re.S)
    if not m1 or not m2:
        continue
    A = set()
    for ln in m1.group(1).splitlines():
        m = G.LINE.match(ln.replace('? ', '時刻未定 ', 1) if ln.startswith('? ') else ln)
        if m:
            for p in m.group(3).split('・'):
                A.add((m.group(1), G.ALIAS.get(m.group(2), m.group(2)), p, m.group(4) or ''))
    B = set()
    for ln in m2.group(1).splitlines():
        m = G.LINE.match(ln)
        if m:
            for p in m.group(3).split('・'):
                B.add((m.group(1), G.ALIAS.get(m.group(2), m.group(2)), p, m.group(4) or ''))
    miss = sorted(A - B, key=lambda x: (int(x[0].split(':')[0]) if ':' in x[0] else 99, x[1]))
    print('post%02d 9/12 投稿に無い %d組' % (i, len(miss)))
    for x in miss:
        print('   %s %s／%s%s' % x)
