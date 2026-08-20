#!/usr/bin/env python3
"""ジャンル下書き補正: 2663 第28回 音の会 = enka → dento

ぴあsub「音楽/演歌・邦楽」は演歌歌手(enka)と和楽器・伝統(dento)が同居する。
実ページで演目「五郎時致／黒御簾音楽／賤機帯／道行初音旅」・問合せ=国立劇場チケットセンター
＝歌舞伎音楽(長唄・義太夫・鳴物)の演奏会と確認 → dento が正。
"""
import datetime
import json
import re
import sys
sys.path.insert(0, 'tools')
import build_pia_entries  # noqa stdout UTF-8

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(const\s+EVENTS\s*=\s*)(\[.*?\])(;\s*\n)', h, re.S)
EVENTS = json.loads(m.group(2))

for e in EVENTS:
    if e.get('id') == 2663:
        print(f"id=2663 {e.get('name')}")
        print(f"   _genre: {e.get('_genre')} → dento")
        e['_genre'] = 'dento'

bak = f'index.html.bak_{datetime.date.today():%m%d}_genre_draft'
open(bak, 'w', encoding='utf-8').write(h)
out = h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():]
open('index.html', 'w', encoding='utf-8').write(out)
print(f'\n適用 (backup: {bak})')
