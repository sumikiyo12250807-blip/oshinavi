# -*- coding: utf-8 -*-
"""ラベル規則を直したビルダーで id3508 THE AWAODORI の枠を作り直して差分を見る（--apply で適用）。
現物編集＝tickets のみ置換・id据え置き（[[feedback_new_list_order_lock]]）。"""
import json
import re
import sys

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
from build_pia_entries import build
import reconcile_pia as R

APPLY = '--apply' in sys.argv
h = open('index.html', encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in h else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
byid = {e['id']: e for e in EVENTS}

e = byid[3508]
urls = R.pia_urls(e)
ne = build({'newid': 3508, 'artist': e.get('artist', ''), 'urls': urls})
out = [f"id=3508 {e.get('artist')}", f'  urls={urls}', '', '--- 現在 ---']
for t in e.get('tickets') or []:
    out.append(f"  {t.get('type')}  [date={t.get('date')}]")
out.append('')
out.append('--- 作り直し ---')
if ne is None:
    out.append('  🚨 買える枠ゼロで返ってきた（置換しない）')
else:
    for t in ne['tickets']:
        out.append(f"  {t.get('type')}  [date={t.get('date')}]")
    seen = {}
    for t in ne['tickets']:
        seen[t['type']] = seen.get(t['type'], 0) + 1
    dup = [k for k, v in seen.items() if v > 1]
    out.append('')
    out.append('同一バッジの重複: ' + ('なし' if not dup else str(dup)))

if APPLY and ne is not None:
    e['tickets'] = ne['tickets']
    open('index.html.bak_0730_awa', 'w', encoding='utf-8', newline='').write(h)
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
    open('index.html', 'w', encoding='utf-8', newline='').write(
        h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
    out.append('')
    out.append('=== 適用した (backup: index.html.bak_0730_awa) ===')
else:
    out.append('')
    out.append('=== 表示のみ（適用は --apply） ===')

open('tmp/rebuild_3508_0730.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('wrote tmp/rebuild_3508_0730.txt')
