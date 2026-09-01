# -*- coding: utf-8 -*-
"""救済適用（--ids）の前後で画面に出る枠が減っていないか突合。
比較相手は救済直前のバックアップ index.html.bak_0902_rescue。"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
TODAY = '2026-09-02'
BEFORE = 'index.html.bak_0902_rescue'


def load(p):
    h = open(p, encoding='utf-8').read()
    return json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))


def base_type(ty):
    ty = re.sub(r'〜\s*\d{1,2}/\d{1,2}(?:\s*\d{1,2}:\d{2})?\s*$', '', ty or '')
    ty = re.sub(r'\d{1,2}/\d{1,2}(?:\s*\d{1,2}:\d{2})?\s*発売\s*$', '', ty)
    return ty.strip()


def visible(t):
    if t.get('saleUntilSoldOut') or t.get('soldout'):
        return True
    sd, d = t.get('startDate'), (t.get('date') or '')
    return not ((not sd or sd <= TODAY) and d < TODAY)


def keys(e):
    return {(base_type(t.get('type')), (t.get('url') or '').strip())
            for t in (e.get('tickets') or []) if visible(t)}


old = {e['id']: e for e in load(BEFORE)}
new = {e['id']: e for e in load('index.html')}
print(f'エントリ数 {len(old)} → {len(new)}')
shr = []
for i, e in new.items():
    if i in old:
        lost = keys(old[i]) - keys(e)
        if lost:
            shr.append((i, e.get('artist', ''), sorted(lost)))
print(f'画面に出る枠が減ったエントリ: {len(shr)}件')
for i, n, lost in shr:
    print(f'  🚨 id={i} {n[:30]}')
    for k in lost[:8]:
        print(f'       - {k[0]} {k[1]}')
to = sum(len(keys(e)) for e in old.values())
tn = sum(len(keys(e)) for e in new.values())
print(f'画面に出る枠の総数 {to} → {tn} （差 {tn-to:+d}）')
print('\n--- 救済した11件の枠数')
for i in (2168, 3488, 3491, 4036, 4037, 4044, 4116, 4956, 5155, 5160, 5193):
    print(f'  id{i} {len(keys(old[i]))} → {len(keys(new[i]))}  {new[i].get("artist","")[:26]}')
