# -*- coding: utf-8 -*-
"""5041/5042（第20回アジア競技大会）の2つの誤りを直す（2026-08-22・検証エージェントの指摘＋実ページで裏取り済）。

① startDate の誤り＝一般発売枠に startDate=2026-08-22 が入っていて、画面が「本日発売」になり
   一日中いちばん上に並んでしまう。実ページ（ticketInformation.do?eventCd=2610261 / 2620084）は
   **2026/7/15(水) 10:00 より発売・販売期間 〜9/26 16:00 / 〜9/29 18:00**。→ startDate を 2026-07-15 に直す。
② 券種名落ち＝8/22 10:00 発売の枠は実物が **《ラウンジホスピタリティチケット》**（別商品）。
   同じ「一般発売」に見えて画面で区別できない（[[feedback_pia_parser_flattens_slots]]／
   [[feedback_same_day_show_time_badge]]の考え方）。→ バッジ文言に券種名を入れる。
"""
import io
import json
import re
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
by = {e['id']: e for e in EVENTS}

LOUNGE = '《ラウンジホスピタリティチケット》'
n = 0
for i in (5041, 5042):
    e = by[i]
    for t in e['tickets']:
        if t.get('startDate') == '2026-08-22' and (t.get('date') or '') > '2026-08-22':
            t['startDate'] = '2026-07-15'
            print('id%d startDate 2026-08-22 → 2026-07-15 | %s' % (i, t['type']))
            n += 1
        elif '8/22 10:00発売' in (t.get('type') or '') and LOUNGE not in t['type']:
            t['type'] = t['type'].replace('一般発売', '一般発売' + LOUNGE, 1)
            print('id%d 券種名を追記 | %s' % (i, t['type']))
            n += 1
    e['verifiedAt'] = '2026-08-22'

print('直した枠 %d' % n)
shutil.copyfile('index.html', 'index.html.bak_0822_asia')
open('index.html', 'w', encoding='utf-8').write(
    h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
print('適用した')
