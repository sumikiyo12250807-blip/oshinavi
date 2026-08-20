# -*- coding: utf-8 -*-
"""新着プール(genre:new)から「載せる価値の無い子」を洗い出す。
 A: 全枠の締切が今日まで＝明日には死ぬ・将来枠なし（[[feedback_presale_first_harvest]]）
 B: 公演日が今日／明日で当日券のみ
ついでに 締切が今日〜3日以内しか無い子も参考表示。"""
import re, json, io, sys, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
TODAY = '2026-07-10'
h = open('index.html', encoding='utf-8').read()
E = json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);', h, re.S).group(1))
news = [e for e in E if e.get('genre') == 'new']
print(f'genre:new {len(news)}件\n')

A, B, C = [], [], []
for e in news:
    ts = e.get('tickets', [])
    if not ts: continue
    ends = [t.get('date') for t in ts if t.get('date')]
    if not ends: continue
    last = max(ends)
    url = (e.get('links') or {}).get('pia', '')
    row = (e['id'], e['artist'][:26], e.get('venue', '')[:22], e.get('date'), last, url)
    if last <= TODAY:
        A.append(row)
    elif e.get('date') and e['date'] <= TODAY:
        B.append(row)
    elif last <= '2026-07-13':
        C.append(row)

def show(title, rows):
    print(f'--- {title} {len(rows)}件 ---')
    for i, a, v, d, last, u in rows:
        print(f'  id={i} {a} @{v} / 公演日 {d} / 最終締切 {last}')
        if u: print(f'     {u}')
    print()

show('🚨A 全枠が今日まで＝明日には死ぬ（載せる価値なし）', A)
show('⚠️B 公演日が今日以前（当日券のみ）', B)
show('参考C 締切が7/13までしかない', C)
print('A_IDS =', [r[0] for r in A])
print('B_IDS =', [r[0] for r in B])
