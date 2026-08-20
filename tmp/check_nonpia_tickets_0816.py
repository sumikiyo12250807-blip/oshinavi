# -*- coding: utf-8 -*-
"""soldout候補25件のうち、ぴあ以外の売り手の枠（ticket.url がe+/ローチケ/楽天）を持つエントリを洗い出す。
mark_soldout --apply はエントリ内の生きた枠を一括でsoldoutにするので、
ぴあ以外で売っている枠を巻き込む恐れがある（feedback_saleended_vs_soldout）。"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

IDS = [130,1071,2223,2341,2401,2415,2416,2815,2882,2916,2997,3287,3432,3513,3594,3649,3651,3743,3766,3872,3875,3899,3912,3922,3931,3937,4095,4319,4326,4327]
TODAY = "2026-08-16"

raw = open('index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', raw, re.S).group(1))

def host(u):
    if not u: return ""
    m = re.match(r'https?://([^/]+)', u)
    return m.group(1) if m else u[:30]

for e in EVENTS:
    if e.get('id') not in IDS:
        continue
    rows = []
    for t in e.get('tickets') or []:
        d, sd = t.get('date') or '', t.get('startDate')
        expired = d < TODAY and not (sd and sd == d)
        rows.append((host(t.get('url')), d, bool(t.get('soldout')), expired, (t.get('type') or '')[:44]))
    nonpia = [r for r in rows if r[0] and 'pia.jp' not in r[0]]
    alive_nonpia = [r for r in nonpia if not r[3] and not r[2]]
    flag = "🚨要除外" if alive_nonpia else ""
    print("id=%-5s links=%s %s" % (e['id'], ",".join(k for k, v in (e.get('links') or {}).items() if v), flag))
    for h_, d, so, ex, ty in rows:
        print("    [%s] date=%s soldout=%s 満了=%s %s" % (h_ or "(links継承)", d, so, ex, ty))
