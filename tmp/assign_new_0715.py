#!/usr/bin/env python3
"""新着プール(genre:new)を _genre 下書き通りに正式ジャンルへ振り分け。

方針([[project_vendor_genre_autoassign]])＝_genreをそのまま適用・自分で再分類しない。
人の確認が要るのは _piaSub 空/「音楽その他」の名前ベースfallbackだけ→下で警告表示。
"""
import datetime
import json
import re
import sys
sys.path.insert(0, 'tools')
import build_pia_entries  # noqa stdout UTF-8

DRY = '--apply' not in sys.argv

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(const\s+EVENTS\s*=\s*)(\[.*?\])(;\s*\n)', h, re.S)
EVENTS = json.loads(m.group(2))
NEW = [e for e in EVENTS if e.get('genre') == 'new']

from collections import Counter
cnt = Counter()
fallback = []
for e in NEW:
    g = e.get('_genre')
    cnt[g] += 1
    if not e.get('_piaSub'):   # 空=名前ベースfallback→人の目
        fallback.append((e['id'], e.get('name'), g))

print(f'新着 {len(NEW)}件の下書き内訳:')
for g, n in cnt.most_common():
    print(f'   {g}: {n}')
print(f'\n名前ベースfallback（_piaSub空・妥当性を目視）{len(fallback)}件:')
for i, nm, g in fallback:
    print(f'   id={i} → {g} | {nm}')

if DRY:
    print('\n(確認のみ。--apply で適用)')
    sys.exit(0)

# 適用：_genre→genre、_extraGenres→extraGenres、下書きフィールド削除
moved = 0
for e in NEW:
    g = e.get('_genre')
    if not g:
        print(f"⚠️ id={e['id']} は_genre空・スキップ"); continue
    e['genre'] = g
    extra = [x for x in (e.get('_extraGenres') or []) if x]
    if extra:
        e['extraGenres'] = extra
    for k in ('_genre', '_extraGenres', '_piaSub', '_piaCat'):
        e.pop(k, None)
    moved += 1

# NEW_ORDER空に
h2 = h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():]
h2 = re.sub(r'const NEW_ORDER = \[[\d,\s]*\];', 'const NEW_ORDER = [];', h2)

bak = f'index.html.bak_{datetime.date.today():%m%d}_assign'
open(bak, 'w', encoding='utf-8').write(h)
open('index.html', 'w', encoding='utf-8').write(h2)
print(f'\n=== {moved}件 振り分け完了・NEW_ORDER空 (backup: {bak}) ===')
