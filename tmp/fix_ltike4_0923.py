# -*- coding: utf-8 -*-
"""ローチケ4件の「発売日が締切に化けた枠」を、実ページの受付期間で直す（2026-09-23 朝）。
ローチケは WebFetch が通らないので実ブラウザで読んだ（[[reference_ltike_machine_unreachable]]）。
読んだ受付期間（そのまま写し）:
  id7819 REVERSE EDGE 2 (神奈川 11/2)  先着 2026/9/19 10:00 〜 2026/10/21 23:00
  id7820 別府葉子       (大阪 12/19)  先着一般 2026/9/20 10:00 〜 2026/12/18 23:59（残りわずか）
  id7821 野田かつひこ    (福岡 12/15)  先着一般 2026/9/14 10:00 〜 2026/12/14 23:59
  id10762 新日本プロレス 赤磐(岡山 11/1) 先着一般 2026/9/20 10:00 〜 2026/11/1 18:00
使い方: python fix_ltike4.py [--apply]
"""
import io
import json
import re
import sys

APPLY = '--apply' in sys.argv

# (id, 直す枠の今の type, 新しい type, 新しい date)
FIX = [
    (7819, '一般発売（神奈川 11/2公演）9/19 10:00発売',
     '先着（神奈川 11/2公演）〜10/21 23:00', '2026-10-21'),
    (7820, '一般発売（大阪 12/19公演）9/20 10:00発売',
     '一般発売（大阪 12/19公演）〜12/18 23:59', '2026-12-18'),
    (7821, '一般発売（福岡 12/15公演）9/14 10:00発売',
     '一般発売（福岡 12/15公演）〜12/14 23:59', '2026-12-14'),
    (10762, '一般発売（岡山 11/1公演）9/20 10:00発売',
     '一般発売（岡山 11/1公演）〜11/1 18:00', '2026-11-01'),
]

text = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[)', text)
start = m.start(1)
events, end = json.JSONDecoder().raw_decode(text, start)
by = {e.get('id'): e for e in events}

log = []
for eid, old, new, newdate in FIX:
    e = by.get(eid)
    if e is None:
        log.append('⚠️ id=%s が見つからない' % eid)
        continue
    hits = [t for t in (e.get('tickets') or []) if (t.get('type') or '') == old]
    if len(hits) != 1:
        log.append('⚠️ id=%s 直す枠が %d件（1件でないので触らない）: %s' % (eid, len(hits), old))
        continue
    t = hits[0]
    before = (t.get('type'), t.get('date'), t.get('startDate'))
    t['type'] = new
    t['date'] = newdate
    # 発売開始はもう過ぎている＝startDate は残す（「発売開始まであとX日」には出ない）
    log.append('✅ id=%-6s %s | %s  →  %s | %s' % (eid, before[0], before[1], new, newdate))

io.open('tmp/fix_ltike4_report.txt', 'w', encoding='utf-8').write('\n'.join(log) + '\n')
sys.stdout.write('done: tmp/fix_ltike4_report.txt\n')
if not APPLY:
    sys.stdout.write('(--apply de write)\n')
    raise SystemExit(0)
body = json.dumps(events, ensure_ascii=False, indent=2).replace('\r\n', '\n').replace('\n', '\r\n')
data = (text[:start] + body + text[end:]).encode('utf-8')
if data.count(b'\r\n') != data.count(b'\n'):
    sys.stdout.write('ABORT: CRLF broken\n')
    raise SystemExit(1)
io.open('index.html', 'wb').write(data)
sys.stdout.write('written (crlf %d)\n' % data.count(b'\r\n'))
