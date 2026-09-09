# -*- coding: utf-8 -*-
"""id950 天満天神繁昌亭の 11/16 総称枠を1つだけ外す。
ぴあ eventCd=2630742 は 11/16 が【13:30公演】【19:00公演】の2枚だけで、総称の枠は存在しない
（自分で pia_cards.py で数えて確認済み・カード8枚）。昼のヒールで昼夜2枚を足したのに
総称枠が残ったので、同じ公演が画面に3つ出ていた。
🚨外す条件を厳しくする＝type完全一致 かつ 同じeventCd かつ 置き換え先の2枚が居ること。
"""
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

TARGET = '一般発売（大阪 11/16公演）9/16 10:00発売'
KEEP = ['一般発売【11/16（月）13:30公演】（大阪 11/16公演）9/16 10:00発売',
        '一般発売【11/16（月）19:00公演】（大阪 11/16公演）9/16 10:00発売']

h = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
events = json.loads(m.group(2))
e = next(x for x in events if x['id'] == 950)

types = [t.get('type') for t in e['tickets']]
assert all(k in types for k in KEEP), '置き換え先の昼夜2枚が見つからない。中止する'
hit = [t for t in e['tickets'] if t.get('type') == TARGET]
assert len(hit) == 1, '総称枠が %d件（1件でないので中止）' % len(hit)
assert '2630742' in (hit[0].get('url') or ''), 'eventCdが違う。中止する'

before = len(e['tickets'])
e['tickets'] = [t for t in e['tickets'] if t is not hit[0]]
print('id950 枠 %d → %d（外した: %s）' % (before, len(e['tickets']), TARGET))

if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
out = h[:m.start(2)] + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', '\r\n') + h[m.end(2):]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
print('書き込み完了')
