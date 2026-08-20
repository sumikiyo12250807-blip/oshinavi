# -*- coding: utf-8 -*-
"""id4226 IKKO の「プレイガイド最速先行（大阪 11/8公演）8/16 11:00発売」を受付中形に直す。
ヒールは今日あたしが足したe+の東京9/29枠2つを消してしまうので安全弁が作動した＝ぴあ枠だけ手で当てる。
根拠＝ぴあ eventCd=2626048 の再取得で「〜8/22 11:00」(date=2026-08-22)。"""
import re, json, sys, os
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

for e in EVENTS:
    if e.get('id') != 4226:
        continue
    for t in e.get('tickets') or []:
        if (t.get('type') or '').startswith('プレイガイド最速先行') and t.get('startDate') == '2026-08-16':
            t['type'] = "プレイガイド最速先行（大阪 11/8公演）〜8/22 11:00"
            t['date'] = "2026-08-22"
            t.pop('startDate', None)
            print("直した →", t['type'], t['date'])
    e['tickets'].sort(key=lambda t: (t.get('date') or ''))
    break
else:
    print("id4226 が見つからない"); sys.exit(1)

bak = 'index.html.bak_0816_fix4226'
if not os.path.exists(bak):
    open(bak, 'w', encoding='utf-8', newline='').write(h)
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
open('index.html', 'w', encoding='utf-8', newline='').write(
    h[:m.start()] + m.group(1) + new_arr.replace('\n', '\r\n') + m.group(3) + h[m.end():])
print("=== 適用 ===")
