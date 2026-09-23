# -*- coding: utf-8 -*-
"""Blueberry Girls 9/27 福岡（TIGET 524250）を新規エントリとして入れる。2026-09-23 夜。

inject_tiget が②「名前×公演日が一致」で止めた1件。調べたら:
  ・既存 id12156 ＝ artist「Blueberry Girls」／イベント名「この映画を見終わったら 福岡公演」
    （TIGET 517958・INSA 福岡・9/27・前方/一般チケット）
  ・新しい 524250 ＝「Blueberry Girlsツアー直前無銭ライブ」（同じ INSA・同じ 9/27・同じ券種名）
  ・🚨**両方のページが生きている（どちらも HTTP 200）**＝別の名前で両方売られている
→ [[feedback_dedup_badges_keeps_urls]]＝飛び先URLが違えば畳まない。
  [[feedback_oshinavi_concept]]＝買える枠を落とさない。**別エントリとして入れる**。
⚠️同じ会場・同じ日・同じ券種名なので、画面では重複に見える。ユーザーに見せて判断を仰ぐ。

使い方: python tmp/x0923/tiget_bg1.py [--apply]
"""
import io
import json
import re
import sys

APPLY = '--apply' in sys.argv
PATH = 'index.html'
EVNO = '524250'

text = io.open(PATH, encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[)', text)
start = m.start(1)
events, end = json.JSONDecoder().raw_decode(text, start)

if re.search(r'tiget\.net/events/%s' % EVNO, text):
    sys.stdout.write('すでに入っている＝何もしない\n')
    raise SystemExit(0)

built = json.load(io.open('tmp/built_tiget_0923pm.json', encoding='utf-8'))
if isinstance(built, dict):
    built = built.get('entries') or []
src = [e for e in built if EVNO in ((e.get('links') or {}).get('tiget') or '')]
if len(src) != 1:
    sys.stdout.write('組み上がりに見つからない（%d件）\n' % len(src))
    raise SystemExit(1)
e = dict(src[0])

lb = json.load(io.open('.claude/state/last_batch.json', encoding='utf-8'))['batches']
e['id'] = max([x['id'] for x in events] + [b.get('id_to') or 0 for b in lb]) + 1
e['genre'] = 'new'          # ぴあ以外＝振り分けはユーザーの確認後
e.pop('_samename', None)

# 公演日の順に差し込む（並び順の番人が見る）
events.append(e)
sys.stdout.write('id%s %s 枠%d\n' % (e['id'], e.get('name'), len(e.get('tickets') or [])))

if not APPLY:
    sys.stdout.write('(--apply de write)\n')
    raise SystemExit(0)

body = json.dumps(events, ensure_ascii=False, indent=2).replace('\r\n', '\n').replace('\n', '\r\n')
data = (text[:start] + body + text[end:]).encode('utf-8')
if data.count(b'\r\n') != data.count(b'\n'):
    sys.stdout.write('ABORT: CRLF broken\n')
    raise SystemExit(1)
io.open(PATH, 'wb').write(data)
sys.stdout.write('written (crlf %d)\n' % data.count(b'\r\n'))
