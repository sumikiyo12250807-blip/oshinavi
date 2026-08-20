#!/usr/bin/env python3
"""確実な3組を統合。各ticketに対戦カード/会場＋個別url（renderCardが下部ボタン自動非表示）。

1. 読売ジャイアンツ: 2696←2697,2698（全東京ドーム・全7/25 11:00発売）
2. オリックス: 既存2699←2729（同京セラ・同7/22発売）
3. みなとみらいフェス: 2726←2727（同8/24・同7/19発売・2会場）

2728(神戸/兵庫)は別球場別県で統合しない。しいきアルゲリッチ5件は公演日が広く分散するので分けたまま。
"""
import datetime
import json
import re
import sys
sys.path.insert(0, 'tools')
from build_pia_entries import norm_fw  # stdout UTF-8


def ev_url(cd):
    return f'https://t.pia.jp/pia/event/event.do?eventCd={cd}'


def jp(iso):
    y, m, d = map(int, iso.split('-'))
    return f"{y}年{m}月{d}日({'月火水木金土日'[datetime.date(y,m,d).weekday()]})"


def md(iso):
    _, m, d = iso.split('-')
    return f"{int(m)}/{int(d)}"


h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
by = {e['id']: e for e in EVENTS}

# ---- 1. 読売ジャイアンツ（2696親） ----
# (公演日, 対戦相手, eventCd)
g_games = [
    ('2026-09-12', '対阪神', '2626269'),
    ('2026-09-18', '対中日', '2626271'),
    ('2026-09-19', '対中日', '2626271'),
    ('2026-09-20', '対ヤクルト', '2626272'),
]
g = by[2696]
g['name'] = g['artist'] = '読売ジャイアンツ 公式戦'
g['tickets'] = [{
    'type': f"一般発売（東京 {md(d)}公演 {opp}）7/25 11:00発売",
    'startDate': '2026-07-25', 'date': '2026-07-25', 'url': ev_url(cd),
} for d, opp, cd in g_games]
g['date'] = g_games[-1][0]
g['dateLabel'] = f"{jp(g_games[0][0])}〜{jp(g_games[-1][0])} 東京 東京ドーム"

# ---- 2. オリックス（既存2699に追加） ----
o = by[2699]
o['tickets'].append({
    'type': '一般発売（大阪 9/5公演 対千葉ロッテ）7/22 12:00発売',
    'startDate': '2026-07-22', 'date': '2026-07-22', 'url': ev_url('2627454'),
})
o['tickets'].sort(key=lambda t: re.search(r'(\d+)/(\d+)公演', t['type']).group(0))
# 公演日順(9/4,9/5,9/8,9/12,9/26)にソート
def _mmdd(t):
    mm = re.search(r'(\d+)/(\d+)公演', t['type'])
    return (int(mm.group(1)), int(mm.group(2)))
o['tickets'].sort(key=_mmdd)

# ---- 3. みなとみらいフェス（2726親） ----
f = by[2726]
f['name'] = f['artist'] = '横浜グリーンエクスポ応援 みなとみらいフェスティバル'
f['venue'] = norm_fw('大さん橋会場／日本丸メモリアルパーク')
f['tickets'] = [
    {'type': '一般発売（神奈川 8/24公演 大さん橋会場）7/19 10:00発売',
     'startDate': '2026-07-19', 'date': '2026-07-19', 'url': ev_url('2624911')},
    {'type': '一般発売（神奈川 8/24公演 日本丸メモリアルパーク）7/19 10:00発売',
     'startDate': '2026-07-19', 'date': '2026-07-19', 'url': ev_url('2624912')},
]
f['dateLabel'] = '2026年8月24日(月) 神奈川 大さん橋会場／日本丸メモリアルパーク'

# ---- 吸収エントリを削除 ----
drop = {2697, 2698, 2729, 2727}
EVENTS = [e for e in EVENTS if e['id'] not in drop]

# ---- NEW_ORDER から new側(2729,2727)を除去 ----
h2 = h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():]
mo = re.search(r'(NEW_ORDER\s*=\s*)\[([0-9,\s]*)\]', h2)
order = [int(x) for x in re.findall(r'\d+', mo.group(2)) if int(x) not in {2729, 2727}]
h2 = h2[:mo.start()] + mo.group(1) + '[' + ', '.join(str(i) for i in order) + ']' + h2[mo.end():]

bak = f'index.html.bak_{datetime.date.today():%m%d}_merge3'
open(bak, 'w', encoding='utf-8').write(h)
open('index.html', 'w', encoding='utf-8').write(h2)

print('=== 統合3組 完了 ===')
for i in (2696, 2699, 2726):
    e = by[i]
    print(f"\nid={i} {e['name']} | {e['prefecture']}/{e['venue']} | date={e['date']}")
    print(f"   {e['dateLabel']}")
    for t in e['tickets']:
        print(f"   枠: {t['type']}")
print(f"\n削除: {sorted(drop)} / NEW_ORDER {len(order)}件 / backup {bak}")
