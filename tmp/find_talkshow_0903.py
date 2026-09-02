# -*- coding: utf-8 -*-
"""既存エントリから「トーク主体」の公演を洗い出す（新設 talkshow へ移す候補）。

🚨移してよいのは**トーク・講演そのものが本体**のものだけ。
   上映会/舞台挨拶のオマケのトーク、舞踊＋トーク、ライブ＋トークは移さない
   （その公演の主目的は別にある＝そのタブを探しに来た人の期待から外れる）。
   memory: feedback_genre_pia_asis_and_other／feedback_button_label_matches_result の考え方。
判断は人がするので、ここでは「本体らしい」「オマケらしい」に機械で分けて並べるだけ。
"""
import re, json, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

src = open('index.html', encoding='utf-8', newline='').read()
events = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S).group(2))

TALK = ('トークショー', 'トークイベント', '講演会', '講演', 'トークライブ', '対談')
# トークが「添え物」であることを示す語
SIDE = ('上映', '舞台挨拶', '先行上映', 'プレミア', '完成披露', '公開記念',
        '舞踊', 'コンサート', 'ライブ', 'LIVE', 'リサイタル', '演奏会', '公演記念',
        '発売記念', 'お渡し会', 'サイン会', '握手会', '写真集')

main, side = [], []
for e in events:
    g = e.get('genre')
    if g in ('new', 'talkshow', 'gakusai'):
        continue
    n = (e.get('name') or '') + ' ' + (e.get('title') or '')
    if not any(t in n for t in TALK):
        continue
    (side if any(s in n for s in SIDE) else main).append(e)

print('=== ① トークが本体らしい %d件（talkshow へ移す候補）===' % len(main))
for e in main:
    print('  id%-6d %-9s %s  @%s' % (e['id'], e.get('genre'), (e.get('name') or '')[:44],
                                     (e.get('venue') or '')[:22]))
print()
print('=== ② トークが添え物らしい %d件（移さない＝現状のまま）===' % len(side))
for e in side:
    print('  id%-6d %-9s %s' % (e['id'], e.get('genre'), (e.get('name') or '')[:56]))

json.dump([e['id'] for e in main], open('tmp/talkshow_main_0903.json', 'w'), ensure_ascii=False)
