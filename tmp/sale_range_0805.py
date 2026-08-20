# -*- coding: utf-8 -*-
"""指定期間に「発売開始」する枠を持つエントリを一覧する（X投稿の候補出し用・コンパクト表示）。
券種名に「M/D HH:MM発売」が明示された枠だけ採用（[[feedback_sale_start_vs_deadline]]）。
使い方: python tmp/sale_range_0805.py 2026-08-06 2026-08-14
"""
import datetime, json, re, sys, collections

sys.stdout.reconfigure(encoding='utf-8')
d0 = datetime.date(*[int(x) for x in sys.argv[1].split('-')])
d1 = datetime.date(*[int(x) for x in sys.argv[2].split('-')])

h = open('index.html', encoding='utf-8').read()
E = json.loads(re.search(r'const\s+EVENTS\s*=\s*(\[.*?\]);\s*\n', h, re.S).group(1))

rows = []
d = d0
while d <= d1:
    md = '%d/%d' % (d.month, d.day)
    pat = re.compile(re.escape(md) + r'\s*(\d{1,2}:\d{2})\s*(?:発売開始|発売予定|発売|販売開始|受付開始)')
    iso = d.isoformat()
    for e in E:
        hit = None
        for t in (e.get('tickets') or []):
            if t.get('startDate') == iso and pat.search(t.get('type') or ''):
                m = pat.search(t.get('type'))
                if hit is None or m.group(1) < hit:
                    hit = m.group(1)
        if hit:
            g = e.get('genre')
            if g == 'new':
                g = '_' + (e.get('_genre') or '?')
            rows.append((iso, hit, g, e['id'], e.get('name') or e.get('artist'), e.get('prefecture')))
    d += datetime.timedelta(days=1)

print('=== %s 〜 %s 発売開始 %d件 ===' % (sys.argv[1], sys.argv[2], len(rows)))
print('ジャンル内訳:', dict(collections.Counter(r[2] for r in rows)))
print()
for r in sorted(rows):
    print('%s %s %-8s id=%-5d %s  [%s]' % (r[0][5:], r[1], r[2], r[3], (r[4] or '')[:52], r[5]))
