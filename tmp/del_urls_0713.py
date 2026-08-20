# -*- coding: utf-8 -*-
"""削除候補の確認URLを index.html の実データからそのまま出す（links.pia + 各ticket.url）。
※URLは絶対に手で書かない・ここの出力をそのまま貼る。"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

IDS = [771, 829, 1249, 1355, 1386, 2142, 2315,
       550, 706, 721, 1068, 1228, 1238, 1306, 1309, 1460, 1465, 1468, 1491,
       1493, 1511, 1550, 1552, 1564, 1592, 1649, 1673, 1685, 2167, 2176,
       2200, 2205, 2214, 2217, 2218, 2219, 2220, 2246]

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
E = {e['id']: e for e in json.loads(m.group(2))}

for i in IDS:
    e = E.get(i)
    if not e:
        print(f'!! id={i} 見つからない')
        continue
    links = e.get('links') or {}
    urls = []
    for k in ('pia', 'rakuten', 'eplus', 'lawson', 'official'):
        u = links.get(k)
        if u:
            urls.append(f'{k}:{u}')
    for t in e.get('tickets', []):
        u = t.get('url')
        if u and not any(u in x for x in urls):
            urls.append(f'ticket:{u}')
    print(f"id={i} | {e.get('artist','')} | {e.get('venue','')} | {e.get('date','')}")
    for u in urls:
        print(f'    {u}')
