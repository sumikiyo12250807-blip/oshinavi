# -*- coding: utf-8 -*-
"""id751 吉田山田の「静岡 11/6公演」枠に会場別ぴあURLを付ける。

reconcile が 💤STALE を出したのは枠が死んだからではなく、links.pia が
上野公演(eventCd=2621135)しか指しておらず、浜松公演の枠を照合できなかったから。
ぴあ実ページ（eventCd=2627110）で「抽選受付中 〜2026/8/16 23:59」を確認済み＝生きている。
複数会場ツアーは各ticketに会場別URLを付ける（memory: feedback_tour_per_ticket_url）。
"""
import re, json, io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
APPLY = '--apply' in sys.argv
URL = 'https://t.pia.jp/pia/event/event.do?eventCd=2627110'

PATH = 'index.html'
h = open(PATH, encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EV = json.loads(m.group(2))

for e in EV:
    if e['id'] != 751:
        continue
    for t in e.get('tickets') or []:
        if '静岡' in (t.get('type') or ''):
            print('id=751 %s' % t.get('type'))
            print('   url %s → %s' % (t.get('url'), URL))
            t['url'] = URL

if not APPLY:
    print('\n（提案のみ。適用は --apply）')
    sys.exit(0)

bak = PATH + '.bak_0814_751url'
open(bak, 'w', encoding='utf-8', newline='').write(h)
body = json.dumps(EV, ensure_ascii=False, indent=2)
if '\r\n' in h:
    body = body.replace('\r\n', '\n').replace('\n', '\r\n')
open(PATH, 'w', encoding='utf-8', newline='').write(h[:m.start(2)] + body + h[m.end(2):])
print('\n=== 適用した (backup: %s) ===' % bak)
