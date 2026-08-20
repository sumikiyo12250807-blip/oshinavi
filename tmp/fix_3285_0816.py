# -*- coding: utf-8 -*-
"""id3285 ルシファー吉岡ネタライブ2026 の手当て（昼ヒールの安全弁で未適用だった子）。
ぴあ eventCd=2629085 実ページ（14:30時点）:
  一般発売 = 本日発売初日 〜2026/10/24(土)23:59  ← 買える
  先行3枠(マセキライブサークル/1次/2次) = 抽選受付終了 ← 登録の3枠はdateが過去で自然に落ちる
一括適用だと生きた枠が消える形に見えたのは、ぴあが終了枠を返さないため。一般発売枠だけ締切を入れる。
"""
import re, json, sys, os
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

for e in EVENTS:
    if e.get('id') != 3285:
        continue
    for t in e.get('tickets') or []:
        if (t.get('type') or '').startswith('一般発売') and t.get('date') == '2026-08-16':
            t['type'] = "一般発売（東京・大阪・北海道 9/21〜10/25公演）〜10/24 23:59"
            t['date'] = "2026-10-24"
            t.pop('startDate', None)
            print("販売中に変換 →", t['type'], t['date'])
    e['tickets'].sort(key=lambda t: (t.get('date') or ''))
    break
else:
    print("id3285 が見つからない"); sys.exit(1)

bak = 'index.html.bak_0816_fix3285'
if not os.path.exists(bak):
    open(bak, 'w', encoding='utf-8', newline='').write(h)
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
open('index.html', 'w', encoding='utf-8', newline='').write(
    h[:m.start()] + m.group(1) + new_arr.replace('\n', '\r\n') + m.group(3) + h[m.end():])
print("=== 適用 ===")
