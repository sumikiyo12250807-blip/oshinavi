# -*- coding: utf-8 -*-
"""公演終了組（check_expired の削除候補）を、確認用の直URL付きで一覧化する。
URLは index.html の links から機械抽出のみ（捏造しない）。"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

IDS = [113,406,611,717,813,904,953,1044,1271,1361,1875,2147,2602,2640,2690,2860,3218,3392,3448,3508,3516,3806,4012,4124,4125]
TODAY = "2026-08-16"

raw = open('index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', raw, re.S).group(1))
by = {e['id']: e for e in EVENTS}

for i in IDS:
    e = by.get(i)
    if not e:
        print("id=%s 見つからない" % i); continue
    links = e.get('links') or {}
    url = links.get('pia') or links.get('eplus') or links.get('lawson') or links.get('rakuten') or ""
    site = 'ぴあ' if links.get('pia') else ('e+' if links.get('eplus') else ('ローチケ' if links.get('lawson') else ('楽天' if links.get('rakuten') else '(URL無し)')))
    tks = e.get('tickets') or []
    alive = [t for t in tks if (t.get('date') or '') >= TODAY and not t.get('soldout')]
    so = sum(1 for t in tks if t.get('soldout'))
    print("- **id%s %s**｜%s｜公演日 %s｜枠%d（生き%d・予定枚数終了%d）｜[%s](%s)" % (
        i, (e.get('artist') or e.get('name') or '')[:34], (e.get('venue') or '')[:26],
        e.get('date'), len(tks), len(alive), so, site, url))
    for t in alive:
        print("    ⚠️生き枠: %s | date=%s" % (t.get('type'), t.get('date')))
