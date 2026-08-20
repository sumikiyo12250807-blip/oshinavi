# -*- coding: utf-8 -*-
"""id3510 第39期竜王戦第2局三島対局 前夜祭 を新着プールへ戻す（ユーザー指示 7/31）。
決めたジャンルは下書き _genre/_extraGenres に持たせる（[[feedback_new_pool_ok_before_assign]] 戻し方）。
NEW_ORDER にも同じ件数を入れる。"""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(const\s+EVENTS\s*=\s*)(\[.*?\])(;\s*\n)', h, re.S)
EVENTS = json.loads(m.group(2))
e = next(x for x in EVENTS if x['id'] == 3510)

print('before: genre=%s extraGenres=%s' % (e['genre'], e.get('extraGenres')))
e['_genre'] = e['genre']
e['_extraGenres'] = list(e.get('extraGenres') or [])
e['genre'] = 'new'
e.pop('extraGenres', None)
print('after : genre=%s _genre=%s _extraGenres=%s' % (e['genre'], e['_genre'], e['_extraGenres']))

new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
body = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]
mo = re.search(r'(const\s+NEW_ORDER\s*=\s*)(\[[^\]]*\])', body)
body = body[:mo.start()] + mo.group(1) + '[3510]' + body[mo.end():]

open('index.html.bak_0731_revert3510', 'w', encoding='utf-8').write(h)
open('index.html', 'w', encoding='utf-8').write(body)
print('=== 適用 / NEW_ORDER=[3510] ===')
