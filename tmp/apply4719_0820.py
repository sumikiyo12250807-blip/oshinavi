# -*- coding: utf-8 -*-
"""4719 ウィーン・ヨハン・シュトラウス管弦楽団を3会場ツアーに統合する。
差し替えるのは tickets / date / dateLabel / venue / prefecture の5つだけ。
id・genre(new)・_genre・verified は据え置き。根拠＝tmp/built4719.json（ぴあ3ページを機械構築）。
"""
import json, re, sys, shutil, io
sys.stdout.reconfigure(encoding='utf-8')

built = json.load(io.open('tmp/built4719.json', encoding='utf-8'))
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

n = 0
for e in EVENTS:
    if e['id'] != 4719:
        continue
    print('before: date=%s / pref=%s / 枠%d' % (e.get('date'), e.get('prefecture'), len(e.get('tickets') or [])))
    for k in ('tickets', 'date', 'dateLabel', 'venue', 'prefecture'):
        e[k] = built[k]
    print('after : date=%s / pref=%s / 枠%d' % (e.get('date'), e.get('prefecture'), len(e.get('tickets') or [])))
    n += 1

if n:
    shutil.copyfile('index.html', 'index.html.bak_0820_4719')
    open('index.html', 'w', encoding='utf-8').write(
        h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
print('=== %d件 更新 ===' % n)
