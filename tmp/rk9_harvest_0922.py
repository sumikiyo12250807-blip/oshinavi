# -*- coding: utf-8 -*-
"""楽天 post-sitemap で「販売中」なのに楽天URLが index.html に無かった9本だけを rakuten_harvest の形で読む。
既存の名前一致で捨てず、全部読んで「名前が既存にあるか」を印にして残す（足し込み先の判断材料）。"""
import importlib.util, io, json, re, sys, time
sys.path.insert(0, 'tools')
spec = importlib.util.spec_from_file_location('rh', 'tools/rakuten_harvest.py')
RH = importlib.util.module_from_spec(spec)
spec.loader.exec_module(RH)
sys.stdout.reconfigure(encoding='utf-8')

URLS = [
    'https://ticket.rakuten.co.jp/music/jpop/idle/rtyu133/',
    'https://ticket.rakuten.co.jp/music/jpop/idle/rtyu029/',
    'https://ticket.rakuten.co.jp/music/fes/rtax918/',
    'https://ticket.rakuten.co.jp/music/jpop/rtol267/',
    'https://ticket.rakuten.co.jp/music/jpop/idle/rtbc021/',
    'https://ticket.rakuten.co.jp/event/rtkt926/',
    'https://ticket.rakuten.co.jp/event/matsuri/rtg2672/',
    'https://ticket.rakuten.co.jp/music/rtol238/',
    'https://ticket.rakuten.co.jp/event/rtck026/',
]
src = io.open('index.html', encoding='utf-8').read()
EV = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
names = {}
for e in EV:
    for k in (e.get('name'), e.get('artist')):
        if k:
            names.setdefault(RH.norm_name(k), []).append(e['id'])
out = []
for u in URLS:
    body = RH.fetch(u)
    rec = RH.parse_page(u, body)
    ok, why = RH.alive(rec)
    rec['rakuten_deeplink'] = RH.deeplink(u)
    rec['_same_name_ids'] = names.get(RH.norm_name(rec.get('name')), [])
    print('%s | %s | 公演%d 枠%d | alive=%s %s | 既存名 %s' % (u[-9:], (rec.get('name') or '')[:36], len(rec.get('perfs') or []),
                                                       len(rec.get('windows') or []), ok, why or '', rec['_same_name_ids']))
    if ok:
        out.append(rec)
    time.sleep(1.5)
json.dump(out, io.open('tmp/rakuten_rk9_0922.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('→ tmp/rakuten_rk9_0922.json', len(out))
