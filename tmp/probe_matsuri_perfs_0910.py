# -*- coding: utf-8 -*-
"""MATSURI(rtax088) の公演カードを機械で並べて、重複の正体を見る。"""
import sys

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_harvest as RH

U = 'https://ticket.rakuten.co.jp/music/rtax088/'
rec = RH.parse_page(U, RH.fetch(U))
print('shape=%s  perfs=%d  windows=%d' % (rec['shape'], len(rec['perfs']), len(rec['windows'])))
for w in rec['windows']:
    print('  WIN type=%r timming=%r' % (w.get('type'), w.get('timming')))
for p in rec['perfs']:
    print('  P %s end=%r time=%r pref=%r venue=%r sale_end=%r tn=%r st=%r'
          % (p['date'], p.get('end'), p.get('time'), p.get('pref'), p.get('venue'),
             p.get('sale_end'), (p.get('ticket_name') or '')[:26], p.get('status')))
