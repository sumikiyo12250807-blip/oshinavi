# -*- coding: utf-8 -*-
"""build_pia_entries.py が作り直した内容を、既存エントリへ id 据え置きで差し替える汎用の当て込み。
genre は既存のまま（新着プールの並び順・id を動かさない＝[[feedback_new_list_order_lock]]）。
使い方: python tmp/apply_built_0819.py tmp/built_xxx.json
"""
import json, re, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')

built = {o['id']: o for o in json.load(open(sys.argv[1], encoding='utf-8'))}
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

FIELDS = ('date', 'dateLabel', 'venue', 'prefecture', 'tickets', 'verified', 'verifiedAt',
          '_genre', '_extraGenres', '_piaSub')
n = 0
for e in EVENTS:
    b = built.get(e['id'])
    if not b:
        continue
    print('=== id=%d %s (genre=%s は据え置き)' % (e['id'], e['name'][:40], e.get('genre')))
    print('  before 枠=%d' % len(e.get('tickets') or []))
    for k in FIELDS:
        if k in b:
            e[k] = b[k]
    links = e.get('links') or {}
    if b.get('links', {}).get('pia'):
        links['pia'] = b['links']['pia']
    e['links'] = links
    print('  after  枠=%d' % len(e['tickets']))
    for t in e['tickets']:
        print('    -', t['type'], t['date'])
    n += 1

if n:
    shutil.copyfile('index.html', 'index.html.bak_0819_applybuilt')
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    open('index.html', 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print('=== %d件 更新 ===' % n)
