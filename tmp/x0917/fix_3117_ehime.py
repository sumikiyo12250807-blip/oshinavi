# -*- coding: utf-8 -*-
"""3117 佐野元春&THE COYOTE BAND 愛媛9/25の締切をぴあの実表示に合わせる（2026-09-16 夜）。

reconcile が MISSING「[受付中] 〜9/24 23:59 一般発売」と言い続けたのは、枠が無いからではなく
**締切がずれているから**。ぴあの愛媛のページ（eventCd=2623020）を機械パースした結果は
  一般発売（愛媛 9/25公演）〜9/24 23:59
で、登録は
  一般発売（愛媛 9/25公演）〜9/9 23:59
＝ぴあが 9/9 → 9/24 に延ばしている（feedback_deadline_extended_after_register）。

merge_with_urls は「骨格（券種名＋（…公演））が既存にある枠は触らない」作りなので足されない＝
締切の更新はこちらで当てる。飛び先（ticket.url）は既存のものをそのまま残す。
使い方: python tmp/x0917/fix_3117_ehime.py [--apply]
"""
import io
import json
import re
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')
P = 'index.html'
ID = 3117
OLD = '一般発売（愛媛 9/25公演）〜9/9 23:59'
NEW = '一般発売（愛媛 9/25公演）〜9/24 23:59'
NEWDATE = '2026-09-24'

src = io.open(P, encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
e = next(x for x in events if x['id'] == ID)
hit = [t for t in e['tickets'] if t['type'] == OLD]
assert len(hit) == 1, [t['type'] for t in e['tickets']]
assert not any(t['type'] == NEW for t in e['tickets']), '既に新しい締切の枠がある'
t = hit[0]
print('id%d %s' % (ID, OLD))
print('     -> %s  (date %s -> %s)' % (NEW, t.get('date'), NEWDATE))
t['type'] = NEW
t['date'] = NEWDATE
if '--apply' in sys.argv:
    shutil.copyfile(P, 'index.html.bak_0916_ehime3117')
    out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', '\r\n') + m.group(3) + src[m.end():]
    io.open(P, 'w', encoding='utf-8', newline='').write(out)
    print('wrote')
