# -*- coding: utf-8 -*-
"""e+の実ページの窓（開始/終了/状態）をチケットごとに一覧表示するだけの調査用。"""
import sys, io, json, re
sys.path.insert(0, 'tools')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import reconcile_eplus as R
from eplus_harvest import fetch, parse_ld

IDS = [int(x) for x in sys.argv[1].split(',')]
evs = R.load()
cache = {}
for e in evs:
    if e['id'] not in IDS:
        continue
    print('\n=== id=%d %s (%s) ===' % (e['id'], e.get('artist', ''), e.get('date', '')))
    for ti, t, u in R.eplus_tickets(e):
        print('  t%d 登録: type=%s | startDate=%s date=%s' % (ti, t.get('type', ''), t.get('startDate'), t.get('date')))
        print('     %s' % u)
        if u not in cache:
            try:
                cache[u] = fetch(u)
            except Exception as ex:
                cache[u] = None
        if not cache[u]:
            print('     FETCH失敗'); continue
        ld = parse_ld(cache[u])
        if ld:
            print('     LD公演: %s %s %s' % (ld[0].get('date'), ld[0].get('pref'), (ld[0].get('name') or '')[:30]))
        for b in R.parse_blocks(cache[u]):
            print('     窓 %-7s %s %s 〜 %s %s | %s' % (b['status'], b['sd'], b.get('st') or '', b['ed'],
                                                       b.get('et') or '', (b.get('name') or '')[:34]))
