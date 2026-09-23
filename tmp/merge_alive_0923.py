# -*- coding: utf-8 -*-
"""mark_soldout が「ぴあに買える枠がある」と言った58件の取りこぼしを、登録へ足し込む（2026-09-23 昼）。
🚨足し算＝既存の枠は1つも消さない。ビルドの枠のうち、券種名＋締切が登録に無いものだけ足す。
🚨飛び先URLが空の枠には、その候補のぴあURLを焼く（[[feedback_tour_per_ticket_url]]）。
⛔id21880 林家希林は外す＝ぴあの実ページは「後日、販売を予定しております」で、
   ビルダーが拾う「9/10 10:00発売」は古い表示。ユーザーの返事待ち。
使い方: python merge_alive.py [--apply]
"""
import io
import json
import re
import sys

APPLY = '--apply' in sys.argv
SKIP = {21880}
SCR = r"C:\Users\user\AppData\Local\Temp\claude\C--Users-user-oshinavi\211b8b3d-6701-4434-8b7f-224ce869b3f9\scratchpad"

built = {e['id']: e for e in json.load(io.open(SCR + r"\built_alive.json", encoding='utf-8'))}
cand = {c['newid']: c for c in json.load(io.open(SCR + r"\cand_alive.json", encoding='utf-8'))}

text = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[)', text)
start = m.start(1)
events, end = json.JSONDecoder().raw_decode(text, start)

log = []
added_total = 0
touched = 0
for ev in events:
    i = ev.get('id')
    if i not in built or i in SKIP:
        continue
    b = built[i]
    src = (cand[i]['urls'] or [None])[0]
    have = set(((t.get('type') or ''), t.get('date')) for t in (ev.get('tickets') or []))
    added = []
    for t in (b.get('tickets') or []):
        k = ((t.get('type') or ''), t.get('date'))
        if k in have:
            continue
        t = dict(t)
        if not t.get('url'):
            t['url'] = src
        ev.setdefault('tickets', []).append(t)
        have.add(k)
        added.append(t['type'])
    if added:
        ev['verifiedAt'] = '2026-09-23'
        touched += 1
        added_total += len(added)
        log.append('✅ id=%-6s +%d枠  %s' % (i, len(added), (ev.get('name') or ev.get('artist') or '')[:30]))
        for a in added:
            log.append('        + %s' % a)

log.append('--- %d件に %d枠を足した（外した id=%s）---' % (touched, added_total, sorted(SKIP)))
io.open('tmp/merge_alive_report.txt', 'w', encoding='utf-8').write('\n'.join(log) + '\n')
sys.stdout.write('done: tmp/merge_alive_report.txt (%d entries, %d slots)\n' % (touched, added_total))
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
