# -*- coding: utf-8 -*-
"""X投稿から件数の実数を外す（memory feedback_x_no_counts_oshi_first＝網羅していないので嘘になる）。
🚨原因はあたしの素材（tmp/x_posts_material_*.py）が「（他にも◯件あるわ）」と書いていたこと＝素材側も直す。
"""
import glob
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

n = 0
for p in sorted(glob.glob('tmp/x0914/post*.txt')):
    s = io.open(p, encoding='utf-8').read()
    b = s
    s = re.sub(r'他にも\s*\d+\s*件以上あるわ。', 'ほかにもまだあるわ。', s)
    s = re.sub(r'他にもう\s*\d+\s*件あるわ。', 'ほかにもあるわ。', s)
    s = re.sub(r'他にも\s*\d+\s*件あるわ。', 'ほかにもあるわ。', s)
    if s != b:
        io.open(p, 'w', encoding='utf-8').write(s)
        n += 1
        print('直した:', os.path.basename(p))
print('%d本を直したわ' % n)

# 素材の作り方も直す（次からこの言い方をさせない）
for q in ('tmp/x_posts_material_0913.py', 'tmp/x_posts_material_0914.py'):
    if not os.path.exists(q):
        continue
    s = io.open(q, encoding='utf-8').read()
    b = s
    s = re.sub(r'（他にも%[sd]件以上あるわ）', '（ほかにもあるわ＝件数は書かない）', s)
    s = re.sub(r'（他にも%[sd]件あるわ）', '（ほかにもあるわ＝件数は書かない）', s)
    if s != b:
        io.open(q, 'w', encoding='utf-8').write(s)
        print('素材の道具も直した:', q)
