# -*- coding: utf-8 -*-
import re, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

d = json.load(open('tmp/heal_stale.json', encoding='utf-8'))
print('heal_stale.json 要素数:', len(d))
print('先頭itemキー:', list(d[0].keys()))
print()

# index.html から id -> (artist, pia_url) を引くための辞書
src = open('index.html', encoding='utf-8').read()
m = re.search(r'const EVENTS\s*=\s*(\[.*?\]);\s*\n', src, re.S)
data = json.loads(m.group(1))
byid = {e['id']: e for e in data}

from collections import Counter
print('status値の分布:', dict(Counter(x.get('status') for x in d)))
print()

# status が convert 以外（削除候補系）を拾う
zero = [x for x in d if x.get('status') != 'convert']

def show(items, title):
    print(f'=== {title} {len(items)}件 ===')
    for x in items:
        i = x.get('id')
        e = byid.get(i, {})
        art = e.get('artist') or e.get('name') or '(不明)'
        links = e.get('links') or {}
        url = links.get('pia') or links.get('eplus') or ''
        print(f"id={i}: {art} @ {e.get('venue','')} ({e.get('date','')})")
        print(f"   URL: {url}")
    print()

show([x for x in d if x.get('status')=='delete'], '削除候補（heal:買える枠ゼロ）→要reconcile再照合')
show([x for x in d if x.get('status')=='NO_PIA_URL'], 'ぴあURL無し（機械照合不可・目視）')
show([x for x in d if x.get('status')=='WPIA'], 'w.pia直販（削除NG・要目視）')
