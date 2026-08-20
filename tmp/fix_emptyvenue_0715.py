#!/usr/bin/env python3
"""空カッコ会場「全国ツアー（）」3件を実データで埋める（ぴあ実ページ確認済・捏造なし）。

- 2744 大橋ちっぽけ: ぴあが県名のみの全国ツアー→県を列挙
- 2747 9mm Parabellum Bullet: 北海道3会場ツアー(実会場をぴあ実ページで確認)
- 2752 Chevon: ぴあが県名のみの全国ツアー→県を列挙
"""
import datetime
import json
import re
import sys
sys.path.insert(0, 'tools')
from build_pia_entries import norm_fw  # stdout UTF-8

FIX = {
    2744: {'venue': '全国ツアー（北海道・宮城・東京・大阪・兵庫・岡山・広島・愛媛・福岡）', 'pref': '全国'},
    2747: {'venue': '北海道ツアー（CASINO DRIVE／苫小牧ELLCUBE／ペニーレーン24）', 'pref': '北海道'},
    2752: {'venue': '全国ツアー（宮城・新潟・京都・広島・香川）', 'pref': '全国'},
}

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

for e in EVENTS:
    fx = FIX.get(e.get('id'))
    if not fx:
        continue
    old_v, old_l = e.get('venue'), e.get('dateLabel')
    e['venue'] = norm_fw(fx['venue'])
    e['prefecture'] = fx['pref']
    # dateLabel末尾の「全国ツアー（）」空カッコも掃除（あれば）
    e['dateLabel'] = re.sub(r'全国ツアー（\s*）', '全国ツアー', e.get('dateLabel') or '')
    print(f"id={e['id']} {e.get('name')}")
    print(f"   venue: {old_v} → {e['venue']}")
    print(f"   pref : {fx['pref']}")
    print(f"   label: {e['dateLabel']}")

bak = f'index.html.bak_{datetime.date.today():%m%d}_emptyvenue'
open(bak, 'w', encoding='utf-8').write(h)
out = h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():]
open('index.html', 'w', encoding='utf-8').write(out)
print(f'\n=== 3件修正 (backup: {bak}) ===')
