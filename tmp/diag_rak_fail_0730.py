# -*- coding: utf-8 -*-
"""reconcile_rakuten が FAIL を出した既存4件を、生HTMLの一次情報で診断する。
（WebFetchは楽天を「販売終了」と誤読するので使わない）"""
import json
import re
import sys

sys.path.insert(0, 'tools')
import rakuten_harvest as R

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EV = json.loads(m.group(2))
byid = {e['id']: e for e in EV}


def raw_url(u):
    mm = re.search(r'murl=([^&]+)', u or '')
    if mm:
        import urllib.parse
        return urllib.parse.unquote(mm.group(1))
    return u


out = []
for i in (5, 6, 1768, 3220):
    e = byid[i]
    out.append(f"===== id={i}  {e.get('artist')} =====")
    out.append(f"  venue={e.get('venue')}")
    out.append(f"  date={e.get('date')}  dateLabel={e.get('dateLabel')}")
    out.append('  --- 登録枠 ---')
    for t in e.get('tickets') or []:
        out.append(f"    {t.get('type')}  [date={t.get('date')} start={t.get('startDate')} unknownEnd={t.get('saleEndUnknown')} sold={t.get('saleUntilSoldOut')}]")
    urls = [raw_url((e.get('links') or {}).get('rakuten'))]
    for t in e.get('tickets') or []:
        u = raw_url(t.get('url') or '')
        if u and u not in urls:
            urls.append(u)
    for u in urls:
        out.append(f'  --- ページ {u} ---')
        try:
            b = R.fetch(u)
        except Exception as ex:
            out.append(f'    取得失敗 {ex}')
            continue
        for p in R.parse_perfs(b):
            out.append(f"    公演: date={p.get('date')} end={p.get('end')} pref={p.get('pref')} venue={p.get('venue')} status={p.get('status')}")
            out.append(f"          sale_start={p.get('sale_start')} sale_end={p.get('sale_end')}")
        for w in R.parse_windows(b):
            f, t2 = R.win_dates(w['timming'])
            out.append(f"    枠: {w['type']} | {w['timming']} | status={w['status']} → 開始{f} 終了{t2}")
    out.append('')

open('tmp/diag_rak_fail_0730.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('wrote tmp/diag_rak_fail_0730.txt')
