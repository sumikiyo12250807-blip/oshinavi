# -*- coding: utf-8 -*-
"""削除後の健全性チェック：件数・改行(CRLF)・並び順ロジックの指紋照合。"""
import re, json, io, sys
sys.stdout.reconfigure(encoding='utf-8')

DEL = [105, 129, 342, 466, 472, 473, 812, 1664, 1887, 2204, 2255, 2309, 2329,
       2532, 2558, 2740, 2848, 3100, 3221, 3227, 3419]

for p in ('index.html', 'index.html.bak_0803_morning_delete'):
    b = io.open(p, 'rb').read()
    crlf = b.count(b'\r\n')
    lf = b.count(b'\n') - crlf
    h = b.decode('utf-8')
    evs = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
    tick = sum(len(e.get('tickets') or []) for e in evs)
    print('%-40s 件数=%d 枠=%d CRLF=%d 単独LF=%d' % (p, len(evs), tick, crlf, lf))
    if p == 'index.html':
        ids = set(e['id'] for e in evs)
        left = [i for i in DEL if i in ids]
        print('  削除漏れ:', left if left else 'なし')
        print('  id重複:', 'あり' if len(ids) != len(evs) else 'なし')

# 並び順ロジックの指紋（sort_guard が見るブロック）を前後で照合
def fp(p):
    h = io.open(p, encoding='utf-8', newline='').read()
    out = []
    for kw in ('saleStartPending', '.sort(', 'NEW_ORDER'):
        out.append(''.join(re.findall(re.escape(kw) + r'.{0,200}', h, re.S)))
    return out

a, c = fp('index.html'), fp('index.html.bak_0803_morning_delete')
print('並び順ロジック指紋 一致:', a == c)
