# -*- coding: utf-8 -*-
"""楽天チケットに「これから発売（発売前）」の公演がどれだけあるかを実測する。

やること
 ① sitemap から全公演URLと lastmod を集めて、更新の新しさ別に件数を出す（ここは軽い）
 ② 新しい順に N 件だけ実ページを読んで、
    「発売前の販売枠（開始が未来）を持つページ」が何%あるかを測る
 ③ そのうち OSHINAVI に未登録のものを出す
使い方: python tmp/rakuten_presale_probe_0909.py [調べるページ数(既定120)]
"""
import sys, os, re, json, io, datetime, collections
os.chdir(r'C:\Users\user\oshinavi')
sys.path.insert(0, 'tools')
import rakuten_harvest as rh
from check_expired import extract_events_array
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

N = int(sys.argv[1]) if len(sys.argv) > 1 else 120
TODAY = datetime.date.today().isoformat()

# ① sitemap
idx = rh.fetch(rh.SITEMAP)
maps = [u for u in re.findall(r'<loc>([^<]+)</loc>', idx)
        if 'post-sitemap' in u or 'static_event' in u]
rows = []
for mu in maps:
    try:
        b = rh.fetch(mu)
    except Exception:
        continue
    for m in re.finditer(r'<url>\s*<loc>([^<]+)</loc>\s*(?:<lastmod>([^<]+)</lastmod>)?', b, re.S):
        rows.append((m.group(1), (m.group(2) or '')[:10]))
rows = list({u: (u, d) for u, d in rows}.values())
print('sitemapの公演URL: %d件' % len(rows))
c = collections.Counter()
for u, d in rows:
    if not d:
        c['lastmod無し'] += 1; continue
    age = (datetime.date.fromisoformat(TODAY) - datetime.date.fromisoformat(d)).days
    for k, lim in (('7日以内', 7), ('30日以内', 30), ('90日以内', 90), ('それより古い', 10 ** 9)):
        if age <= lim:
            c[k] += 1; break
for k in ('7日以内', '30日以内', '90日以内', 'それより古い', 'lastmod無し'):
    print('   %-10s %d' % (k, c[k]))

# ② 新しい順に N 件を実ページで見る
rows = [r for r in rows if r[1]]
rows.sort(key=lambda r: r[1], reverse=True)
target = rows[:N]
have = set()
for e in extract_events_array('index.html'):
    for v in (e.get('links') or {}).values():
        if v and ('rakuten' in v or 'linksynergy' in v):
            mm = re.search(r'(?:ticket\.rakuten\.co\.jp|%2F)([^/%]+)%?2?F?$', v)
            have.add(v)
have_ids = set()
for v in have:
    for m in re.finditer(r'/([a-z0-9]{5,10})/?$|%2F([a-z0-9]{5,10})%2F$', v):
        have_ids.add((m.group(1) or m.group(2)))

print('\n新しい順に %d ページを実際に読む…' % len(target))
pre, sell, dead, err = [], 0, 0, 0
for i, (u, d) in enumerate(target, 1):
    try:
        rec = rh.parse_page(u, rh.fetch(u))
    except Exception:
        err += 1; continue
    if not rec or not rec.get('windows'):
        dead += 1; continue
    fut = False
    for w in rec['windows']:
        f, t = rh.win_dates(w['timming'])
        if f and f[:10] > TODAY:
            fut = True
    if fut:
        code = u.rstrip('/').split('/')[-1]
        pre.append((u, rec.get('name', '')[:38], code in have_ids))
    else:
        sell += 1
print('\n発売前の枠を持つページ: %d件 / 販売中だけ: %d件 / 枠が読めない: %d件 / 取得失敗: %d件'
      % (len(pre), sell, dead, err))
print('\n■ 発売前を持つページ（✅=登録済み ／ 🆕=未登録）')
for u, n, known in pre:
    print('   %s %-38s %s' % ('✅' if known else '🆕', n, u))
