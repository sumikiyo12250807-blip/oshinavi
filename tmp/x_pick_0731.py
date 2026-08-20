# -*- coding: utf-8 -*-
"""X投稿の玉出し＝7/31に「発売開始」する枠を全部並べる（[[feedback_x_deadline_vs_presale_by_genre]]
＝基本は発売開始を告知・締切告知は基本しない）。
🚨未pushの新着プール(id3470-3517)は**まだ公開サイトに載っていない**ので候補から外す
（oshinavi.jpへ誘導しても無い公演＝嘘になる）。
出力: tmp/x_pick_0731.txt
"""
import io
import json
import re

TARGET = '2026-07-31'
POOL = range(3470, 3518)   # 未pushの新着プール

h = open('index.html', encoding='utf-8').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[.*?\]);\s*\n', h, re.S)
EVENTS = json.loads(m.group(1))

rows = []
for e in EVENTS:
    if e.get('verified') is not True:
        continue
    for t in e.get('tickets') or []:
        if t.get('startDate') != TARGET:
            continue
        rows.append((e, t))

lines = ['%s に発売開始する枠: %d 件（うち未公開プール分は下に分離）' % (TARGET, len(rows)), '']
pub = [(e, t) for e, t in rows if e['id'] not in POOL]
unpub = [(e, t) for e, t in rows if e['id'] in POOL]


def dump(title, items):
    lines.append('=' * 70)
    lines.append('%s : %d件' % (title, len(items)))
    for e, t in sorted(items, key=lambda x: (x[0].get('_genre') or x[0].get('genre') or '', x[0]['id'])):
        lines.append('-' * 70)
        lines.append('id%s [%s] %s' % (e['id'], e.get('_genre') or e.get('genre'), e.get('name')))
        lines.append('  公演   : %s' % e.get('dateLabel'))
        lines.append('  会場   : %s' % e.get('venue'))
        lines.append('  枠     : %s' % t.get('type'))
        lines.append('  締切   : %s' % t.get('date'))
        lk = e.get('links') or {}
        for k in ('pia', 'rakuten', 'eplus', 'lawson', 'official'):
            if lk.get(k):
                lines.append('  %-7s: %s' % (k, lk[k]))
        if t.get('url'):
            lines.append('  枠URL  : %s' % t['url'])


dump('公開済み＝X投稿に使える', pub)
dump('未pushの新着プール＝今は使えない', unpub)

io.open('tmp/x_pick_0731.txt', 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('wrote tmp/x_pick_0731.txt (public=%d unpublished=%d)' % (len(pub), len(unpub)))
