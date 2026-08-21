# -*- coding: utf-8 -*-
"""新着プールの分裂・表記を直す（2026-08-21・part1検証エージェントの指摘）。

① 4802+4803 女王蜂 ＝ 全国ツアー2026「星」の札幌10/11・名古屋10/23。同一ツアーなので1エントリへ。
② 4797+4798 可憐なアイボリー ＝ 5th Anniversary Live Tour の神戸9/12・東京10/9。同一ツアーなので1エントリへ。
③ 4818「【当日引換券】原田知世」＝ **公演名の頭に券種が混入**している。
   公演名は「原田知世」にして、券種は枠(ticket.type)側で表現する
   （[[feedback_entry_template_standard]]／[[feedback_terminology_batch_split]]）。

※ 4816+4817 DMBQ は公演ごとに共演者が違う別企画なので**統合しない**（統合すると出演者情報が潰れる）。
"""
import io, re, json, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
by = {e['id']: e for e in EVENTS}

def merge(keep, drop, venue, pref, label):
    a, b = by[keep], by[drop]
    for t in b['tickets']:
        t = dict(t)
        t.setdefault('url', (b.get('links') or {}).get('pia'))
        a['tickets'].append(t)
    for t in a['tickets']:
        t.setdefault('url', (a.get('links') or {}).get('pia'))
    a['venue'] = venue
    a['prefecture'] = pref
    a['date'] = max(a['date'], b['date'])
    a['dateLabel'] = label
    a['verifiedAt'] = '2026-08-21'
    print('統合 id=%d ← id=%d ／ 枠%d ／ date=%s' % (keep, drop, len(a['tickets']), a['date']))
    for t in a['tickets']:
        print('    -', t['type'])

merge(4802, 4803, '全国ツアー（Zepp Sapporo／Zepp Nagoya）', '北海道・愛知',
      '2026年10月11日(日)〜2026年10月23日(金) 北海道・愛知')
merge(4797, 4798, '全国ツアー（神戸VARIT.／大手町三井ホール）', '兵庫・東京',
      '2026年9月12日(土)〜2026年10月9日(金) 兵庫・東京')

e = by[4818]
print('\n公演名 %r → %r' % (e['name'], '原田知世'))
e['name'] = '原田知世'
e['artist'] = '原田知世'
for t in e['tickets']:
    if '当日引換券' not in t['type']:
        t['type'] = t['type'].replace('一般発売', '当日引換券販売', 1)
        print('    枠 →', t['type'])
e['verifiedAt'] = '2026-08-21'

DROP = {4803, 4798}
KEEP = [x for x in EVENTS if x['id'] not in DROP]
assert len(KEEP) == len(EVENTS) - 2
shutil.copyfile('index.html', 'index.html.bak_0821_p1fix')
open('index.html', 'w', encoding='utf-8').write(
    h[:m.start()] + m.group(1) + json.dumps(KEEP, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
print('\n=== %d件 → %d件 ===' % (len(EVENTS), len(KEEP)))
