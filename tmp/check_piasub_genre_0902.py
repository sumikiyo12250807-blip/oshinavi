# -*- coding: utf-8 -*-
"""_piaSub（ぴあのサブカテゴリ）と ジャンル下書き(_genre)／確定ジャンル(genre) がズレていないか点検。
2026-08-31 のアークラ大サーカス（_piaSub=イベントその他 なのに genre=engeki）と同じ型を機械で拾う。
出典 feedback_genre_pia_asis_and_other の最終節「定期点検の項目にする」。"""
import re, json, sys
sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
from build_pia_entries import PIA_GENRE_MAP

h = open('index.html', encoding='utf-8').read()
EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
bad_new, bad_live, nomap = [], [], set()
for e in EV:
    sub = e.get('_piaSub')
    if not sub:
        continue
    key = sub.split('/')[-1].strip()     # 「アート/アート」→「アート」
    ent = PIA_GENRE_MAP.get(key) or PIA_GENRE_MAP.get(sub)
    if not ent:
        nomap.add(sub)
        continue
    want = ent[0] if isinstance(ent, (tuple, list)) else ent
    g = e.get('genre')
    cur = e.get('_genre') if g == 'new' else g
    if cur and cur != want:
        row = (e['id'], sub, cur, want, (e.get('artist') or '')[:34])
        (bad_new if g == 'new' else bad_live).append(row)

print(f'=== _piaSub と ジャンルのズレ ===')
print(f'新着プール {len(bad_new)}件 / 掲載中 {len(bad_live)}件 / 対応表に無いサブカテゴリ {len(nomap)}種')
if nomap:
    print('  対応表に無い:', sorted(nomap)[:10])
for title, rows in (('新着プール', bad_new), ('掲載中', bad_live)):
    if not rows:
        continue
    print(f'\n--- {title}')
    for i, sub, cur, want, nm in rows[:60]:
        print(f'  id{i:<5} _piaSub={sub:<14} いま={cur:<10} ぴあ通りなら={want:<10} {nm}')
    if len(rows) > 60:
        print(f'  … 他 {len(rows)-60}件')
