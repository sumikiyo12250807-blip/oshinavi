# -*- coding: utf-8 -*-
"""id6159「藝大定期邦楽 第92回」の下書きジャンルを dento → hougaku に直す。
ぴあ区分は「クラシック/クラシック邦楽」＝演奏を聴くもの＝音楽側の伝統
（feedback_dento_split_music_stage）。道具側（build_pia_entries）は同時に直した。"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
src = open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
EV = json.loads(m.group(2))
hit = 0
for e in EV:
    if e['id'] == 6159 and e.get('_genre') == 'dento':
        e['_genre'] = 'hougaku'
        hit = 1
        print(f"id6159 {e.get('artist')} _piaSub={e.get('_piaSub')} → _genre=hougaku")
if not hit:
    print('該当なし（すでに直っている？）')
    sys.exit(0)
nl = '\r\n' if '\r\n' in src else '\n'
arr = json.dumps(EV, ensure_ascii=False, indent=2).replace('\r\n', '\n').replace('\n', nl)
open('index.html.bak_0902_6159', 'w', encoding='utf-8', newline='').write(src)
open('index.html', 'w', encoding='utf-8', newline='').write(
    src[:m.start()] + m.group(1) + arr + m.group(3) + src[m.end():])
print('applied')
