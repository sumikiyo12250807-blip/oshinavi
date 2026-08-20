# -*- coding: utf-8 -*-
"""今夜のX投稿対象エントリを、ぴあ実ページと突き合わせて取りこぼしを洗い出す（読むだけ・書き換えなし）。

各エントリの links.pia を tools/pia_tickets.py --json で全券種パースし、
「買える枠(発売前/受付中)」の公演日が、登録済み ticket.type の文字列に現れているかで判定する。
（ぴあ429対策で1件ごとに待つ: reference_pia_rate_limit_429）
"""
import io
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from check_expired import extract_events_array

IDS = [1637, 2151, 2153, 2159, 2178, 2185, 2188, 2311, 2900, 3118, 3191]
OUT = os.path.join(HERE, 'audit_x_0801.txt')

events = {e['id']: e for e in extract_events_array('index.html')}
lines = []
summary = []

for eid in IDS:
    e = events.get(eid)
    if not e:
        lines.append(f'### id={eid} 見つからない')
        continue
    pia = (e.get('links') or {}).get('pia')
    name = e.get('name')
    lines.append(f'### id={eid} {name}')
    lines.append(f'  登録枠 {len(e.get("tickets") or [])}件 / pia={pia}')
    if not pia:
        lines.append('  → piaリンク無し・機械照合できない')
        lines.append('')
        summary.append((eid, name, None, None))
        continue

    try:
        r = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'pia_tickets.py'), pia, '--json'],
                           capture_output=True, timeout=90)
        rows = json.loads(r.stdout.decode('utf-8', 'replace'))
    except Exception as ex:
        lines.append(f'  → 取得失敗 {ex}')
        lines.append('')
        summary.append((eid, name, None, None))
        continue

    buyable = [x for x in rows if x.get('state') in ('発売前', '受付中')]
    reg_text = ' '.join((t.get('type') or '') for t in (e.get('tickets') or []))

    missing = []
    for x in buyable:
        pd = x.get('perfdate') or ''
        m = re.match(r'(\d{4})-(\d{2})-(\d{2})', pd)
        if not m:
            continue
        md = f'{int(m.group(2))}/{int(m.group(3))}'
        if md not in reg_text:
            missing.append((md, x.get('pref'), x.get('venue'), x.get('title'), x.get('state'), x.get('when')))

    lines.append(f'  ぴあ買える枠 {len(buyable)}件 / うち登録に公演日が無い {len(missing)}件')
    for md, pref, venue, title, state, when in missing:
        lines.append(f'    ★{md} {pref} {venue} | {title} | [{state}] {when}')
    lines.append('')
    summary.append((eid, name, len(buyable), len(missing)))
    time.sleep(3)

lines.append('=== まとめ ===')
for eid, name, nb, nm in summary:
    lines.append(f'id={eid} {name}: ぴあ買える{nb} / 取りこぼし候補{nm}')

with io.open(OUT, 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(lines))
print('wrote', OUT)
