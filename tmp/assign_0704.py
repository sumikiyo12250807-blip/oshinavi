# -*- coding: utf-8 -*-
"""7/4 新着プール48件 ジャンル振り分け。下書き_genre→genreに移すだけ(再分類しない・
[[project_vendor_genre_autoassign]])。_extraGenres→extraGenres。下書きフィールド除去。
NEW_ORDER空に。genre:new 0件へ。"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DRY = '--apply' not in sys.argv

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

from collections import Counter
cnt = Counter()
changed = 0
for e in EVENTS:
    if e.get('genre') != 'new':
        continue
    dg = e.get('_genre')
    if not dg:
        print("❌ _genre無し id=", e['id']); continue
    e['genre'] = dg
    ex = e.get('_extraGenres') or []
    if ex:
        e['extraGenres'] = ex
        cnt[dg + '+' + ','.join(ex)] += 1
    else:
        cnt[dg] += 1
    for k in ('_genre', '_piaSub', '_extraGenres'):
        e.pop(k, None)
    changed += 1

print("振り分け", changed, "件:", dict(cnt))
remain = sum(1 for e in EVENTS if e.get('genre') == 'new')
print("genre:new 残:", remain)

# NEW_ORDER 空に
mo = re.search(r'(  const NEW_ORDER = )(\[[^\]]*\])(;)', h)

if DRY:
    print("(DRY)")
else:
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    open('index.html.bak_0704_assign', 'w', encoding='utf-8').write(h)
    h2 = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]
    mo2 = re.search(r'(  const NEW_ORDER = )(\[[^\]]*\])(;)', h2)
    h2 = h2[:mo2.start()] + mo2.group(1) + '[]' + mo2.group(3) + h2[mo2.end():]
    open('index.html', 'w', encoding='utf-8').write(h2)
    print("✅ 振り分け完了 (backup: index.html.bak_0704_assign) / NEW_ORDER空に")
