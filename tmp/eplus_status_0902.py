# -*- coding: utf-8 -*-
"""e+の個別-P頁から「販売状態の生の文言」を拾う（引数=URL）。
予定枚数終了（＝消さない）と受付終了（＝販売終了）を打ち分けるために使う。
parse_blocks は open/before/ended しか返さないので、ここは生HTMLの文字を読む。"""
import re, sys
sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
from eplus_harvest import fetch

u = sys.argv[1]
html = fetch(u)
print(u)
words = ['予定枚数終了', '完売', '受付終了', '販売終了', '受付期間外', '受付前',
         '受付中', '販売中', 'まもなく', 'SOLD OUT', 'soldout']
for w in words:
    n = html.count(w)
    if n:
        print(f'  「{w}」 ×{n}')
# 販売状態らしきクラス/文言のまわりを少し出す
for m in re.finditer(r'(?:status|state|label)[^>]{0,80}>\s*([^<]{2,20})\s*<', html):
    t = m.group(1).strip()
    if any(w in t for w in ('終了', '完売', '受付', '販売', 'SOLD')):
        print('  状態表示:', t)
