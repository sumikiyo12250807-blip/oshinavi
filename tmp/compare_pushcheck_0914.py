# -*- coding: utf-8 -*-
"""push前の独立検証（scratchpad/pushcheck_[AB]_result.json）と index.html の登録値を突き合わせる（読むだけ）。
compare_recheck_0914.py と同じ見方。違うのは読むファイルと、ぴあ以外の枠（e+・楽天）を数えないこと
（エージェントはぴあしか読んでいない＝他社の枠まで比べると必ずズレる）。
使い方: python tmp/compare_pushcheck_0914.py
出力: tmp/compare_pushcheck_0914.md
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
SP = r'C:\Users\user\AppData\Local\Temp\claude\C--Users-user-oshinavi\ada2db76-3770-4399-ab5a-9e566d50214d\scratchpad'
TODAY = datetime.date.today().isoformat()

src = open('index.html', encoding='utf-8').read()
by = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))}


def visible(t):
    if t.get('saleUntilSoldOut') or t.get('soldout'):
        return not t.get('soldout')
    sd, d = t.get('startDate'), t.get('date') or ''
    return not ((not sd or sd <= TODAY) and d < TODAY)


def is_pia(t, e):
    u = t.get('url') or (e.get('links') or {}).get('pia') or ''
    return 'pia.jp' in u or not u


def n(s):
    return re.sub(r'\s+', '', unicodedata.normalize('NFKC', s or '')).replace('>', '/').replace('＞', '/').replace(' ', '/')


GRP = sys.argv[1] if len(sys.argv) > 1 else '*'   # 検証の組（A/B/C/V/S）を1つだけ見る時に渡す
rows = []
for p in sorted(glob.glob(os.path.join(SP, 'pushcheck_%s_result.json' % GRP))):
    rows += json.load(io.open(p, encoding='utf-8'))

OUT = 'tmp/compare_pushcheck_0914%s.md' % ('' if GRP == '*' else '_' + GRP)
out = io.open(OUT, 'w', encoding='utf-8')
W = out.write
W('# push前の独立再導出と登録値の突合（%s）\n\n' % TODAY)
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
    live = [s for s in (r.get('slots') or []) if (s.get('state') or '') in ('受付中', '発売前')]
    vis = [t for t in (e.get('tickets') or []) if visible(t) and is_pia(t, e)]
    if len(live) != len(vis):
        flags.append('枠（ぴあ分） 登録%d／実%d' % (len(vis), len(live)))
    sold = [s for s in (r.get('slots') or []) if (s.get('state') or '') == '予定枚数終了']
    if sold:
        flags.append('実に予定枚数終了 %d枠（登録の売り切れ印 %d）' % (
            len(sold), sum(1 for t in e.get('tickets') or [] if t.get('soldout'))))
    if r.get('note'):
        flags.append('note: %s' % r['note'][:100])
    if flags:
        diff_n += 1
        W('- **id%s %s**\n' % (r['id'], (e.get('name') or '')[:40]))
        for f in flags:
            W('  - %s\n' % f)
W('\n読めた %d件 / ズレあり %d件\n' % (len(rows), diff_n))
out.close()
print('読めた %d件 / ズレあり %d件 → %s' % (len(rows), diff_n, OUT))
