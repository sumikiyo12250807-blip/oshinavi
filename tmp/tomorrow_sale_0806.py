# -*- coding: utf-8 -*-
"""指定日に「発売開始」する枠を持つエントリを抽出する（X投稿の候補出し用）。
採用するのは券種名に「M/D HH:MM発売」が明示されている枠だけ（[[feedback_sale_start_vs_deadline]]）。
締切（〜M/D）は発売開始ではないので拾わない。
使い方: python tmp/tomorrow_sale_0806.py 2026-08-06
"""
import json, re, sys, collections

sys.stdout.reconfigure(encoding='utf-8')
TARGET = sys.argv[1]
y, mo, d = [int(x) for x in TARGET.split('-')]
MD = '%d/%d' % (mo, d)

h = open('index.html', encoding='utf-8').read()
E = json.loads(re.search(r'const\s+EVENTS\s*=\s*(\[.*?\]);\s*\n', h, re.S).group(1))

# 「8/6 12:00発売」「8/6 10:00発売開始」など、時刻付きで発売と明示された枠だけ
pat = re.compile(re.escape(MD) + r'\s*(\d{1,2}:\d{2})\s*(?:発売開始|発売予定|発売|販売開始|受付開始)')

rows = []
for e in E:
    hits = []
    for t in (e.get('tickets') or []):
        if t.get('startDate') != TARGET:
            continue
        m = pat.search(t.get('type') or '')
        if m:
            hits.append((m.group(1), t.get('type')))
    if hits:
        hits.sort()
        rows.append((e, hits))

by_genre = collections.Counter((e.get('genre') or e.get('_genre') or '?') for e, _ in rows)
print('=== %s 発売開始（時刻明示）＝ %d件 ===' % (TARGET, len(rows)))
print('ジャンル内訳:', dict(by_genre))
print()
for e, hits in sorted(rows, key=lambda r: r[1][0][0]):
    g = e.get('genre')
    g = '%s(_%s)' % (g, e.get('_genre')) if g == 'new' else g
    print('id=%-5d %-6s %s' % (e['id'], g, e.get('name')))
    print('        %s / %s' % (e.get('dateLabel') or '', e.get('venue') or ''))
    for tm, ty in hits:
        print('        %s  %s' % (tm, ty))
    for k, v in (e.get('links') or {}).items():
        if v and k in ('pia', 'eplus', 'rakuten', 'lawson', 'official'):
            print('        %s: %s' % (k, v))
    print()
