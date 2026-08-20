# -*- coding: utf-8 -*-
"""X投稿8本の機械チェック＝字数・「。」直後の改行・3点セット・URL・重複語。"""
import os
import re
import collections

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'x_posts_0812.txt')
with open(P, 'r', encoding='utf-8') as f:
    raw = f.read()

blocks = re.split(r'^===(.+?)===\s*$', raw, flags=re.M)[1:]
posts = [(blocks[i].strip(), blocks[i + 1]) for i in range(0, len(blocks), 2)]

HEAD = 'OSHINAVIの"本日発売"ピックアップ🎫'
CTA = '▼チケット情報はこちら → https://oshinavi.jp'
SIGN = '推しの"発売日"見逃さない｜OSHINAVI'

ng = 0
for title, body in posts:
    body = re.sub(r'^\[全\d+字\]\s*$', '', body, flags=re.M).strip('\n')
    n = len(body)
    kaigyo = re.findall(r'。(?=[^\s])', body)
    tags = [l for l in body.split('\n') if l.strip().startswith('#')]
    ok_head = body.split('\n')[0] == HEAD
    ok_cta = CTA in body
    ok_sign = SIGN in body
    ok_len = 290 <= n <= 340
    bad = []
    if not ok_head:
        bad.append('冒頭NG')
    if not ok_cta:
        bad.append('CTA NG')
    if not ok_sign:
        bad.append('署名NG')
    if not tags:
        bad.append('タグ無し')
    if kaigyo:
        bad.append('。直後に文字%d箇所' % len(kaigyo))
    if not ok_len:
        bad.append('字数外')
    if body.count('https://') != 1:
        bad.append('URL数%d' % body.count('https://'))
    ng += len(bad)
    print('%-34s %3d字  %s' % (title, n, 'OK' if not bad else ' / '.join(bad)))

# 重複語（本文だけ・テンプレ行を除く）
words = collections.Counter()
for title, body in posts:
    lines = [l for l in body.split('\n')
             if l and not l.startswith(('OSHINAVI', '▼', '推しの', '#', '[全'))]
    seen = set(re.findall(r'[ぁ-んァ-ヶ一-龠]{3,}', '\n'.join(lines)))
    for w in seen:
        words[w] += 1
print('\n-- 2本以上に出た3字以上の語 --')
for w, c in words.most_common():
    if c >= 2:
        print('%s x%d' % (w, c))
print('\nNG合計 %d' % ng)
