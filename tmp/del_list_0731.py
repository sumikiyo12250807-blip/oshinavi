# -*- coding: utf-8 -*-
"""7/31朝の削除候補リストを index.html から機械抽出してマークダウンで出す。
URLは links.pia / links.eplus / links.rakuten / links.lawson ＋ 各 ticket.url を実データから拾う。"""
import re, json, sys, io

IDS = [192, 362, 606, 871, 928, 962, 1000, 1247, 1297, 1366, 1466, 1494, 1500,
       1884, 2137, 2150, 2225, 2256, 2366, 2670, 2747, 2754, 2838, 2861, 2928,
       3001, 3010]

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
E = {e['id']: e for e in json.loads(m.group(2))}

out = io.open('tmp/del_list_0731.md', 'w', encoding='utf-8')
for i in IDS:
    e = E.get(i)
    if not e:
        out.write('- id=%d 見つからない\n' % i); continue
    urls = []
    for k in ('pia', 'eplus', 'rakuten', 'lawson'):
        u = (e.get('links') or {}).get(k)
        if u and u not in urls:
            urls.append((k, u))
    for t in e.get('tickets', []):
        u = t.get('url')
        if u and all(u != x[1] for x in urls):
            urls.append(('ticket', u))
    lab = {'pia': 'ぴあ', 'eplus': 'e+', 'rakuten': '楽天', 'lawson': 'ローチケ', 'ticket': '券種'}
    links = ' / '.join('[%s](%s)' % (lab[k], u) for k, u in urls) or '(URL無し)'
    out.write('- **%s**（%s・%s） %s\n' % (e.get('name'), e.get('venue') or '', e.get('date'), links))
out.close()
print('wrote tmp/del_list_0731.md  %d件' % len(IDS))
