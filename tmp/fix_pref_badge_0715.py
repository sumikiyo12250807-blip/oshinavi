#!/usr/bin/env python3
"""県誤検出4件のバッジ内県名を掃除（「（宮城・東京 9/4公演）」→「（宮城 9/4公演）」）

会場名の「東京エレクトロン」から拾った"東京"がバッジにも残っていた。
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
EVENTS = json.loads(m.group(2))

n = 0
for e in EVENTS:
    pref = FIX.get(e.get('id'))
    if not pref:
        continue
    for t in e.get('tickets', []):
        old = t.get('type', '')
        # 「（<県リスト> M/D公演）」の県リスト部分を正しい1県に置換
        new = re.sub(r'（[^） ]+ (\d{1,2}/\d{1,2}[^）]*公演)）', f'（{pref} \\1）', old, count=1)
        if new != old:
            t['type'] = new
            print(f"id={e['id']} {e.get('name')}")
            print(f"   before: {old}")
            print(f"   after : {new}")
            n += 1

bak = f'index.html.bak_{datetime.date.today():%m%d}_pref_badge'
open(bak, 'w', encoding='utf-8').write(h)
new_html = h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():]
open('index.html', 'w', encoding='utf-8').write(new_html)
print(f'\n=== バッジ{n}枠 修正 (backup: {bak}) ===')
