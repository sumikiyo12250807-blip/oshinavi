# -*- coding: utf-8 -*-
"""ヒールが出した削除候補を、夜に仕分けやすい形に整理する。

🚨ぴあだけで照合した「0枠」は削除理由にならない（DELETE_GATE 3章）。
   ここでは**消さない**。他社を当てる前に、機械で分かる除外条件を先に外しておく:
     ・他社（e+／楽天／ローチケ）のリンクや枠を持っている
     ・売り切れ/販売終了のフラグが付いている枠がある
     ・saleEndUnknown を持っている
     ・公演日が今日以降
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
        groups['既に消えている'].append((c['id'], c.get('artist') or '', ''))
        continue
    ls = e.get('links') or {}
    urls = [t.get('url') or '' for t in (e.get('tickets') or [])]
    other = [k for k in ('eplus', 'rakuten', 'lawson') if ls.get(k)] \
        + [u for u in urls if u and 'pia.jp' not in u]
    pia = ls.get('pia') or next((u for u in urls if 'pia.jp' in u), '')
    row = (e['id'], e.get('artist') or e.get('name') or '', pia)
    if other:
        groups['他社あり'].append(row)
    elif any(t.get('soldout') or t.get('saleEnded') for t in (e.get('tickets') or [])):
        groups['売切/終了フラグあり'].append(row)
    elif any(t.get('saleEndUnknown') for t in (e.get('tickets') or [])):
        groups['締切不明あり'].append(row)
    else:
        groups['ぴあだけ・要他社確認'].append(row)

with open('tmp/delete_candidates_0910.md', 'w', encoding='utf-8') as f:
    f.write('# %s ヒールが出した削除候補 %d件（**まだ1件も消していない**）\n\n' % (TODAY, len(cands)))
    f.write('ぴあだけで照合した0枠は削除理由にならない（DELETE_GATE 3章）。\n')
    f.write('夜に e+／楽天／ローチケ／主催直販／配信視聴券まで当ててから仕分ける。\n')
    for k in ('他社あり', '売切/終了フラグあり', '締切不明あり', 'ぴあだけ・要他社確認', '既に消えている'):
        rows = groups[k]
        f.write('\n## %s … %d件\n\n' % (k, len(rows)))
        for i, n, u in sorted(rows):
            f.write('- id=%s %s\n' % (i, n[:60]))
            if u:
                f.write('  - %s\n' % u)

print('削除候補 %d件を仕分けたわ → tmp/delete_candidates_0910.md' % len(cands))
for k in groups:
    print('   %-18s %d件' % (k, len(groups[k])))
