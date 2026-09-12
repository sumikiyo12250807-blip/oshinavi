# -*- coding: utf-8 -*-
"""Xのトレンド8位までの名前を、OSHINAVIの「いま買える枠」に当てる（読むだけ・2026-09-12夜の便）。
いま買える＝枠の締切(date)が今日以降・売り切れでない・発売日(startDate)が今日以前か無い。発売前の枠は別に数える。
振り分け前（genre:new）は出さない＝画面の新着タブにしか出ないため。
使い方: python tmp/x0913/trend_match.py
出力: tmp/x0913/trend_match.txt
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
TODAY = '2026-09-12'
# トレンドの言葉 → 在庫を探す語（トレンドの話題そのものには触れない。名前の一致だけ見る）
KEYS = {
    '#SideM11th_day1': ['SideM', 'アイドルマスター', 'アイマス'],
    'すわほー': ['ヤクルト', 'スワローズ'],
    'うさほー／#giants': ['ジャイアンツ', '巨人'],
    '#グラブルプロフ投稿祭': ['グラブル', 'グランブルー'],
    'ジョバンニ': ['ジョバンニ'],
    '#エヌトワ': ['エヌトワ'],
}
src = io.open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
out = []
for trend, words in KEYS.items():
    out.append('■ %s（%s）' % (trend, '・'.join(words)))
    for e in ev:
        if e.get('genre') == 'new':
            continue
        text = ' '.join([e.get('artist') or '', e.get('name') or '', e.get('venue') or ''])
        if not any(w in text for w in words):
            continue
        live, pre = [], []
        for t in e.get('tickets') or []:
            if t.get('soldout') or (t.get('date') or '') < TODAY:
                continue
            (pre if (t.get('startDate') or '') > TODAY else live).append(t)
        if not live and not pre:
            continue
        out.append('  id%s %s | %s | 買える%d枠・発売前%d枠' % (e['id'], e.get('name'), e.get('dateLabel'), len(live), len(pre)))
        for t in (live + pre)[:6]:
            out.append('     - %s' % t.get('type'))
io.open('tmp/x0913/trend_match.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('→ tmp/x0913/trend_match.txt (%d行)' % len(out))
