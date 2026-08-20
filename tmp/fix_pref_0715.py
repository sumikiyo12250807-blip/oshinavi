#!/usr/bin/env python3
"""県誤検出4件を修正（prefecture / dateLabel / tickets[].type の「全国」→実県）

原因：会場名の「東京エレクトロン」(命名権)から"東京"を拾い、実県と2県になって全国化。
ぴあ__regionで裏取り済み：1097宮城 / 2134山梨 / 2300宮城 / 2338山梨
"""
import datetime
import json
import re
import sys
sys.path.insert(0, 'tools')
from build_pia_entries import PREF_RE  # stdoutをUTF-8ラップ

FIX = {1097: '宮城', 2134: '山梨', 2300: '宮城', 2338: '山梨'}

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(const\s+EVENTS\s*=\s*)(\[.*?\])(;\s*\n)', h, re.S)
if not m:
    print('!! EVENTS配列が見つからない'); sys.exit(1)
EVENTS = json.loads(m.group(2))

n = 0
for e in EVENTS:
    pref = FIX.get(e.get('id'))
    if not pref:
        continue
    before = (e.get('prefecture'), e.get('dateLabel'))
    e['prefecture'] = pref
    lab = e.get('dateLabel') or ''
    venue = e.get('venue') or ''
    # 「… 全国 会場名」/「… 全国ツアー」→ 実県表記に統一（T-SQUARE形＝日付 県 会場）
    if ' 全国ツアー' in lab:
        lab = lab.replace(' 全国ツアー', f' {pref} {venue}')
    lab = lab.replace(' 全国 ', f' {pref} ')
    # 「2026年9月4日(金)〜2026年9月4日(金)」の同日重複を単日形に畳む
    lab = re.sub(r'(\d+年\d+月\d+日\([日月火水木金土]\))〜\1', r'\1', lab)
    e['dateLabel'] = lab
    for t in e.get('tickets', []):
        t['type'] = t.get('type', '').replace('（全国 ', f'（{pref} ')
    print(f"id={e['id']} {e.get('name')}")
    print(f"   pref: {before[0]} → {pref}")
    print(f"   dateLabel: {before[1]}")
    print(f"          →   {lab}")
    for t in e.get('tickets', []):
        print(f"   枠: {t.get('type')}")
    n += 1

bak = f'index.html.bak_{datetime.date.today():%m%d}_pref_fix'
open(bak, 'w', encoding='utf-8').write(h)
new = h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():]
open('index.html', 'w', encoding='utf-8').write(new)
print(f'\n=== {n}件 修正 (backup: {bak}) ===')
