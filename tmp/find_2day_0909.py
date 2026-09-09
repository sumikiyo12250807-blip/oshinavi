# -*- coding: utf-8 -*-
"""同じ会場で2日間だけのエントリのdateLabelの書き方と、priceの入り方を確かめる。"""
import io, re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
h = io.open('index.html', encoding='utf-8', newline='').read()
evs = json.loads(re.search(r'const EVENTS = (\[.*?\]);\r?\n', h, re.S).group(1))

print('=== 同一会場で「〜」を含むdateLabel（全国ツアー以外）の例 ===')
n = 0
for e in evs:
    dl = e.get('dateLabel') or ''
    if '〜' in dl and 'ツアー' not in dl and '東京ドーム' in (e.get('venue') or '') + dl:
        print('  id%-6d %s | venue=%s' % (e['id'], dl, e.get('venue')))
        n += 1
        if n >= 8:
            break
if n == 0:
    for e in evs:
        dl = e.get('dateLabel') or ''
        if re.match(r'^2026年\d+月\d+日\(.\)〜\d+月\d+日\(.\) ', dl) and 'ツアー' not in dl:
            print('  id%-6d %s | venue=%s' % (e['id'], dl, e.get('venue')))
            n += 1
            if n >= 8:
                break

print('\n=== price が入っているエントリの例 ===')
n = 0
for e in evs:
    if e.get('price'):
        print('  id%-6d price=%r  %s' % (e['id'], e['price'], (e.get('name') or '')[:30]))
        n += 1
        if n >= 6:
            break
print('price入り 合計 %d件' % sum(1 for e in evs if e.get('price')))
