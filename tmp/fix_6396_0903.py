# -*- coding: utf-8 -*-
"""id6396 吉川晃司から「熊本 8/1公演」の枠を外す。
理由＝8/1は既に終わった公演。ぴあのbundleページに古い枠（6/27発売開始）が残っていて
ビルダーが拾ってしまった。画面には出ていない（販売期間が過去で非表示）が、
venue と prefecture に熊本が残ると「熊本でもやる」と誤解される。
残すのは東京10/16公演（9/5 10:00発売）。
"""
import re, json, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
src = open('index.html', encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in src else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))

hit = 0
for e in events:
    if e.get('id') != 6396:
        continue
    before = len(e.get('tickets', []))
    e['tickets'] = [t for t in e.get('tickets', []) if '熊本 8/1公演' not in (t.get('type') or '')]
    after = len(e['tickets'])
    print('枠 %d → %d' % (before, after))
    assert after == 1, '残る枠が1つでない'
    e['venue'] = '国立代々木競技場 第一体育館'
    e['prefecture'] = '東京'
    hit += 1

if hit != 1:
    print('!! hit=%d なので書き戻さない' % hit)
    sys.exit(1)

open('index.html.bak_0903_fix6396', 'w', encoding='utf-8', newline='').write(src)
dumped = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl)
open('index.html', 'w', encoding='utf-8', newline='').write(
    src[:m.start()] + m.group(1) + dumped + m.group(3) + src[m.end():])
print('id6396 を東京10/16公演だけにした')
