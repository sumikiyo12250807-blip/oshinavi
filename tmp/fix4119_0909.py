# -*- coding: utf-8 -*-
"""id4119 の artist を「稲垣潤一」に直す（name は公式の公演名のまま残す）。
裏取り＝ぴあ実ページ eventCd=2628511 に「［出演］稲垣潤一」と書いてある（2026-09-09 に自分で確認）。
Why＝検索候補は artist から作るので、いまのままだと「稲垣潤一」で探した人が見つけられない。
"""
import io, re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

h = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
events = json.loads(m.group(2))
e = next(x for x in events if x['id'] == 4119)
assert e['artist'] == 'JUNICHI INAGAKI Christmas Dinner Show', '中身が違う。中止'
print('旧 artist =', e['artist'])
e['artist'] = '稲垣潤一'
print('新 artist =', e['artist'])
print('name はそのまま =', e['name'])

if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
out = h[:m.start(2)] + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', '\r\n') + h[m.end(2):]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
print('書き込み完了')
