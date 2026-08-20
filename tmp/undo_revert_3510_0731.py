# -*- coding: utf-8 -*-
"""id3510 を新着へ戻した操作を取り消す（ユーザー訂正 7/31「第39期竜王戦は無し」）。
dento + extraGenres:["sports"] の振り分け済み状態に復帰し、NEW_ORDER を空に戻す。"""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(const\s+EVENTS\s*=\s*)(\[.*?\])(;\s*\n)', h, re.S)
EVENTS = json.loads(m.group(2))
e = next(x for x in EVENTS if x['id'] == 3510)

e['genre'] = e.pop('_genre')
extra = e.pop('_extraGenres', [])
if extra:
    e['extraGenres'] = extra
e.pop('_piaSub', None)
print('id3510: genre=%s extraGenres=%s 下書き=%s' % (
    e['genre'], e.get('extraGenres'), [k for k in e if k.startswith('_')]))

left = [x['id'] for x in EVENTS if x.get('genre') == 'new']
if left:
    raise SystemExit('genre:new が残っている: %s' % left)

new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
body = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]
mo = re.search(r'(const\s+NEW_ORDER\s*=\s*)(\[[^\]]*\])', body)
body = body[:mo.start()] + mo.group(1) + '[]' + body[mo.end():]
open('index.html', 'w', encoding='utf-8').write(body)

b = open('index.html', 'rb').read()
print('CRLF=%d 単独LF=%d' % (b.count(b'\r\n'), b.count(b'\n') - b.count(b'\r\n')))
print('=== 復帰完了 / NEW_ORDER=[] ===')
