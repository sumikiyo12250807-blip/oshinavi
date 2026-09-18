# -*- coding: utf-8 -*-
"""ぴあ総ざらい（audit_posts）の「本命」候補を、足し込み／新規の候補リストに割る（2026-09-18 夜）。

🚨「未登録」はeventCdで見ているので、**県＋公演日で登録側に当て直す**
   （[[feedback_existing_entries_miss_new_windows]]）。当たったら足し込み、当たらなければ新規。
🚨 名前が一致する既存があるなら新規にしない＝ツアーは1エントリ（[[feedback_tour_consolidate]]）。
🚫 駐車場だけの売り場は入れない（[[feedback_oshinavi_concept]]）。

  python tmp/x0919/audit_to_cands.py
"""
import io
import json
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')

PARK = re.compile(r'駐車場|駐輪')

h = io.open('index.html', encoding='utf-8', newline='').read()
EV = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))}


def norm(s):
    s = unicodedata.normalize('NFKC', s or '').lower()
    return re.sub(r'[\s　・･,，.。!！?？~〜\-—–_/／\(\)（）\[\]【】「」『』"\'’]', '', s)


byname = {}
for e in EV.values():
    k = norm(e.get('artist') or e.get('name'))
    if k:
        byname.setdefault(k, []).append(e['id'])

txt = io.open('tmp/x0919/audit_posts.txt', encoding='utf-8').read()
sec = txt.split('■ 🎯本命')[1].split('■ ')[0] if '■ 🎯本命' in txt else ''

cur = None
merge, new, skip = {}, {}, []
for ln in sec.split('\n'):
    m = re.match(r'● (.+?)\s+（ぴあのヒット', ln)
    if m:
        cur = m.group(1).strip()
        continue
    mu = re.search(r'(https?://\S+)', ln)
    if not mu or not cur:
        continue
    if PARK.search(cur):
        skip.append(cur)
        continue
    ids = byname.get(norm(cur)) or []
    if ids:
        tgt = sorted(ids)[0]
        d = merge.setdefault(tgt, {'newid': tgt, 'artist': EV[tgt].get('artist') or cur, 'urls': []})
        for u in [(EV[tgt].get('links') or {}).get('pia') or ''] + \
                 [t.get('url') or '' for t in EV[tgt].get('tickets') or []]:
            if u and u not in d['urls']:
                d['urls'].append(u)
        if mu.group(1) not in d['urls']:
            d['urls'].append(mu.group(1))
    else:
        d = new.setdefault(cur, {'newid': 920000 + len(new), 'artist': cur, 'urls': []})
        if mu.group(1) not in d['urls']:
            d['urls'].append(mu.group(1))

io.open('tmp/x0919/cands3_merge.json', 'w', encoding='utf-8').write(
    json.dumps(list(merge.values()), ensure_ascii=False, indent=1))
io.open('tmp/x0919/cands3_new.json', 'w', encoding='utf-8').write(
    json.dumps(list(new.values()), ensure_ascii=False, indent=1))
print('足し込み %d件（URL計%d）／新規 %d件／🚫外した %d件'
      % (len(merge), sum(len(v['urls']) for v in merge.values()), len(new), len(skip)))
for k, v in sorted(merge.items()):
    print('  足し込み id%d %s（URL%d本）' % (k, v['artist'][:28], len(v['urls'])))
for v in new.values():
    print('  新規 %s | %s' % (v['artist'][:40], v['urls'][0]))
