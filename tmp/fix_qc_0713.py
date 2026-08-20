# -*- coding: utf-8 -*-
"""新着QCで出た2件を修正。
 id2560 K-1: 券種名の「◎K-1.CLUB◎」囲み装飾が中間◎として残っている → 囲みごと除去
 id2516 加藤大樹（p）: venue「全国ツアー（）」の空カッコ → ぴあが持つ県（福岡/佐賀/大分）で埋める
   ※会場名はぴあにも公式にも出ていないため県表記。推測で会場名を書かない。
"""
import re, json, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
E = json.loads(m.group(2))

changed = []
for e in E:
    if e['id'] == 2560:
        for t in e.get('tickets', []):
            old = t.get('type', '')
            new = re.sub(r'^[^◎]*◎', '', old).strip()
            if new != old:
                t['type'] = new
                changed.append(f"id2560 券種 '{old}' → '{new}'")
    if e['id'] == 2516:
        old = e.get('venue', '')
        if old == '全国ツアー（）':
            e['venue'] = '全国ツアー（福岡・佐賀・大分）'
            changed.append(f"id2516 会場 '{old}' → '{e['venue']}'")

for c in changed:
    print(' ', c)
bak = f'index.html.bak_{datetime.date.today():%m%d}_qc'
open(bak, 'w', encoding='utf-8').write(h)
new_arr = json.dumps(E, ensure_ascii=False, indent=2)
open('index.html', 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print(f'=== {len(changed)}件修正 (backup {bak}) ===')
