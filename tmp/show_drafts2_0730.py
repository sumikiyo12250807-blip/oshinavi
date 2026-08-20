# -*- coding: utf-8 -*-
"""投入した新着プールの下書きジャンル＆締切分布をまとめる（報告用）。"""
import collections
import datetime
import json
import re

TODAY = datetime.date.today()
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
news = sorted([e for e in EVENTS if e.get('genre') == 'new'], key=lambda e: e['id'])

lines = [f'genre:new {len(news)}件  (id {news[0]["id"]}..{news[-1]["id"]})']
tally = collections.Counter((e.get('_genre') or '(空)') for e in news)
lines.append('下書き: ' + ' / '.join(f'{k}{v}' for k, v in tally.most_common()))

# 発売開始までの日数（最も早い startDate）と最遅締切
buckets = collections.Counter()
for e in news:
    ts = e.get('tickets') or []
    starts = [t.get('startDate') for t in ts if t.get('startDate')]
    if starts:
        d = (datetime.date.fromisoformat(min(starts)) - TODAY).days
        buckets['4日後以降' if d >= 4 else ('2〜3日後' if d >= 2 else ('明日' if d == 1 else '本日発売'))] += 1
    else:
        buckets['販売中(発売済)'] += 1
lines.append('発売まで: ' + ' / '.join(f'{k}{v}' for k, v in buckets.most_common()))

src = collections.Counter('楽天' if (e.get('links') or {}).get('rakuten') else 'ぴあ' for e in news)
lines.append('ソース: ' + ' / '.join(f'{k}{v}' for k, v in src.most_common()))
lines.append('')
lines.append('id    | _genre     | 枠 | 最遅締切   | 名前')
lines.append('-' * 96)
for e in news:
    ts = e.get('tickets') or []
    last = max((t.get('date') or '') for t in ts) if ts else ''
    lines.append('{:<5} | {:<10} | {:>2} | {:<10} | {}'.format(
        e['id'], e.get('_genre') or '(空)', len(ts), last, (e.get('artist') or '')[:42]))

open('tmp/drafts2_0730.txt', 'w', encoding='utf-8').write('\n'.join(lines))
print('wrote tmp/drafts2_0730.txt')
