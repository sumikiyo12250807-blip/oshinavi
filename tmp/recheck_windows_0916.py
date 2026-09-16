# -*- coding: utf-8 -*-
"""読み直しで「枠 登録N／実M」と出た id を、公演日ごとのカードでなく「券種名＋締切」の組で数え直す（読むだけ・2026-09-16）。
エージェントはぴあの公演カードを1枚ずつ数える。登録は同じ券種・同じ締切の枠を1つのバッジにまとめる（build_pia_entries の形）。
使い方: python tmp/recheck_windows_0916.py 10443,10444,...
出力: 登録の画面に出る枠数 ／ 実の受付中・発売前の（券種名, 締切）の組の数 ／ 登録に無い締切
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
SP = r'C:\Users\user\AppData\Local\Temp\claude\C--Users-user-oshinavi\166bfbc5-2524-465f-aba5-b0b622c14861\scratchpad'
TODAY = datetime.date.today().isoformat()
ids = [int(x) for x in sys.argv[1].split(',')]
src = io.open('index.html', encoding='utf-8').read()
by = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))}
rows = {}
for p in glob.glob(os.path.join(SP, 'recheck_*_result.json')):
    for r in json.load(io.open(p, encoding='utf-8')):
        rows[r['id']] = r


def n(s):
    s = unicodedata.normalize('NFKC', s or '')
    s = re.sub(r'\s*／.*$', '', s)          # 「券種名 ／ 公演名」の公演名を落とす
    return re.sub(r'[\s.．。]+', '', s)


def visible(t):
    if t.get('saleUntilSoldOut') or t.get('soldout'):
        return not t.get('soldout')
    sd, d = t.get('startDate'), t.get('date') or ''
    return not ((not sd or sd <= TODAY) and d < TODAY)


def mdhm(s):
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})(?:\s+(\d{1,2}:\d{2}))?', s or '')
    return ('%d/%d %s' % (int(m.group(2)), int(m.group(3)), m.group(4) or '')).strip() if m else ''


for i in ids:
    e, r = by.get(i), rows.get(i)
    if not e or not r:
        print('id%d：登録か読み直しが無い' % i)
        continue
    vis = [t for t in e.get('tickets') or [] if visible(t)]
    live = [s for s in r.get('slots') or [] if s.get('state') in ('受付中', '発売前')]
    wins = {(n(s.get('name')), s.get('sale_end') or '', s.get('state')) for s in live}
    reg_ends = {re.search(r'〜((?:R\d+年\s*)?\d{1,2}/\d{1,2}(?:\s+\d{1,2}:\d{2})?)', t.get('type') or '') for t in vis}
    reg_ends = {m.group(1) for m in reg_ends if m}
    miss = sorted({mdhm(w[1]) for w in wins if w[1] and mdhm(w[1]) not in reg_ends})
    mark = '＝' if len(wins) == len(vis) else '≠'
    print('id%d %s ｜ 登録%d %s 実の組%d（カード%d）%s' % (
        i, e['name'][:26], len(vis), mark, len(wins), len(live), ('｜ 登録に無い締切 ' + '・'.join(miss)) if miss else ''))
