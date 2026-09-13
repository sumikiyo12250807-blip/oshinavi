# -*- coding: utf-8 -*-
"""SPY×FAMILY 2 の二重登録を畳む（2026-09-13・ユーザー「①両方」）。

何が起きていたか＝同じ枠「一般発売（愛知 12/13〜12/19公演）9/13 10:00発売」が
  id353（ツアーまとめ・bundle b2667826・genre=2.5ji）
  id4615（御園座だけ・eventCd=2623310・genre=musical）
の2枚のカードに出ていた。

やること
  ① id353 のジャンルを「両方方式」にする（memory feedback_genre_both_when_unclear）
     主はぴあの区分に従う＝ぴあは「演劇/ミュージカル・ショー」なので **musical が主**、2.5ji をサブへ。
  ② 🚨畳む前に、id4615 の飛び先 eventCd=2623310 を id353 の愛知の枠へ焼き込む
     （memory feedback_tour_per_ticket_url＝url が空のまま畳むと、その会場の売り場への導線が消える）
  ③ id4615 を消す

使い方: python tmp/fix_spyfamily_0913.py [--apply]
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
APPLY = '--apply' in sys.argv
MISONO = 'https://t.pia.jp/pia/event/event.do?eventCd=2623310'

path = 'index.html'
src = io.open(path, encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
ev = json.loads(m.group(2))

before = len(ev)
e353 = next((e for e in ev if e['id'] == 353), None)
e4615 = next((e for e in ev if e['id'] == 4615), None)
assert e353 and e4615, '対象のエントリが無い'

# ① 両方方式
e353['genre'] = 'musical'
e353['extraGenres'] = ['2.5ji']
print('① id353 genre=musical / extraGenres=["2.5ji"]')

# ② 愛知の枠に御園座の飛び先を焼き込む
burned = 0
for t in e353.get('tickets') or []:
    if '愛知' in (t.get('type') or '') and not t.get('url'):
        t['url'] = MISONO
        burned += 1
        print('② 焼き込み:', t.get('type'))
if burned == 0:
    print('⚠️ 愛知の枠が見つからない（または既にURLがある）＝中止')
    sys.exit(1)

# ③ 4615 を消す
ev = [e for e in ev if e['id'] != 4615]
print('③ id4615 を削除（%d件 → %d件）' % (before, len(ev)))

if not APPLY:
    print('（--apply で適用）')
    sys.exit(0)

io.open('index.html.bak_0913_spyfamily', 'w', encoding='utf-8').write(src)
out = src[:m.start()] + m.group(1) + json.dumps(ev, ensure_ascii=False, indent=2) + m.group(3) + src[m.end():]
io.open(path, 'w', encoding='utf-8').write(out)
print('✅ 適用したわ（backup: index.html.bak_0913_spyfamily）')
