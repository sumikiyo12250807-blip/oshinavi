# -*- coding: utf-8 -*-
"""新着47件の振り分け（ユーザー「お直し0よ 振り分けOK」2026-07-19）。
下書き _genre / _extraGenres を正式な genre / extraGenres へ移し、下書きフィールドを掃除する。
"""
import re, json, sys, shutil
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')

PATH = 'index.html'
BAK = 'index.html.bak_0719_assign_ok'
shutil.copy(PATH, BAK)
h = open(PATH, encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
E = json.loads(m.group(2))

cnt = Counter()
both = []
for e in E:
    if e.get('genre') != 'new':
        continue
    g = e.get('_genre')
    if not g:
        print(f'[!] id={e["id"]} ジャンル未決 {e.get("name")}')
        continue
    e['genre'] = g
    cnt[g] += 1
    if e.get('_extraGenres'):
        e['extraGenres'] = e.pop('_extraGenres')
        both.append((e['id'], e.get('name'), g, e['extraGenres']))
    for k in ('_genre', '_piaSub', '_srcgenre'):
        e.pop(k, None)

new_arr = json.dumps(E, ensure_ascii=False, indent=2)
new_arr = '\n'.join(('  ' + ln if ln.strip() else ln) for ln in new_arr.split('\n')).lstrip()
h = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]

# 振り分け済みなので新着タブの並び順指定は空にする
mo = re.search(r'(const NEW_ORDER = )(\[[^\]]*\])', h)
h = h[:mo.start()] + mo.group(1) + '[]' + h[mo.end():]

open(PATH, 'w', encoding='utf-8').write(h)

print('振り分け:', dict(cnt), '計', sum(cnt.values()))
for i, n, g, x in both:
    print(f'  両方式: {n} → {g} + {x}')
print('genre:new 残', sum(1 for e in E if e.get('genre') == 'new'))
print('下書き _genre 残', sum(1 for e in E if '_genre' in e))
print('NEW_ORDER クリア済')
print(f'(backup {BAK})')
