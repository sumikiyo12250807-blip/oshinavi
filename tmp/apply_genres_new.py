# -*- coding: utf-8 -*-
"""新着54件(genre:new)を _genre(ぴあカテゴリ基準) で本ジャンルに振り分け。
draft欄(_genre/_extraGenres/_piaSub)を除去、NEW_ORDER空に。"""
import json, io, sys, shutil, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
txt = open('index.html', encoding='utf-8').read()
i = txt.index('const EVENTS = [') + len('const EVENTS = ')
arr, _ = json.JSONDecoder().raw_decode(txt, i)

# 1106 はぴあ「バレエ・ダンス」→ classic+engeki に戻す（ぴあ基準）
override = {1106: ('classic', ['engeki'])}

def ser(e):
    body = json.dumps(e, ensure_ascii=False, indent=2)
    return '\n'.join('  ' + ln for ln in body.split('\n'))

new_txt = txt
applied = 0
import collections
dist = collections.Counter()
for e in arr:
    if e.get('genre') != 'new':
        continue
    old_block = ser(e)
    ne = dict(e)
    g, ex = override.get(e['id'], (e.get('_genre'), e.get('_extraGenres') or []))
    ne['genre'] = g
    # フィールド順を既存に合わせる: genre の位置はそのまま、extraGenres を genre 直後に
    for k in ['_genre', '_extraGenres', '_piaSub']:
        ne.pop(k, None)
    if ex:
        # extraGenres を挿入（genre の直後になるよう dict 再構築）
        rebuilt = {}
        for k, v in ne.items():
            rebuilt[k] = v
            if k == 'genre':
                rebuilt['extraGenres'] = ex
        ne = rebuilt
    new_block = ser(ne)
    assert new_txt.count(old_block) == 1, ('block', e['id'], new_txt.count(old_block))
    new_txt = new_txt.replace(old_block, new_block)
    applied += 1
    dist[g] += 1
    for x in ex: dist['+'+x] += 1

# NEW_ORDER 空に
new_txt, n = re.subn(r'(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]', r'\g<1>[]', new_txt, count=1)
assert n == 1

# 検証
i2 = new_txt.index('const EVENTS = [') + len('const EVENTS = ')
arr2, _ = json.JSONDecoder().raw_decode(new_txt, i2)
assert sum(1 for e in arr2 if e.get('genre') == 'new') == 0

shutil.copy('index.html', 'index.html.bak_0621_assign_new')
open('index.html', 'w', encoding='utf-8').write(new_txt)
print('振り分け適用', applied, '件 / 新着プール空に')
print('内訳:', dict(dist))
