# -*- coding: utf-8 -*-
"""ぴあの発売前一覧（音楽 lg=01・先着0102/抽選0202）を全ページ読み、発売日が 2026/9/14 の行を全部出して、
OSHINAVIに同じ eventCd があるか・そのエントリに9/14発売の枠があるかを突き合わせる（読むだけ）。"""
import json, re, sys, time
sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import presale_harvest as PH  # noqa
import urllib.request
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
src = open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
cd2e = {}
for e in ev:
    for u in [(e.get('links') or {}).get('pia') or ''] + [t.get('url') or '' for t in e.get('tickets') or []]:
        for c in re.findall(r'eventCd=(\d+)', u):
            cd2e.setdefault(c, e)
hits = []
for filt in ('rlsStatus=0102', 'rlsStatus=0202'):
    page = 1
    prev = None
    while page < 120:
        url = 'https://t.pia.jp/pia/rlsInfo.do?lg=01&%s&page=%d' % (filt, page)
        h = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read().decode('utf-8', 'replace')
        rows = PH.parse_page(h)
        if rows is None:
            print('presale_harvest に parse_rows が無い'); sys.exit(1)
        sig = [r.get('url') for r in rows]
        if not rows or sig == prev:
            break
        prev = sig
        for r in rows:
            if (r.get('rlsdate') or '').startswith('2026/9/14'):
                hits.append(r)
        page += 1
        time.sleep(0.6)
print('ぴあの音楽で9/14発売の行 %d件' % len(hits))
for r in hits:
    m = re.search(r'eventCd=(\d+)', r['url'])
    e = cd2e.get(m.group(1)) if m else None
    has = e and any(t.get('startDate') == '2026-09-14' for t in e.get('tickets') or [])
    print('  %s %s | %s | %s | %s' % ('✅' if has else ('⚠️登録あり・9/14枠なし' if e else '❌未登録'),
          r.get('artist'), r.get('saletype'), r.get('venue'), ('id%s' % e['id']) if e else r['url']))
