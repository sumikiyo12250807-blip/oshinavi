# -*- coding: utf-8 -*-
"""id7731 海宝直人 のプレリザーブ枠の date を、ぴあの締切に合わせる。

■ 何を間違えたか
reconcile_pia が出した MISSING の情報＝「[発売前] 9/12 11:00発売 **(2026-09-16)**」。
括弧の中は**締切**なのに、date を発売日(2026-09-12)で入れてしまった。
そのせいで同じ枠が MISSING と STALE の両方に出た。

■ 直し
  startDate 2026-09-12（発売日）はそのまま
  date      2026-09-12 → **2026-09-16**（締切）

🚨締切が分かっている発売前の枠は date に締切を入れる（[[feedback_ticket_date]]）。
   締切が出ていない枠だけ date=発売日になる。
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

src = io.open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))

hit = 0
for e in events:
    if e['id'] != 7731:
        continue
    for t in e.get('tickets') or []:
        if (t.get('type') or '').startswith('プレリザーブ') and t.get('date') == '2026-09-12':
            print('  直す前: %s  date=%s start=%s'
                  % (t.get('type'), t.get('date'), t.get('startDate')))
            t['date'] = '2026-09-16'
            print('  直した後: %s  date=%s start=%s'
                  % (t.get('type'), t.get('date'), t.get('startDate')))
            hit += 1

if not hit:
    print('直す枠が無かった（もう直っている？）')
    sys.exit(0)

out = (src[:m.start()] + m.group(1)
       + json.dumps(events, ensure_ascii=False, indent=2) + m.group(3) + src[m.end():])

if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
io.open('index.html', 'w', encoding='utf-8').write(out)
print('書き込み完了')
