# -*- coding: utf-8 -*-
"""別エージェントがぴあ実ページからゼロで導いた結果（scratchpad/recheck_[AB]_result.json）と
index.html の登録値を突き合わせる（読むだけ）。

見るもの:
 ①公演日の最終日（千秋楽）＝エントリの date と一致するか
 ②都道府県＝エージェントの shows の県が登録の県に含まれるか
 ③買える／これから発売の枠の数＝エージェント（受付中＋発売前）と、登録の「画面に出る枠」
 ④ジャンル＝エージェントの pia_genre と登録の _piaSub
 ⑤読めなかった件（note）
使い方: python tmp/compare_recheck_0911.py
出力: tmp/compare_recheck_0912.md
"""
import datetime
import glob
import io
import json
import os
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')
SP = r'C:\Users\user\AppData\Local\Temp\claude\C--Users-user-oshinavi\0fc1d2b7-fccb-457b-879f-7aec070e018d\scratchpad'
TODAY = datetime.date.today().isoformat()

src = open('index.html', encoding='utf-8').read()
m = re.search(r'  const EVENTS = (\[.*?\]);', src, re.S)
by = {e['id']: e for e in json.loads(m.group(1))}


def visible(t):
    if t.get('saleUntilSoldOut') or t.get('soldout'):
        return not t.get('soldout')  # 売り切れは「買える」には数えない
    sd, d = t.get('startDate'), t.get('date') or ''
    return not ((not sd or sd <= TODAY) and d < TODAY)


def n(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'\s+', '', s).replace('>', '/').replace('＞', '/')


rows = []
for p in sorted(glob.glob(os.path.join(SP, 'recheck_*_result.json'))):
    rows += json.load(io.open(p, encoding='utf-8'))

out = io.open('tmp/compare_recheck_0912.md', 'w', encoding='utf-8')
W = out.write
W('# 新着の独立再導出と登録値の突合（%s）\n\n' % TODAY)
diff_n = 0
for r in sorted(rows, key=lambda x: x['id']):
    e = by.get(r['id'])
    if not e:
        W('- id%s：エントリが無い\n' % r['id'])
        continue
    flags = []
    shows = r.get('shows') or []
    last = max((s.get('date') or '' for s in shows), default='')
    if last and last != e.get('date'):
        flags.append('千秋楽 登録%s／実%s' % (e.get('date'), last))
    prefs_e = e.get('prefecture') or ''
    for s in shows:
        pf = (s.get('pref') or '').replace('県', '').replace('府', '').replace('都', '') if s.get('pref') not in ('東京都', '京都府', '大阪府', '北海道') else s.get('pref')
        pf = {'東京都': '東京', '京都府': '京都', '大阪府': '大阪'}.get(pf, pf)
        if pf and pf not in prefs_e and prefs_e != '全国':
            flags.append('県 登録「%s」に「%s」が無い' % (prefs_e, s.get('pref')))
            break
    live = [s for s in (r.get('slots') or []) if (s.get('state') or '') in ('受付中', '発売前')]
    vis = [t for t in (e.get('tickets') or []) if visible(t)]
    if len(live) != len(vis):
        flags.append('枠 登録%d／実%d' % (len(vis), len(live)))
    pg = n(r.get('pia_genre'))
    ps = n(e.get('_piaSub'))
    if pg and ps and ps not in pg and pg not in ps:
        flags.append('ジャンル 登録「%s」／実「%s」' % (e.get('_piaSub'), r.get('pia_genre')))
    if r.get('note'):
        flags.append('note: %s' % r['note'][:80])
    if flags:
        diff_n += 1
        W('- **id%s %s**\n' % (r['id'], (e.get('name') or '')[:40]))
        for f in flags:
            W('  - %s\n' % f)
W('\n読めた %d件 / ズレあり %d件\n' % (len(rows), diff_n))
out.close()
print('読めた %d件 / ズレあり %d件 → tmp/compare_recheck_0912.md' % (len(rows), diff_n))
