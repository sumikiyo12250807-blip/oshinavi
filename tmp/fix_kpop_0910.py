# -*- coding: utf-8 -*-
"""ぴあ区分「音楽/海外ROCK・POPS」の韓国アーティストを kpop に読み替える。

[[feedback_kpop_vs_yougaku]]＝ぴあに K-POP の区分が無いので韓国勢は全部この箱に落ちる。
読み替えるのは**この区分のときだけ**（音楽その他などは広げない）。

裏取り（2026-09-10）:
  id7602 BOYNEXTDOOR … KOZ ENTERTAINMENT（HYBE傘下）の韓国6人組
      https://kozofficial.com/artist/profile/BOYNEXTDOOR
  id7513 KIRARA … ソウル拠点の韓国のエレクトロニックミュージシャン（FUJI ROCK '26 出演）
      https://www.billboard-japan.com/d_news/detail/165301
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
FIX = {7513: 'kpop', 7602: 'kpop'}

src = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))

n = 0
for e in events:
    if e['id'] in FIX:
        assert '海外ROCK' in (e.get('_piaSub') or ''), 'id%s のぴあ区分が海外ROCK・POPSでない' % e['id']
        print('id=%s %s : _genre %s → %s' % (e['id'], e['name'][:30], e.get('_genre'), FIX[e['id']]))
        e['_genre'] = FIX[e['id']]
        n += 1

if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)

arr = json.dumps(events, ensure_ascii=False, indent=2)
open('index.html', 'w', encoding='utf-8').write(src[:m.start()] + m.group(1) + arr + m.group(3) + src[m.end():])
print('%d件を書き換えたわ' % n)
