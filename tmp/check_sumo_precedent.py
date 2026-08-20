# -*- coding: utf-8 -*-
"""既存の「大相撲」「音楽会」系エントリが実際どのジャンルに入っているかを見る
（自分の感覚でなく既存の運用に合わせる＝[[feedback_check_existing_logic]]）。"""
import json
import re

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
out = []
for kw in ('大相撲', '水族館', '縁日', 'おかあさんといっしょ', '竜王戦', '将棋'):
    out.append(f'--- 「{kw}」を含むエントリ ---')
    n = 0
    for e in EVENTS:
        if kw in (e.get('artist') or ''):
            n += 1
            out.append(f"  id={e['id']} genre={e.get('genre')} extra={e.get('extraGenres')} _genre={e.get('_genre')} | {(e.get('artist') or '')[:48]}")
    if not n:
        out.append('  なし')
open('tmp/check_sumo_precedent.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('wrote tmp/check_sumo_precedent.txt')
