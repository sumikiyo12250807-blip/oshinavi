# -*- coding: utf-8 -*-
"""別エージェントがぴあ実ページからゼロで導いた結果（今日の scratchpad/recheck_*_result.json）と
index.html の登録値を突き合わせる（読むだけ）。compare_recheck_0914.py の日付違い＋見るものを足した。

見るもの:
 ①千秋楽＝エージェントの shows の最後の日と、エントリの date（伸ばす向きのズレと縮む向きのズレを分けて書く）
 ②都道府県＝エージェントの shows の県が登録の県に含まれるか
 ③買える／これから発売の枠の数＝エージェント（受付中＋発売前）と、登録の「画面に出る枠」
 ④ジャンル＝エージェントの pia_genre と登録の _piaSub
 ⑤中止・延期・取扱なし・見合わせの枠がある件
 ⑥読めなかった件（note）
使い方: python tmp/compare_recheck_0915.py
出力: tmp/compare_recheck_0915.md
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
SP = r'C:\Users\user\AppData\Local\Temp\claude\C--Users-user-oshinavi\9f3148c0-6b8e-4c5b-9f93-e5e96670181f\scratchpad'
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


def short_pref(p):
    p = p or ''
    if p in ('東京都', '京都府', '大阪府', '北海道'):
        return {'東京都': '東京', '京都府': '京都', '大阪府': '大阪'}.get(p, p)
    return re.sub(r'[県府都]$', '', p)


rows = []
for p in sorted(glob.glob(os.path.join(SP, 'recheck_*_result.json'))):
    rows += json.load(io.open(p, encoding='utf-8'))

out = io.open('tmp/compare_recheck_0915.md', 'w', encoding='utf-8')
W = out.write
W('# 新着の独立再導出と登録値の突合（%s）\n\n' % TODAY)
cnt = {'千秋楽(伸ばす)': 0, '千秋楽(縮む)': 0, '県': 0, '枠': 0, 'ジャンル': 0, '中止等': 0, '読めない': 0}
diff_n = 0
for r in sorted(rows, key=lambda x: x['id']):
    e = by.get(r['id'])
    if not e:
        W('- id%s：エントリが無い\n' % r['id'])
        continue
    flags = []
    shows = r.get('shows') or []
    last = max(((s.get('date_end') or s.get('date') or '') for s in shows), default='')
    if last and last != e.get('date'):
        k = '千秋楽(伸ばす)' if last > (e.get('date') or '') else '千秋楽(縮む)'
        cnt[k] += 1
        flags.append('%s 登録%s／実%s' % (k, e.get('date'), last))
    prefs_e = e.get('prefecture') or ''
    for s in shows:
        pf = short_pref(s.get('pref'))
        if pf and pf not in prefs_e and prefs_e != '全国':
            cnt['県'] += 1
            flags.append('県 登録「%s」に「%s」が無い' % (prefs_e, s.get('pref')))
            break
    slots = r.get('slots') or []
    live = [s for s in slots if (s.get('state') or '') in ('受付中', '発売前')]
    vis = [t for t in (e.get('tickets') or []) if visible(t)]
    if len(live) != len(vis):
        cnt['枠'] += 1
        flags.append('枠 登録%d／実%d' % (len(vis), len(live)))
    bad = [s for s in slots if (s.get('state') or '') in ('中止', '延期', '取扱なし', '見合わせ')]
    if bad:
        cnt['中止等'] += 1
        flags.append('中止等 %s' % ' ／ '.join('%s:%s' % (s.get('state'), (s.get('name') or '')[:30]) for s in bad[:3]))
    pg = n(r.get('pia_genre'))
    ps = n(e.get('_piaSub'))
    if pg and ps and ps not in pg and pg not in ps:
        cnt['ジャンル'] += 1
        flags.append('ジャンル 登録「%s」／実「%s」' % (e.get('_piaSub'), r.get('pia_genre')))
    if r.get('note'):
        cnt['読めない'] += 1
        flags.append('note: %s' % r['note'][:80])
    if flags:
        diff_n += 1
        W('- **id%s %s**（下書き %s）\n' % (r['id'], (e.get('name') or '')[:40], e.get('_genre')))
        for f in flags:
            W('  - %s\n' % f)
W('\n読めた %d件 / ズレあり %d件\n' % (len(rows), diff_n))
W('内訳: ' + ' / '.join('%s %d' % kv for kv in cnt.items()) + '\n')
out.close()
print('読めた %d件 / ズレあり %d件 → tmp/compare_recheck_0915.md' % (len(rows), diff_n))
print('内訳: ' + ' / '.join('%s %d' % kv for kv in cnt.items()))
