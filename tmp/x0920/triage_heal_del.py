# -*- coding: utf-8 -*-
"""ヒールが出した「買える枠ゼロ」候補を仕分ける（読むだけ・2026-09-14）。triage_delete_candidates_0912.py の日付違い。

🚨ぴあだけで照合した「0枠」は削除理由にならない（DELETE_GATE 3章）。ここでは**消さない**。
   機械で分かる除外条件を先に外し、「ぴあだけ・要他社確認」を mark_soldout／他社確認に回す:
     ・他社（e+／楽天／ローチケ）のリンクや枠を持っている
     ・売り切れ/販売終了のフラグが付いている枠がある
     ・saleEndUnknown を持っている
使い方: python tmp/triage_delete_candidates_0920.py
出力: tmp/delete_candidates_0920.md ＋ tmp/delete_candidates_piaonly_0920.txt（idのカンマ区切り）
"""
import datetime
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()

heal = json.load(open('tmp/heal_stale.json', encoding='utf-8'))
cands = [h for h in heal if h.get('status') == 'delete']

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
by = {e['id']: e for e in json.loads(m.group(2))}

groups = {'他社あり': [], '売切/終了フラグあり': [], '締切不明あり': [],
          'ぴあだけ・要他社確認': [], '既に消えている': []}
for c in cands:
    e = by.get(c['id'])
    if not e:
        groups['既に消えている'].append((c['id'], c.get('artist') or '', '', ''))
        continue
    ls = e.get('links') or {}
    urls = [t.get('url') or '' for t in (e.get('tickets') or [])]
    other = [k for k in ('eplus', 'rakuten', 'lawson') if ls.get(k)] \
        + [u for u in urls if u and 'pia.jp' not in u]
    pia = ls.get('pia') or next((u for u in urls if 'pia.jp' in u), '')
    row = (e['id'], e.get('artist') or e.get('name') or '', pia, e.get('date') or '')
    if other:
        groups['他社あり'].append(row)
    elif any(t.get('soldout') or t.get('saleEnded') for t in (e.get('tickets') or [])):
        groups['売切/終了フラグあり'].append(row)
    elif any(t.get('saleEndUnknown') for t in (e.get('tickets') or [])):
        groups['締切不明あり'].append(row)
    else:
        groups['ぴあだけ・要他社確認'].append(row)

with open('tmp/delete_candidates_0920.md', 'w', encoding='utf-8') as f:
    f.write('# %s ヒールが出した「買える枠ゼロ」%d件（**まだ1件も消していない**）\n\n' % (TODAY, len(cands)))
    f.write('ぴあだけで照合した0枠は削除理由にならない（DELETE_GATE 3章）。売り切れかどうかを mark_soldout で見る。\n')
    for k in ('他社あり', '売切/終了フラグあり', '締切不明あり', 'ぴあだけ・要他社確認', '既に消えている'):
        rows = groups[k]
        f.write('\n## %s … %d件\n\n' % (k, len(rows)))
        for i, n, u, d in sorted(rows):
            f.write('- id=%s %s（公演 %s）\n' % (i, n[:60], d))
            if u:
                f.write('  - %s\n' % u)
open('tmp/delete_candidates_piaonly_0920.txt', 'w', encoding='utf-8').write(
    ','.join(str(r[0]) for r in sorted(groups['ぴあだけ・要他社確認'])))
print('買える枠ゼロ %d件を仕分けた → tmp/delete_candidates_0920.md' % len(cands))
for k in groups:
    print('   %-18s %d件' % (k, len(groups[k])))
