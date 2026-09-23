# -*- coding: utf-8 -*-
"""ぴあ受付中(0101)の一覧が、何ページ目から中身を返さなくなるかを数ページだけ調べる。"""
import importlib.util, io, sys, time
sys.argv = ['presale_harvest.py', '01', 'tmp/x0922/_probe.json', 'rlsStatus=0101', 'from=1,to=1']
src = io.open('tools/presale_harvest.py', encoding='utf-8').read()
cut = src.index('items, seen = [], set()')
ns = {'__name__': 'probe'}
exec(compile(src[:cut], 'presale_harvest_head', 'exec'), ns)
sys.stdout.reconfigure(encoding='utf-8')
for p in (1, 60, 100, 120, 140, 150, 160, 161, 200):
    h = ns['fetch'](p)
    pi = ns['parse_page'](h)
    print(p, '件数', len(pi), '位置', ns['page_pos'](h), '先頭', (pi[0]['url'][-12:] if pi else '-'))
    time.sleep(2)
