# -*- coding: utf-8 -*-
"""投稿に「他にも◯件あるわ」を戻す（2026-09-13）。

🚨あたしの手落ち＝X_SCRIPT.md の「2〜3日後の発売は5件くらい＋『他にも◯件以上あるわ』」
（丸め方まで 2026-09-09 に決まっている）を読まずに、memory の一行要約
「件数を書かない」だけで判断して**わざわざ消した**。
件数を書かないのは「明日33件発売」のような**全体の実数**の話で、この行は別。

素材（material.md）が各ジャンル・各日について残りの件数をすでに機械で数えているので、
それを投稿の同じ位置へ順番に戻す。
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

mat = io.open('tmp/x0914/material.md', encoding='utf-8').read()
blocks = mat.split('## まとめ枠')[1:]
PLACE = re.compile(r'ほかにもまだあるわ。|ほかにもあるわ。')

for i, blk in enumerate(blocks, 4):
    p = 'tmp/x0914/post%02d.txt' % i
    if not os.path.exists(p):
        continue
    # 素材の「（他にも◯件あるわ）」を日付の順に拾う
    counts = []
    for m in re.finditer(r'【(9/1[3-9])\([^)]*\)発売】(.*?)(?=\n【|\n---|\Z)', blk, re.S):
        mm = re.search(r'（(他にも[^）]*|他にもう[^）]*)）', m.group(2))
        if mm:
            counts.append(mm.group(1) + '。')
    s = io.open(p, encoding='utf-8').read()
    n = len(PLACE.findall(s))
    if n != len(counts):
        print('⚠️ %s ＝ 差し戻す場所 %d個 / 素材の件数 %d個（数が合わないので触らない）'
              % (os.path.basename(p), n, len(counts)))
        continue
    it = iter(counts)
    s2 = PLACE.sub(lambda _m: next(it), s)
    io.open(p, 'w', encoding='utf-8').write(s2)
    print('%s ＝ %d個 戻した：%s' % (os.path.basename(p), n, ' / '.join(counts)))
