# -*- coding: utf-8 -*-
"""lastmod が古い楽天URLに、まだ生きている公演がどれだけ混ざっているかを抜き取りで測る。
＝「27,105件を全部舐める価値があるか」を数字で決めるため。
使い方: python tmp/rakuten_old_probe_0909.py [抜き取り件数(既定60)]
"""
import sys, os, re, random, datetime, collections
os.chdir(r'C:\Users\user\oshinavi')
sys.path.insert(0, 'tools')
import rakuten_harvest as rh
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

N = int(sys.argv[1]) if len(sys.argv) > 1 else 60
TODAY = datetime.date.today().isoformat()

idx = rh.fetch(rh.SITEMAP)
maps = [u for u in re.findall(r'<loc>([^<]+)</loc>', idx)
        if 'post-sitemap' in u or 'static_event' in u]
rows = {}
for mu in maps:
    try:
        b = rh.fetch(mu)
    except Exception:
        continue
    for m in re.finditer(r'<url>\s*<loc>([^<]+)</loc>\s*(?:<lastmod>([^<]+)</lastmod>)?', b, re.S):
        rows[m.group(1)] = (m.group(2) or '')[:10]

old = [u for u, d in rows.items() if d and d < '2026-06-11']
print('lastmodが90日より古いURL: %d件' % len(old))
random.seed(20260909)
sample = random.sample(old, min(N, len(old)))
c = collections.Counter()
alive_ex = []
for u in sample:
    try:
        rec = rh.parse_page(u, rh.fetch(u))
    except Exception:
        c['取得失敗'] += 1; continue
    ok, why = rh.alive(rec)
    if ok:
        c['まだ買える'] += 1
        alive_ex.append((rec.get('name', '')[:36], u))
    else:
        c[why or '買えない'] += 1
print('\n抜き取り %d件の内訳' % len(sample))
for k, v in c.most_common():
    print('   %-28s %d (%.0f%%)' % (k, v, 100.0 * v / len(sample)))
print('\nまだ買えるページの例:')
for n, u in alive_ex[:10]:
    print('   %-36s %s' % (n, u))
