# -*- coding: utf-8 -*-
"""新着プールの振り分け下ごしらえ。
ぴあカテゴリ由来の `_genre` をそのまま採用するのが原則（[[project_vendor_genre_autoassign]]）。
人の判断が要るのは `_piaSub` が空 or「音楽その他」など＝名前fallbackに倒れた子だけ。
ここでは**適用せず一覧を出すだけ**。
"""
import re, io, json, sys, collections
sys.stdout.reconfigure(encoding='utf-8')

s = io.open('index.html', encoding='utf-8').read()
m = re.search(r'const EVENTS\s*=\s*(\[)', s)
i = m.start(1); d = 0
for j in range(i, len(s)):
    if s[j] == '[': d += 1
    elif s[j] == ']':
        d -= 1
        if d == 0: break
ev = json.loads(s[i:j + 1])
new = sorted([e for e in ev if e.get('genre') == 'new'], key=lambda e: e['id'])

auto, ask = [], []
for e in new:
    g = e.get('_genre')
    sub = e.get('_piaSub') or ''
    if not g:
        ask.append((e, '下書きジャンルが無い'))
    elif not sub or sub in ('音楽その他', 'その他'):
        ask.append((e, '_piaSub=%r＝名前fallback' % sub))
    else:
        auto.append((e, g, sub))

print('=== 自動適用できる %d件 / 人が見る %d件 ===' % (len(auto), len(ask)))
c = collections.Counter(g for _, g, _ in auto)
print('内訳:', ', '.join('%s %d' % kv for kv in c.most_common()))
print()
print('--- ⚠️人が見る枠 ---')
for e, why in ask:
    print('id%-5s %-40s _genre=%-9s %s' % (
        e['id'], (e.get('name') or '')[:38], e.get('_genre'), why))
    print('        %s' % ((e.get('links') or {}).get('pia') or ''))

json.dump({'auto': [{'id': e['id'], 'name': e['name'], 'genre': g, 'sub': sub,
                     'url': (e.get('links') or {}).get('pia'),
                     'extra': e.get('_extraGenres') or []}
                    for e, g, sub in auto],
           'ask': [{'id': e['id'], 'name': e['name'], 'genre': e.get('_genre'),
                    'sub': e.get('_piaSub'), 'why': why,
                    'url': (e.get('links') or {}).get('pia')} for e, why in ask]},
          open('tmp/assign_plan_0825.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('\nwritten tmp/assign_plan_0825.json')
