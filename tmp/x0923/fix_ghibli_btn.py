# -*- coding: utf-8 -*-
"""id40「ジブリパーク展 大阪」のAmazonボタンの文字を「ガイドブックを見る」にする。2026-09-23 夜。

ユーザー「**ジブリパークのCDのボタンを押したらジブリパーク公式ガイドブックが出て来た
　どうせならCDボタンじゃなく　ガイドブック　ボタンにして**」。

- 仕組み＝`links.amazonLabel` を足すとボタンの文字が変わる（三木大雲＝「三木大雲の著書」と同じ形）。
- 🚨リンク先は触らない＝ガイドブックが出ているなら中身は合っている。
  [[feedback_fix_only_what_was_pointed_at]]＝**指摘された1か所だけ直す**（他の展示エントリには広げない）。
- [[feedback_button_label_matches_result]]＝ボタンの文字は「押した人の期待」に合わせる。

使い方: python tmp/x0923/fix_ghibli_btn.py [--apply]
"""
import io
import json
import re
import sys

APPLY = '--apply' in sys.argv
PATH = 'index.html'
TARGET = 40
LABEL = 'ガイドブックを見る'

text = io.open(PATH, encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[)', text)
start = m.start(1)
events, end = json.JSONDecoder().raw_decode(text, start)

hit = [e for e in events if e['id'] == TARGET]
if not hit:
    sys.stdout.write('id%d が無い\n' % TARGET)
    raise SystemExit(1)
e = hit[0]
links = e.setdefault('links', {})
if not links.get('amazon'):
    sys.stdout.write('id%d に amazon リンクが無い＝何もしない\n' % TARGET)
    raise SystemExit(0)
before = links.get('amazonLabel')
links['amazonLabel'] = LABEL
sys.stdout.write('id%d %s\n  label: %s -> %s\n' % (TARGET, e.get('name'), before, LABEL))

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
