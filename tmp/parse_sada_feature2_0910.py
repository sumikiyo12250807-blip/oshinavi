# -*- coding: utf-8 -*-
"""さだまさし特設ページの 10月〜12月の日程と、楽天のリンクがどこに付いているかを見る。"""
import re
import sys

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_perf_status as P

U = 'https://ticket.rakuten.co.jp/features/sada-tour-2026/'
body = P.fetch(U)
txt = re.sub(r'\s+', ' ', P.strip_tags(body))

for kw in ['10月公演 日程', '11月公演 日程', '12月公演 日程']:
    i = txt.find(kw)
    print('===== %s @%d' % (kw, i))
    if i >= 0:
        print(txt[i:i + 1500])
    print()

print('===== リンクの周り =====')
for m in re.finditer(r'https://ticket\.rakuten\.co\.jp/[^\s"\']*?/rt[0-9a-z]{4,8}/', body):
    i = m.start()
    ctx = re.sub(r'\s+', ' ', P.strip_tags(body[max(0, i - 500):i + 200]))
    print('--- %s\n    …%s\n' % (m.group(0), ctx[-420:]))
