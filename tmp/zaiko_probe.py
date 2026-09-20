# -*- coding: utf-8 -*-
"""ZAIKO（zaiko.io）のカテゴリ一覧の中身を割る。
Inertia.js（Laravel+Vue）なので `<div id="app" data-page="{...JSON...}">` に
**ページのデータが全部入っている**はず。そこを取り出して構造を書き出す。
"""
import html as H
import io
import json
import re
import sys

src = sys.argv[1] if len(sys.argv) > 1 else 'tmp/zaiko_cat_concerts.html'
h = io.open(src, encoding='utf-8', errors='replace').read()
out = io.open('tmp/zaiko_probe.txt', 'w', encoding='utf-8')

m = re.search(r'data-page="([^"]+)"', h)
if not m:
    out.write('data-page が無い\n')
    out.close()
    print('data-page なし')
    sys.exit(1)

raw = H.unescape(m.group(1))
try:
    d = json.loads(raw)
except Exception as e:
    out.write('JSONとして読めない: %s\n先頭500字:\n%s\n' % (e, raw[:500]))
    out.close()
    print('JSON parse 失敗')
    sys.exit(1)

out.write('=== data-page のトップのキー ===\n%s\n\n' % sorted(d.keys()))
out.write('component = %r / url = %r\n\n' % (d.get('component'), d.get('url')))
props = d.get('props') or {}
out.write('=== props のキー ===\n%s\n\n' % sorted(props.keys()))


def sketch(o, path='', depth=0):
    """入れ物の形を浅く書く。"""
    pad = '  ' * depth
    if isinstance(o, dict):
        out.write('%s%s {} キー=%s\n' % (pad, path or 'root', sorted(o.keys())[:20]))
        if depth < 2:
            for k in list(o.keys())[:12]:
                sketch(o[k], k, depth + 1)
    elif isinstance(o, list):
        out.write('%s%s [] %d件\n' % (pad, path, len(o)))
        if o and depth < 3:
            sketch(o[0], path + '[0]', depth + 1)
    else:
        s = repr(o)
        out.write('%s%s = %s\n' % (pad, path, s[:90]))


for k, v in props.items():
    sketch(v, k, 1)

# イベントらしい配列を探して1件だけ全部出す
def find_events(o, path=''):
    hits = []
    if isinstance(o, dict):
        for k, v in o.items():
            hits += find_events(v, '%s.%s' % (path, k))
    elif isinstance(o, list) and o and isinstance(o[0], dict):
        keys = set(o[0].keys())
        if keys & {'title', 'name', 'event_name'} and len(o) > 1:
            hits.append((path, o))
        for i, x in enumerate(o[:1]):
            hits += find_events(x, '%s[%d]' % (path, i))
    return hits


for path, arr in find_events(props, 'props')[:3]:
    out.write('\n=== イベントらしい配列 %s（%d件）===\n' % (path, len(arr)))
    out.write('キー: %s\n\n' % sorted(arr[0].keys()))
    out.write(json.dumps(arr[0], ensure_ascii=False, indent=1)[:2500] + '\n')
out.close()
print('wrote tmp/zaiko_probe.txt')
