# -*- coding: utf-8 -*-
"""公演終了済の削除候補について、index.html から 公演名/会場/公演日/枠状態/URL を機械抽出する。
URLは捏造禁止＝必ず index.html の実データから取る（memory: feedback_delete_candidates_with_url）"""
import json, re, io

IDS = [42,58,99,144,185,222,307,308,314,426,453,665,1117,1145,1179,1559,1743,1745,1876,
       1976,2363,2399,2442,2523,2540,2551,2600,2642,2643,3236,3468,4011,4127,4327,4331]

raw = io.open('index.html', encoding='utf-8').read()
m = re.search(r'const EVENTS\s*=\s*(\[.*?\]);\s*\n', raw, re.S)
events = json.loads(m.group(1))
by_id = {e['id']: e for e in events}

TODAY = '2026-08-17'
for i in IDS:
    e = by_id.get(i)
    if not e:
        print('%d: NOT FOUND' % i); continue
    tks = e.get('tickets') or []
    live = [t for t in tks if not t.get('soldout') and (t.get('date') or '') >= TODAY]
    so = [t for t in tks if t.get('soldout')]
    links = e.get('links') or {}
    url = links.get('pia') or links.get('rakuten') or links.get('eplus') or links.get('lawson') or links.get('official') or ''
    if not url:
        for t in tks:
            if t.get('url'):
                url = t['url']; break
    print('id=%d | %s | %s | 公演日=%s | 枠%d(生きてる%d/売切%d) | %s' % (
        i, e.get('artist',''), e.get('title',''), e.get('date',''), len(tks), len(live), len(so), url))
    for t in tks:
        print('      - %s | date=%s | start=%s | soldout=%s' % (
            t.get('type','')[:60], t.get('date',''), t.get('startDate',''), t.get('soldout')))
