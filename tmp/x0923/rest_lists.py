# -*- coding: utf-8 -*-
"""まとめ投稿の「2〜3日後」ブロックを、**その投稿のジャンルだけ**で作り直すための一覧（2026-09-23 夜）。
X_SCRIPT 1番＝1投稿＝1ジャンル／3番＝2〜3日後は大物5件＋残りを丸めた件数／4番＝1行＝1アーティスト。
🚨ユーザー指摘「他にもあるわ　だけど、他にどのくらいあるかを書くルールよ　ちゃんと全部読んでから書いて」。
"""
import io
import re
import sys
from collections import defaultdict

sys.path.insert(0, 'tools')
from check_expired import extract_events_array

D2 = '2026-09-25'
D3 = '2026-09-26'
POSTS = {
    'post05 アイドル': ['idol'],
    'post06 クラシック・ジャズ': ['classic', 'jazz'],
    'post07 お笑い・落語': ['owarai'],
    'post08 J-POP・ロック': ['jpop', 'rock', 'musicetc', 'enka'],
    'post09 イベント・舞台・映画・スポーツ': ['event', 'kids', 'engeki', 'movie', 'gakusai',
                                            'dinnershow', 'anime', 'fanevent', 'sports', 'musical'],
}


def rough(n):
    if n <= 0:
        return None
    if n < 10:
        return '他にも%d件あるわ' % n
    base = (n // 10) * 10
    d = n - base
    return '他にも%d件以上あるわ' % base if d <= 4 else '他にも%d件近くあるわ' % (base + 10)


def hhmm(ty):
    m = re.search(r'(\d{1,2}):(\d{2})\s*発売', ty or '')
    return '%02d:%s' % (int(m.group(1)), m.group(2)) if m else '99:99'


events = extract_events_array('index.html')
# (日付, ジャンル) → (アーティスト, 時刻) → 県の集合 ＋ 会場
rows = defaultdict(dict)
for e in events:
    if e.get('genre') == 'new':
        continue
    g = e.get('genre') or '?'
    for t in e.get('tickets') or []:
        if t.get('soldout') or t.get('saleEnded'):
            continue
        d = t.get('startDate')
        if d not in (D2, D3):
            continue
        key = (e.get('artist') or e.get('name') or '', hhmm(t.get('type')))
        rec = rows[(d, g)].setdefault(key, {'pref': set(), 'venue': set()})
        rec['pref'].add(e.get('prefecture') or '')
        rec['venue'].add((e.get('venue') or '')[:34])

out = io.open('tmp/x0923/rest_lists.txt', 'w', encoding='utf-8')
for name, gs in POSTS.items():
    out.write('=== %s（%s）===\n' % (name, '+'.join(gs)))
    for d in (D2, D3):
        merged = {}
        for g in gs:
            for k, v in rows.get((d, g), {}).items():
                m = merged.setdefault(k, {'pref': set(), 'venue': set()})
                m['pref'] |= v['pref']
                m['venue'] |= v['venue']
        items = sorted(merged.items(), key=lambda kv: (kv[0][1], kv[0][0]))
        out.write('--- %s 全%d行 ---\n' % (d, len(items)))
        for (a, t), v in items:
            out.write('  %s %s／%s ｜会場: %s\n' % (t, a[:34], '・'.join(sorted(x for x in v['pref'] if x)),
                                                 '／'.join(sorted(v['venue']))[:52]))
        r = rough(max(0, len(items) - 5))
        out.write('  → 5件載せたときの残り%d件 = %s\n\n' % (max(0, len(items) - 5), r or '（行を書かない）'))
out.close()
print('wrote tmp/x0923/rest_lists.txt')
