# -*- coding: utf-8 -*-
"""x_posts_0910.md を1本ずつのファイルに割る（クリップボードで貼るため）。
出力＝tmp/xp0910/01.txt … 10.txt（本文だけ・前後の見出しや区切りは入れない）"""
import io, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')

src = io.open('tmp/x_posts_0910.md', encoding='utf-8').read()
os.makedirs('tmp/xp0910', exist_ok=True)

# 「## N本目 …」から次の「---」までが1本
blocks = re.split(r'^## (\d+)本目 ([^\n]*)\n', src, flags=re.M)
# blocks = [前置き, 番号, 見出し, 中身, 番号, 見出し, 中身, ...]
n = 0
for i in range(1, len(blocks), 3):
    num, head, body = blocks[i], blocks[i + 1], blocks[i + 2]
    body = body.split('\n---\n')[0]
    body = body.strip('\n')
    p = 'tmp/xp0910/%02d.txt' % int(num)
    io.open(p, 'w', encoding='utf-8', newline='\n').write(body)
    n += 1
    print('%s  %-46s %d字' % (p, head[:46], len(body)))
print('計 %d本' % n)
