# -*- coding: utf-8 -*-
"""朝に回す「同じ名前が登録済み」の候補を、登録済みエントリと横に並べた見比べ表にする（読むだけ・2026-09-15 夜）
・名前ごとにまとめて、候補（公演日・県・売り場URL）と登録済み（id・名前・会期・会場・ジャンル）を並べる
・「候補の公演日が登録済みの会期の中か外か」を添える＝外なら同じツアーの新しい公演か、別の公演かを見る目安
使い方: python cands_exist_sheet_0915.py → tmp/cands_uk01exist_sheet_0915.txt
"""
import collections
import io
import json
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')


def norm(s):
    s = unicodedata.normalize('NFKC', s or '').lower()
    return re.sub(r'[\s　・･,，.。!！?？~〜\-—–_/／\(\)（）\[\]【】「」『』"\']', '', s)


def perf_days(s):
    return ['%s-%02d-%02d' % (y, int(m), int(d)) for y, m, d in re.findall(r'(\d{4})/(\d{1,2})/(\d{1,2})', s or '')]


cands = json.load(io.open('tmp/cands_uk01night_0915.json', encoding='utf-8'))
src = io.open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
by_name = collections.defaultdict(list)
for e in ev:
    for k in {norm(e.get('artist')), norm(e.get('name'))}:
        if k:
            by_name[k].append(e)
g = collections.OrderedDict()
for c in cands:
    k = norm(c['artist'])
    if k in by_name:
        g.setdefault(k, []).append(c)

out, n_in, n_out = [], 0, 0
for k, cs in g.items():
    es = {e['id']: e for e in by_name[k]}.values()
    out.append('■ %s（候補 %d件／登録済み %d件）' % (cs[0]['artist'], len(cs), len(es)))
    for e in es:
        out.append('   登録済み id%s｜%s｜%s｜%s｜%s' % (e['id'], (e.get('name') or '')[:30], e.get('dateLabel') or e.get('date'), (e.get('venue') or '')[:30], e.get('genre')))
    firsts = [min([e.get('date') or ''] + [t.get('date') or '' for t in e.get('tickets') or []]) for e in es]
    lo, hi = min(firsts or ['']), max([e.get('date') or '' for e in es] or [''])
    for c in cs:
        days = perf_days(c.get('_perfdate'))
        inside = bool(days) and all(lo <= d <= hi for d in days)
        n_in += inside
        n_out += not inside
        out.append('   候補 %s｜%s｜%s｜登録済みの会期の%s' % (c.get('_perfdate'), c.get('_pref'), c['urls'][0], '中' if inside else '外'))
    out.append('')
io.open('tmp/cands_uk01exist_sheet_0915.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('名前 %d種類・候補 %d件（登録済みの会期の中 %d件／外 %d件）→ tmp/cands_uk01exist_sheet_0915.txt' % (len(g), sum(len(v) for v in g.values()), n_in, n_out))
