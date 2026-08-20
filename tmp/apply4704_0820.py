# -*- coding: utf-8 -*-
"""4704 タクフェス第14弾『北の島から』に、抜けていた東京公演の枠を反映する。
差し替えるのは tickets / date / dateLabel / venue / prefecture の5つだけ。
id・genre(new)・_genre・verified などは据え置き（新着プールの番号固定・下書きジャンル温存）。
根拠＝ぴあ b2669977 を build_pia_entries で機械構築（tmp/built4704.json）。
"""
import json, re, sys, shutil, io
sys.stdout.reconfigure(encoding='utf-8')

built = json.load(io.open('tmp/built4704.json', encoding='utf-8'))
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

n = 0
for e in EVENTS:
    if e['id'] != 4704:
        continue
    print('before: date=%s / pref=%s / 枠%d' % (e.get('date'), e.get('prefecture'), len(e.get('tickets') or [])))
    for k in ('tickets', 'date', 'dateLabel', 'venue', 'prefecture'):
        e[k] = built[k]
    print('after : date=%s / pref=%s / 枠%d' % (e.get('date'), e.get('prefecture'), len(e.get('tickets') or [])))
    n += 1

if n:
    shutil.copyfile('index.html', 'index.html.bak_0820_4704')
    open('index.html', 'w', encoding='utf-8').write(
        h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
print('=== %d件 更新 ===' % n)
