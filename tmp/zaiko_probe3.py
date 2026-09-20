# -*- coding: utf-8 -*-
"""ZAIKOの一覧の中身を割る（正しい取り方）。
Inertia のデータは **`<script data-page="app" type="application/json">` の中身**。
属性値ではない（そこを取り違えて "app" を読んでいた）。
"""
import html as H
import io
import json
import re
import sys

src = sys.argv[1] if len(sys.argv) > 1 else 'tmp/zaiko_cat_concerts.html'
h = io.open(src, encoding='utf-8', errors='replace').read()
out = io.open('tmp/zaiko_probe3.txt', 'w', encoding='utf-8')

m = re.search(r'<script[^>]*data-page="app"[^>]*>(.*?)</script>', h, re.S)
if not m:
    out.write('scriptが見つからない\n')
    out.close()
    print('NG')
    sys.exit(1)
d = json.loads(H.unescape(m.group(1)))
out.write('component = %r\nurl = %r\n\n' % (d.get('component'), d.get('url')))
props = d.get('props') or {}
out.write('=== props のキー ===\n%s\n\n' % sorted(props.keys()))


def find_arrays(o, path='props'):
    hits = []
    if isinstance(o, dict):
        for k, v in o.items():
            hits += find_arrays(v, '%s.%s' % (path, k))
    elif isinstance(o, list) and o and isinstance(o[0], dict):
        hits.append((path, o))
    return hits


arrs = sorted(find_arrays(props), key=lambda x: -len(x[1]))
out.write('=== 辞書の配列（大きい順・上位8）===\n')
for path, arr in arrs[:8]:
    out.write('  %-46s %4d件  キー=%s\n' % (path, len(arr), sorted(arr[0].keys())[:14]))

# イベントらしい配列（title/name と 日付らしいキーを持つもの）を1件まるごと出す
for path, arr in arrs:
    ks = set(arr[0].keys())
    if (ks & {'title', 'name', 'event_name'}) and len(arr) >= 5:
        out.write('\n=== %s（%d件）の1件目 ===\n' % (path, len(arr)))
        out.write(json.dumps(arr[0], ensure_ascii=False, indent=1)[:2600] + '\n')
        out.write('\n=== 同じ配列の title/日付/URLらしい値を10件 ===\n')
        for x in arr[:10]:
            pick = {k: v for k, v in x.items()
                    if re.search(r'title|name|date|time|url|slug|venue|place|status|price', k, re.I)
                    and not isinstance(v, (dict, list))}
            out.write('  %s\n' % json.dumps(pick, ensure_ascii=False)[:300])
        break

# ページ送りの手がかり
out.write('\n=== ページ送り・件数らしいキー ===\n')


def scan_meta(o, path='props'):
    if isinstance(o, dict):
        for k, v in o.items():
            if re.search(r'page|total|count|per_page|next|last|links|meta', k, re.I) \
                    and not isinstance(v, (dict, list)):
                out.write('  %s.%s = %r\n' % (path, k, v))
            scan_meta(v, '%s.%s' % (path, k))
    elif isinstance(o, list):
        for i, v in enumerate(o[:2]):
            scan_meta(v, '%s[%d]' % (path, i))


scan_meta(props)
out.close()
print('wrote tmp/zaiko_probe3.txt')
