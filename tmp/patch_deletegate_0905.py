# -*- coding: utf-8 -*-
"""DELETE_GATE.md の「5.」に、状態テキストの確かめ方（道具名）を1行足す。"""
import io
P = 'DELETE_GATE.md'
s = io.open(P, encoding='utf-8', newline='').read()
OLD = '🚨消える前に**statustextで「予定枚数終了」か**を確かめる。売り切れなら消さずに `soldout` を付ける。'
NEW = ('🚨消える前に**「予定枚数終了」か「販売終了」か**を確かめる＝`python tools/pia_statustext.py <eventCd>`\n'
       '（`pia_tickets.py` は両方を"受付終了"に潰すので判別できない）。\n'
       '**売り切れなら消さずに `soldout` を付ける。販売終了なら `saleEnded` も付ける。どちらも消さない。**')
assert OLD in s, 'target not found'
io.open(P, 'w', encoding='utf-8', newline='').write(s.replace(OLD, NEW, 1))
print('PATCHED')
