#!/usr/bin/env python3
"""dateLabelの「同日〜同日」冗長表記を単日形に畳む。

例: 「2026年8月3日(月)〜2026年8月3日(月) 東京 白金高輪 SELENE b2」
  → 「2026年8月3日(月) 東京 白金高輪 SELENE b2」
真因: 同一公演日の枠が2つあると starts=['8/3','8/3'] で len==1 を満たさず範囲形に落ちていた
     （build_pia_entries 側も恒久修正済み）。
"""
import datetime
import json
import re
import sys
sys.path.insert(0, 'tools')
import build_pia_entries  # noqa  stdoutをUTF-8ラップ

SAME_DAY = re.compile(r'(\d+年\d+月\d+日\([日月火水木金土]\))〜\1')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(const\s+EVENTS\s*=\s*)(\[.*?\])(;\s*\n)', h, re.S)
EVENTS = json.loads(m.group(2))

fixed_new, fixed_old = [], []
for e in EVENTS:
    lab = e.get('dateLabel') or ''
    new = SAME_DAY.sub(r'\1', lab)
    if new != lab:
        e['dateLabel'] = new
        rec = (e.get('id'), e.get('name'), lab, new)
        (fixed_new if e.get('genre') == 'new' else fixed_old).append(rec)

print(f'=== 新着(genre:new) {len(fixed_new)}件 ===')
for i, nm, b, a in fixed_new:
    print(f'id={i} {nm}')
    print(f'   before: {b}')
    print(f'   after : {a}')
print(f'\n=== 既存 {len(fixed_old)}件（同じ冗長表記・ついでに掃除）===')
for i, nm, b, a in fixed_old:
    print(f'id={i} {nm} | {b} → {a}')

if fixed_new or fixed_old:
    bak = f'index.html.bak_{datetime.date.today():%m%d}_datelabel'
    open(bak, 'w', encoding='utf-8').write(h)
    out = h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():]
    open('index.html', 'w', encoding='utf-8').write(out)
    print(f'\n適用 (backup: {bak})')
else:
    print('\n該当なし')
