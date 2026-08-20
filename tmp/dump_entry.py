# -*- coding: utf-8 -*-
"""指定idのエントリ要点を UTF-8 のファイルに書き出す（コンソール化けを避ける）。
  python tmp/dump_entry.py 3743 2866
"""
import re, json, sys
ids = [int(x) for x in sys.argv[1:]]
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
byid = {e['id']: e for e in json.loads(m.group(2))}
out = []
for i in ids:
    e = byid.get(i)
    if not e:
        out.append('id%d: 見つからない' % i); continue
    out.append('id%d %s | date=%s' % (i, e['name'], e['date']))
    out.append('  dateLabel: %s' % e.get('dateLabel'))
    out.append('  venue: %s / pref: %s / genre: %s' % (e.get('venue'), e.get('prefecture'), e.get('genre')))
    out.append('  links: ' + json.dumps(e.get('links'), ensure_ascii=False))
    for t in e['tickets']:
        out.append('   - %s | date=%s start=%s soldout=%s saleEnded=%s url=%s'
                   % (t.get('type'), t.get('date'), t.get('startDate'), t.get('soldout'),
                      t.get('saleEnded'), t.get('url') or ''))
    out.append('')
open('tmp/dump_entry_out.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('wrote tmp/dump_entry_out.txt', len(out), 'lines')
