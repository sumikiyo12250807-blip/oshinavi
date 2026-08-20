# -*- coding: utf-8 -*-
"""削除候補の確認用URLとリンク構成を出す。ぴあ以外の売り場しか無い子＝機械照合すり抜けの
危険があるので最警戒（feedback_delete_nonpia_blindspot）。"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

IDS = [771, 829, 1249, 1355, 1386, 2142, 2315,
       550, 706, 721, 1068, 1228, 1238, 1306, 1309, 1460, 1465, 1468, 1491,
       1493, 1511, 1550, 1552, 1564, 1592, 1649, 1673, 1685, 2167, 2176,
       2200, 2205, 2214, 2217, 2218, 2219, 2220, 2246]

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
E = {e['id']: e for e in json.loads(m.group(2))}

TODAY = '2026-07-13'
risky, past, future = [], [], []
for i in IDS:
    e = E.get(i)
    if not e:
        print(f'!! id={i} 見つからない'); continue
    links = e.get('links') or {}
    vendors = [k for k in ('pia', 'rakuten', 'eplus', 'lawson') if links.get(k)]
    nonpia = [v for v in vendors if v != 'pia']
    row = (i, e.get('artist', ''), e.get('venue', ''), e.get('date', ''), vendors,
           links.get('pia') or links.get('rakuten') or links.get('eplus') or links.get('official', ''))
    if 'pia' not in vendors:
        risky.append(row)
    elif e.get('date', '') < TODAY:
        past.append(row)
    else:
        future.append(row)

print(f'=== 🚨最警戒: ぴあリンク無し（機械照合が効かない）{len(risky)}件 ===')
for i, a, v, d, ven, u in risky:
    print(f'  id={i} {a} @{v} ({d}) 売り場={ven}\n     {u}')

print(f'\n=== 公演終了済み（{TODAY}より前）{len(past)}件 ===')
for i, a, v, d, ven, u in past:
    print(f'  id={i} {a} @{v} ({d}) 売り場={ven}')

print(f'\n=== 公演は未来・ぴあ0枠 {len(future)}件 ===')
for i, a, v, d, ven, u in future:
    extra = f' +{[x for x in ven if x!="pia"]}' if len(ven) > 1 else ''
    print(f'  id={i} {a} @{v} ({d}){extra}\n     {u}')
