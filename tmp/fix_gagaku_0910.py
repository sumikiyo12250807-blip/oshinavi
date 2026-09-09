# -*- coding: utf-8 -*-
"""雅楽の2件が enka（演歌）に落ちていたのを hougaku に直す。

ぴあの区分は「音楽/演歌・邦楽」＝演歌と邦楽が同居した箱で、
**どちらに割るかはうちの側のロジック（build_pia_entries の HOGAKU_RE）が決めている**。
その語彙に雅楽の団体名・楽器名が無くて演歌側に落ちていた＝ぴあの写し間違いではない。

[[feedback_dento_split_music_stage]] の表＝**雅楽は hougaku（演奏を聴きに行くもの）**。

  id7520 天王寺楽所雅亮会 … 四天王寺の雅楽・天王寺舞楽の伝承団体（重要無形民俗文化財）
      https://t.pia.jp/pia/event/event.do?eventCd=2631205
  id7625 東儀秀樹／東儀典親 … 篳篥の雅楽師
      https://t.pia.jp/pia/event/event.do?eventCd=2628490

恒久策として HOGAKU_RE に「楽所|雅亮|舞楽|篳篥|龍笛|竜笛|笏拍子|東儀」を足した（同日）。
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
FIX = {7520: 'hougaku', 7625: 'hougaku'}

src = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))

for e in events:
    if e['id'] in FIX:
        assert '演歌' in (e.get('_piaSub') or ''), 'id%s のぴあ区分が演歌・邦楽でない' % e['id']
        print('id=%s %s : _genre %s → %s' % (e['id'], e['name'][:30], e.get('_genre'), FIX[e['id']]))
        e['_genre'] = FIX[e['id']]

if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)

arr = json.dumps(events, ensure_ascii=False, indent=2)
open('index.html', 'w', encoding='utf-8').write(src[:m.start()] + m.group(1) + arr + m.group(3) + src[m.end():])
print('書き込み完了')
