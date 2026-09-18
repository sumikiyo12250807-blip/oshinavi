# -*- coding: utf-8 -*-
"""reconcile --new が出した MISSING 28枠を足す（2026-09-18 夜の便）。

対象＝大樹生命 Wリーグ 14件（10/3 20:00の一般発売2種が抜けていた）＋冬の日本海シリーズ（10/24 10:00）。

🚨やり方は**足し算**（[[feedback_heal_flattens_ticket_types]]）＝
   再導出した枠が「今ある枠を全部含んでいる（上位集合）」ことを確かめてから置き換える。
   1枠でも失う組があれば、その組は触らずに報告する。

  python tmp/wl_merge_0918.py          … 調べるだけ
  python tmp/wl_merge_0918.py --apply
"""
import io
import json
import re
import sys

APPLY = '--apply' in sys.argv

h = io.open('index.html', encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in h else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
BUILT = {int(e.get('id') or e.get('newid')): e for e in
         json.load(io.open('tmp/wl_built.json', encoding='utf-8-sig'))}

out = io.open('tmp/wl_merge_0918.txt', 'w', encoding='utf-8')
added = touched = 0
blocked = []
for e in EVENTS:
    b = BUILT.get(e['id'])
    if not b:
        continue
    old = [t.get('type') for t in (e.get('tickets') or [])]
    new = [t.get('type') for t in b['tickets']]
    lost = [t for t in old if t not in new]
    if lost:
        blocked.append((e['id'], e.get('name'), lost))
        out.write('🛡️ 触らない id%d %s ← 消えるはずだった枠: %s\n'
                  % (e['id'], e.get('name'), ' / '.join(lost)))
        continue
    plus = [t for t in b['tickets'] if t.get('type') not in old]
    if not plus:
        out.write('   変化なし id%d %s\n' % (e['id'], e.get('name')))
        continue
    out.write('＋%d枠 id%d %s\n' % (len(plus), e['id'], e.get('name')))
    for t in plus:
        out.write('     - %s | 締切%s | 発売%s\n' % (t.get('type'), t.get('date'), t.get('startDate')))
    added += len(plus)
    touched += 1
    if APPLY:
        e['tickets'] = list(b['tickets'])

out.write('\n=== ＋%d枠 / %d件 / 触らなかった %d件 ===\n' % (added, touched, len(blocked)))
if APPLY:
    assert not blocked, '枠が消える組がある＝適用しない'
    io.open('index.html.bak_0918_wlmerge', 'w', encoding='utf-8', newline='').write(h)
    m2 = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
    io.open('index.html', 'w', encoding='utf-8', newline='').write(
        h[:m2.start()] + m2.group(1)
        + json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
        + m2.group(3) + h[m2.end():])
    b = open('index.html', 'rb').read()
    out.write('CRCRLF=%d / 素のLF=%d\n' % (b.count(b'\r\r\n'), b.count(b'\n') - b.count(b'\r\n')))
out.close()
print('done added=%d touched=%d blocked=%d apply=%s' % (added, touched, len(blocked), APPLY))
