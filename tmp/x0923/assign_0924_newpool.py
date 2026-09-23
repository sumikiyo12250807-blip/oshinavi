# -*- coding: utf-8 -*-
"""明日(9/24)発売の新着プールのうち、**売り場がジャンルを言っているものだけ**振り分ける（2026-09-23 夜）。
ユーザー「明日発売のまだ振り分けてない新着も載せてほしい　ジャンルを間違えないで」。

🚨[[feedback_genre_pia_asis_and_other]]＝ジャンルは売り場の言う通りに機械で写す。
   **人が最終判断する枠を作らない**＝売り場がジャンルを出していないものは推測しない。

振り分ける6件（機械で決まる）:
  TIGET 5件 … _srcgenre=tiget:29（＝アイドル）→ idol
  ZAIKO 1件 … ZAIKOはジャンルを出さない（zaiko:?）が、**同じアーティストの既存3件が全部 jpop**
              （id2611／21130／21708 チキン ガーリック ステーキ）＝名前一致で jpop に決まる
振り分けない7件（e+・売り場がジャンルを出していない）＝ユーザーに聞く:
  21150 真田ナオキランチディナーショー／21173 シアターDD -KAGUYA-／21175 ラムネ商店街 紫咲伊織聖誕祭／
  21179 上北健 Acoustic Live／21297 Johnnivan - Club Angie in Tokyo／21333 ゼラOneman Tour
  ※21231 工藤静香＝id7774(dinnershow) と同じ公演／21261 東京キューバンボーイズ＝id7824・11188(jazz) と
    同じ公演＝**どちらも既に投稿に載っている**ので足す必要なし（重複としてユーザーに報告）
使い方: python tmp/x0923/assign_0924_newpool.py [--apply]
"""
import io
import json
import re
import sys

APPLY = '--apply' in sys.argv
ASSIGN = {21026: 'idol', 21036: 'idol', 22457: 'idol', 22460: 'idol', 22468: 'idol',
          20943: 'jpop'}

text = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[)', text)
start = m.start(1)
events, end = json.JSONDecoder().raw_decode(text, start)

log = []
n = 0
for ev in events:
    g = ASSIGN.get(ev.get('id'))
    if not g:
        continue
    if ev.get('genre') != 'new':
        log.append('⏭️ id=%s は既に genre=%s' % (ev['id'], ev.get('genre')))
        continue
    ev['genre'] = g
    ex = ev.pop('_extraGenres', None)
    if ex:
        ev['extraGenres'] = ex
    ev.pop('_genre', None)
    src = ev.pop('_srcgenre', None)
    n += 1
    log.append('✅ id=%-6s → %-6s （売り場の申告 %s）%s' % (ev['id'], g, src or '無し', (ev.get('name') or '')[:34]))

# NEW_ORDER から外す（[[feedback_new_order_array]]）
pool = [e['id'] for e in events if e.get('genre') == 'new']
mo = re.search(r'const NEW_ORDER = \[([^\]]*)\];', text)
arr = [int(x) for x in mo.group(1).split(',') if x.strip()]
kept = [i for i in arr if i in set(pool)]
log.append('--- 振り分け %d件 ／ 新着プール %d件 ／ NEW_ORDER %d→%d ---' % (n, len(pool), len(arr), len(kept)))

io.open('tmp/x0923/assign_0924_report.txt', 'w', encoding='utf-8').write('\n'.join(log) + '\n')
sys.stdout.write('done: %d assigned / pool %d\n' % (n, len(pool)))
if not APPLY:
    sys.stdout.write('(--apply de write)\n')
    raise SystemExit(0)
body = json.dumps(events, ensure_ascii=False, indent=2).replace('\r\n', '\n').replace('\n', '\r\n')
newtext = text[:start] + body + text[end:]
newtext = re.sub(r'const NEW_ORDER = \[[^\]]*\];',
                 'const NEW_ORDER = [%s];' % ', '.join(str(i) for i in kept), newtext, count=1)
data = newtext.encode('utf-8')
if data.count(b'\r\n') != data.count(b'\n'):
    sys.stdout.write('ABORT: CRLF broken\n')
    raise SystemExit(1)
io.open('index.html', 'wb').write(data)
sys.stdout.write('written (crlf %d)\n' % data.count(b'\r\n'))
