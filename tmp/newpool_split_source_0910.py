# -*- coding: utf-8 -*-
"""新着プールを「ぴあ由来」と「ぴあ以外」に分ける。

ぴあ由来＝エージェント検証を通せば振り分けを自走してよい。
ぴあ以外（e+／楽天／ローチケ）＝**振り分けだけがユーザーの確認後**なので新着タブに残す
（[[feedback_nonpia_user_eyes_until_gate]]／[[feedback_check_on_oshinavi_not_tables]]）。
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
events = json.loads(m.group(2))
pool = [e for e in events if e.get('genre') == 'new']

pia, other, nodraft = [], [], []
for e in pool:
    ls = e.get('links') or {}
    if ls.get('pia'):
        pia.append(e)
    else:
        other.append(e)
    if not e.get('_genre'):
        nodraft.append(e)

print('新着プール %d件 → ぴあ由来 %d件 / ぴあ以外 %d件' % (len(pool), len(pia), len(other)))
print('下書き_genreが無い: %s' % ([e['id'] for e in nodraft] or 'なし'))
print()
print('ぴあ以外のid（振り分けから外す）:')
print(','.join(str(e['id']) for e in sorted(other, key=lambda x: x['id'])))

with open('tmp/newpool_nonpia_0910.txt', 'w', encoding='utf-8') as f:
    f.write('ぴあ以外の新着 %d件（振り分けはユーザーの確認後）\n' % len(other))
    for e in sorted(other, key=lambda x: x['id']):
        ls = e.get('links') or {}
        src = [k for k in ('eplus', 'rakuten', 'lawson') if ls.get(k)]
        f.write('  id=%-5s %-46s %s %s [%s] _genre=%s\n'
                % (e['id'], e['name'][:46], e['date'], e.get('prefecture') or '',
                   '/'.join(src), e.get('_genre')))
