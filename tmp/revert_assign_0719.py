# -*- coding: utf-8 -*-
"""振り分けを取り消して新着プール(genre:"new")に戻す。
ユーザーが新着タブで目視チェックするまで振り分けない運用が正しい
（memory: feedback_new_pool_ok_before_assign）。あたしが朝に自走で振り分けた分の巻き戻し。

ジャンル案は _genre に下書きとして残す（OK後に一発適用できるように）。
"""
import re, json, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')

PATH = 'index.html'
shutil.copy(PATH, 'index.html.bak_0719_revert_assign')

# 振り分け前のバックアップから _piaSub（ぴあカテゴリ由来）を回収
bak = open('index.html.bak_0719_assign', encoding='utf-8').read()
mb = re.search(r'(  const EVENTS = )(\[.*?\])(;)', bak, re.S)
SUB = {e['id']: e.get('_piaSub') for e in json.loads(mb.group(2)) if '_piaSub' in e}

h = open(PATH, encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
E = json.loads(m.group(2))

n = 0
for e in E:
    i = e.get('id') or 0
    if not (2865 <= i <= 2914):
        continue
    e['_genre'] = e.get('genre')          # 決めたジャンルは下書きとして保持
    if e.get('extraGenres'):
        e['_extraGenres'] = e.pop('extraGenres')
    if SUB.get(i) is not None:
        e['_piaSub'] = SUB[i]
    e['genre'] = 'new'                     # 新着タブに戻す
    n += 1

new_arr = json.dumps(E, ensure_ascii=False, indent=2)
new_arr = '\n'.join(('  ' + ln if ln.strip() else ln) for ln in new_arr.split('\n')).lstrip()
open(PATH, 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])

from collections import Counter
print('新着に戻した:', n, '件')
print('下書きジャンル:', dict(Counter(e.get('_genre') for e in E if e.get('genre') == 'new')))
print('genre:new 総数:', sum(1 for e in E if e.get('genre') == 'new'))
