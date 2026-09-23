# -*- coding: utf-8 -*-
"""まとめ投稿の「他にも◯件あるわ」を機械で数える（2026-09-23 夜）。
X_SCRIPT 3番＝2〜3日後は5件くらい＋残りを丸めた件数。**数は必ず機械で数える**。
丸め方（2026-09-13 ユーザー修正・四捨五入）:
  10未満          … そのままの数「◯件」
  下1桁が0〜4    … 切り下げて「◯件以上」
  下1桁が5〜9    … 切り上げて「◯件近く」
  0件            … 「他にも」の行を書かない
  1件            … 行を書かず、その1件をリストに足す
🚨数えるのは「1行＝1アーティスト」にまとめた後の行数（X_SCRIPT 4番）＝
   同じ名前で同じ時刻の複数県は1行なので、枠数ではなくアーティスト×時刻のユニーク数で数える。
"""
import io
import json
import re
import sys
from collections import defaultdict

sys.path.insert(0, 'tools')
from check_expired import extract_events_array

D2 = '2026-09-25'
D3 = '2026-09-26'

# 各まとめ投稿が受け持つジャンル
POSTS = {
    'post05 アイドル': ['idol'],
    'post06 クラシック・ジャズ': ['classic', 'jazz'],
    'post07 お笑い・落語': ['owarai'],
    'post08 J-POP・ロック': ['jpop', 'rock', 'musicetc', 'enka'],
    'post09 イベント・舞台・映画・スポーツ': ['event', 'kids', 'engeki', 'movie', 'gakusai',
                                            'dinnershow', 'anime', 'fanevent', 'sports', 'musical'],
}


def rough(n):
    if n == 0:
        return '（行を書かない）'
    if n == 1:
        return '（その1件をリストに足す）'
    if n < 10:
        return '他にも%d件あるわ' % n
    base = (n // 10) * 10
    d = n - base
    return '他にも%d件以上あるわ' % base if d <= 4 else '他にも%d件近くあるわ' % (base + 10)


def hhmm(ty):
    m = re.search(r'(\d{1,2}):(\d{2})\s*発売', ty or '')
    return '%02d:%s' % (int(m.group(1)), m.group(2)) if m else '(時刻なし)'


events = extract_events_array('index.html')
# 日付 → ジャンル → 「アーティスト×時刻」のユニーク集合（＝投稿に並ぶ行数）
rows = defaultdict(lambda: defaultdict(set))
for e in events:
    if e.get('genre') == 'new':
        continue
    g = e.get('genre') or '?'
    for t in e.get('tickets') or []:
        if t.get('soldout') or t.get('saleEnded'):
            continue
        if t.get('startDate') not in (D2, D3):
            continue
        key = ((e.get('artist') or e.get('name') or ''), hhmm(t.get('type')))
        rows[t['startDate']][g].add(key)

out = io.open('tmp/x0923/count_rest.txt', 'w', encoding='utf-8')
out.write('# まとめ投稿の「他にも◯件あるわ」（機械で数えた・2026-09-23）\n')
out.write('# 数えているのは「1行＝1アーティスト×時刻」のユニーク行数（X_SCRIPT 4番の形）\n\n')
LISTED = 5   # 各投稿が並べている件数
for name, gs in POSTS.items():
    out.write('## %s（%s）\n' % (name, '+'.join(gs)))
    for d in (D2, D3):
        total = set()
        for g in gs:
            total |= rows[d].get(g, set())
        rest = max(0, len(total) - LISTED)
        out.write('  %s … 全%d行／5件載せる → 残り%d → **%s**\n' % (d, len(total), rest, rough(rest)))
    out.write('\n')
out.close()
print('wrote tmp/x0923/count_rest.txt')
