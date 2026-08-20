# -*- coding: utf-8 -*-
"""id=38 アフタヌーン40周年展(e+・非ぴあ)。
前売券は7/9 23:59で受付終了、当日券が7/10 00:00〜7/26 18:00で受付中(e+生ページ裏取り)。
ぴあリンクが無く機械照合をすり抜けるため手当て。[[feedback_delete_nonpia_blindspot]]"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DRY = '--apply' not in sys.argv
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
for e in EVENTS:
    if e['id'] != 38: continue
    e['tickets'] = [{
        "type": "当日券 一般発売 先着（東京 7/12〜7/26会期）〜7/26 18:00",
        "startDate": "2026-07-10",
        "date": "2026-07-26",
    }]
    e['verifiedAt'] = "2026-07-10"
    print(json.dumps(e['tickets'], ensure_ascii=False, indent=1))
if DRY:
    print("(DRY)")
else:
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    open('index.html.bak_0710_fix38','w',encoding='utf-8').write(h)
    open('index.html','w',encoding='utf-8').write(h[:m.start()]+m.group(1)+new_arr+m.group(3)+h[m.end():])
    print("written")
