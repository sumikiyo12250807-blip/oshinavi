# -*- coding: utf-8 -*-
"""7/3 新着50件(1812-1869) ジャンル振り分け(ユーザーOK「振り分けて」2026-07-03)。
下書き_genre/_extraGenres(ぴあカテゴリ由来・_piaSub全件充填で人の再分類不要)をそのまま確定。
バレエ=classic+engeki(1812/1851)。genre確定・extraGenres付与・下書きフィールド除去・NEW_ORDER空・genre:new解消。"""
import re, json, sys, io
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

pool = [e for e in EVENTS if e.get('genre') == 'new']
# 下書き検証: _genre必須・空なら停止(人の判断が要る)
bad = [e['id'] for e in pool if not e.get('_genre')]
assert not bad, '_genre空でreview要: %s' % bad

tally = Counter()
audit = []
for e in pool:
    g = e['_genre']
    extra = e.get('_extraGenres') or []
    e['genre'] = g
    if extra:
        e['extraGenres'] = extra
    audit.append((e['id'], g, extra, (e.get('name') or e.get('artist') or '')[:34]))
    for k in ('_genre', '_extraGenres', '_piaSub'):
        e.pop(k, None)
    tally[g + ('+' + '/'.join(extra) if extra else '')] += 1

# NEW_ORDER 空に
h_new = re.sub(r'(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]', r'\g<1>[]', h, count=1)
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
m2 = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h_new, re.S)
out = h_new[:m2.start()] + m2.group(1) + new_arr + m2.group(3) + h_new[m2.end():]

remaining_new = sum(1 for e in EVENTS if e.get('genre') == 'new')
open('index.html.bak_0703_assign', 'w', encoding='utf-8').write(h)
open('index.html', 'w', encoding='utf-8').write(out)
for a in audit:
    print(f"  id={a[0]} -> {a[1]}{'+'+'/'.join(a[2]) if a[2] else ''} | {a[3]}")
print('振り分け %d件 / genre:new 残 %d件' % (len(pool), remaining_new))
print('内訳:', dict(sorted(tally.items(), key=lambda x: -x[1])))
print('backup: index.html.bak_0703_assign')
