# -*- coding: utf-8 -*-
"""id=2316 UNCHAIN を、ぴあ実ページから再構築した内容（tmp/built_unchain_0819.json）で更新する。
削除候補に出ていたが、同じ30周年企画の後続公演（9/6・10/1・11/8・11/29）に生きた枠が6つあった。
genre は既存のまま（新着に戻さない）。tickets / date / dateLabel / venue / prefecture / links.pia を差し替える。
"""
import json, re, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')

built = {o['id']: o for o in json.load(open('tmp/built_unchain_0819.json', encoding='utf-8'))}
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

FIELDS = ('date', 'dateLabel', 'venue', 'prefecture', 'tickets', 'verified', 'verifiedAt')
n = 0
for e in EVENTS:
    b = built.get(e['id'])
    if not b:
        continue
    print('=== id=%d %s' % (e['id'], e['name']))
    print('  before genre=%s date=%s 枠=%d' % (e.get('genre'), e.get('date'), len(e.get('tickets') or [])))
    for k in FIELDS:
        if k in b:
            e[k] = b[k]
    links = e.get('links') or {}
    links['pia'] = b['links']['pia']
    e['links'] = links
    print('  after  genre=%s date=%s 枠=%d' % (e.get('genre'), e.get('date'), len(e.get('tickets') or [])))
    for t in e['tickets']:
        print('    -', t['type'], t['date'])
    n += 1

if n:
    shutil.copyfile('index.html', 'index.html.bak_0819_unchain')
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    open('index.html', 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print('=== %d件 更新 ===' % n)
