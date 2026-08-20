# -*- coding: utf-8 -*-
"""7/1 venue欄修復: [:4]打切りバグで会場が欠けてた「全国ツアー」新着を、
ぴあから全会場取り直してvenue(とdateLabel)だけ更新。ticketsは触らない(1721集約保持)。"""
import re, json, sys, io
sys.path.insert(0, 'tools')
import build_pia_entries as bpe
from build_pia_entries import build
# build_pia_entries が import 時に sys.stdout を UTF-8 ラップ済み。再ラップ禁止(閉じる)。

cands = {c['newid']: c for c in json.load(open('tmp/cands_0701.json', encoding='utf-8'))}
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

targets = [e['id'] for e in EVENTS if e.get('genre') == 'new' and e.get('venue', '').startswith('全国ツアー')]
print('対象(全国ツアー new):', targets)

changed = 0
for e in EVENTS:
    if e['id'] not in targets:
        continue
    c = cands.get(e['id'])
    if not c:
        print(f"  id={e['id']} cand無し skip"); continue
    ne = build({'newid': e['id'], 'artist': c['artist'], 'urls': c['urls']})
    if not ne:
        print(f"  id={e['id']} build None skip"); continue
    old = e['venue']
    if ne['venue'] != old:
        e['venue'] = ne['venue']; e['dateLabel'] = ne['dateLabel']
        changed += 1
        print(f"  id={e['id']} {e['artist'][:20]}")
        print(f"     旧: {old}")
        print(f"     新: {ne['venue']}")
    else:
        print(f"  id={e['id']} 変化なし")

new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
open('index.html.bak_0701_venuefix', 'w', encoding='utf-8').write(h)
open('index.html', 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print(f"=== venue更新 {changed}件 (backup: index.html.bak_0701_venuefix) ===")
if bpe._DROPPED:
    print("!! DROPPED:", bpe._DROPPED)
