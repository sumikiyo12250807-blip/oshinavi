# -*- coding: utf-8 -*-
"""id21607 中村ゆりか＝登録は福岡9/23の1枠だけで、ぴあに4公演あったのを取り込む（2026-09-23 昼）。
バッジ0の番人が「公演まで31日より先なのに買える枠0」で出した分。

ぴあ実ページ（pia_tickets --all / pia_statustext で確認）:
  2616419 宮城 11/21   一般発売 〜11/12 23:59        ← 受付中＝買える
  2623226 東京 R9 1/17 一般発売 〜1/7 23:59          ← 受付中＝買える
  2623108 愛知 10/31   一般発売 **予定枚数終了**     ← 売り切れ＝消さずに印で出す
  2622748 大阪 12/13   一般発売 **予定枚数終了**     ← 同上
  2622423 福岡 9/23    販売終了（公演は今日）        ← 既存の枠をそのまま残す
🚨ev.date は千秋楽 2027-01-17 に直す（10/31のままだと買える枠があるのに画面から消える）。
使い方: python fix_21607.py [--apply]
"""
import io
import json
import re
import sys

APPLY = '--apply' in sys.argv
U = 'https://t.pia.jp/pia/event/event.do?eventCd='

ADD = [
    {'type': '一般発売（宮城 11/21公演）〜11/12 23:59', 'date': '2026-11-12', 'url': U + '2616419'},
    {'type': '一般発売（東京 R9年 1/17公演）〜1/7 23:59', 'date': '2027-01-07', 'url': U + '2623226'},
    {'type': '一般発売（愛知 10/31公演）', 'date': '2026-10-31', 'url': U + '2623108',
     'soldout': True, 'soldoutSince': '2026-09-23'},
    {'type': '一般発売（大阪 12/13公演）', 'date': '2026-12-13', 'url': U + '2622748',
     'soldout': True, 'soldoutSince': '2026-09-23'},
]

text = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[)', text)
start = m.start(1)
events, end = json.JSONDecoder().raw_decode(text, start)
ev = next(e for e in events if e.get('id') == 21607)

have = set((t.get('type') or '') for t in (ev.get('tickets') or []))
added = 0
for s in ADD:
    if s['type'] in have:
        continue
    ev.setdefault('tickets', []).append(dict(s))
    added += 1
# 既存の福岡の枠にも飛び先を焼く（url が空だった）
for t in ev['tickets']:
    if not t.get('url'):
        t['url'] = U + '2622423'
ev['date'] = '2027-01-17'
ev['venue'] = '全国ツアー（福岡トヨタホールスカラエスパシオ／今池ガスホール／仙台PIT／YES THEATER／品川プリンスホテル ステラボール）'
ev['prefecture'] = '全国'
ev['dateLabel'] = '2026年9月23日(水)〜2027年1月17日(日) 全国'
ev['verifiedAt'] = '2026-09-23'

sys.stdout.write('id21607 tickets %d (+%d) / date=%s\n' % (len(ev['tickets']), added, ev['date']))
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
