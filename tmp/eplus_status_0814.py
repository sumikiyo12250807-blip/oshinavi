# -*- coding: utf-8 -*-
"""e+個別ページの券種ステータス文言だけを抜く（予定枚数終了か受付終了かの区別用）。"""
import sys, io, re
sys.path.insert(0, 'tools')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from eplus_harvest import fetch

KW = ['予定枚数終了', '受付は全て終了', '受付終了', '完売', '販売終了', 'キャンセル待ち', '先着']

for u in sys.argv[1:]:
    print('\n=== %s' % u)
    try:
        h = fetch(u)
    except Exception as ex:
        print('  FETCH失敗 %s' % ex)
        continue
    if not h:
        print('  FETCH失敗(空)')
        continue
    txt = re.sub(r'<[^>]+>', ' ', h)
    txt = re.sub(r'\s+', ' ', txt)
    for kw in KW:
        n = txt.count(kw)
        if n:
            i = txt.find(kw)
            print('  %s x%d … %s' % (kw, n, txt[max(0, i - 60):i + 40]))
