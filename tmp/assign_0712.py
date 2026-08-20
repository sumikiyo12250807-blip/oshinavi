# -*- coding: utf-8 -*-
"""7/12 新着100件(2400-2499)を下書き_genre→本ジャンル確定。両方式は_extraGenres→extraGenres。
下書きfield全除去。NEW_ORDER空リセット。再分類しない（[[project_vendor_genre_autoassign]]）。"""
import re, json, datetime, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
E = json.loads(m.group(2))
cnt = collections.Counter()
extras = []
for e in E:
    if 2400 <= e['id'] <= 2499:
        g = e.get('_genre')
        assert g and g != 'new', f"id{e['id']} _genre未設定={g}"
        ex = e.get('_extraGenres')
        e['genre'] = g
        if ex:
            e['extraGenres'] = ex
            extras.append((e['id'], g, ex, (e.get('artist') or '')[:20]))
        for k in ('_genre', '_extraGenres', '_piaSub', '_srcgenre'):
            e.pop(k, None)
        cnt[g] += 1
# NEW_ORDER空
new = re.sub(r'(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]', r'\g<1>[]', h[:m.start()] + m.group(1) + json.dumps(E, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():], count=1)
bak = f'index.html.bak_{datetime.date.today():%m%d}_assign'
open(bak, 'w', encoding='utf-8').write(h)
open('index.html', 'w', encoding='utf-8').write(new)
print('=== 振り分け %d件 / NEW_ORDER空 (backup %s) ===' % (sum(cnt.values()), bak))
print('本ジャンル:', dict(cnt))
print('両方式(extraGenres) %d件:' % len(extras))
for x in extras:
    print('  ', x)
