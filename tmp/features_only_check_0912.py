# -*- coding: utf-8 -*-
"""特設ページからしか辿れなかった164本を引いて、発売前／販売中／過去に分ける。

入口の穴（static_event-sitemap の特設ページ849本を見ていなかった）の実害を数える。
売り状態は rakuten_perf_status（購入ボタンのAJAX）で取る＝売り切れを発売前と数えない。
"""
import io
import json
import sys
import time

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_harvest as RH
import rakuten_perf_status as PS
import rakuten_presale_harvest as H

urls = json.load(io.open('tmp/features_only_urls_0912.json', encoding='utf-8'))
out = {'presale': [], 'onsale': [], 'soldout': [], 'past': [], 'error': []}
for i, u in enumerate(urls, 1):
    if not u.endswith('/'):
        u = u + '/'
    try:
        rec = RH.parse_page(u, RH.fetch(u))
    except Exception as ex:
        out['error'].append({'url': u, 'why': repr(ex)[:70]})
        continue
    if not rec.get('name') or not rec.get('perfs'):
        out['error'].append({'url': u, 'why': '公演が読めない形式'})
        continue
    rows = []
    try:
        r = PS.perf_status(u)
        rows = r['rows'] if r.get('ok') else []
    except Exception:
        rows = []
    kind, presale, _ = H.classify(rec, rows)
    out[kind].append({
        'url': u, 'name': rec['name'], '_genre': rec.get('_genre'),
        'perfs': len(rec['perfs']),
        'first': min(p['date'] for p in rec['perfs']),
        'last': max((p.get('end') or p['date']) for p in rec['perfs']),
        'presale_windows': [{'type': w.get('type'), 'timming': w.get('timming')} for w in presale],
        'windows': [{'type': w.get('type'), 'timming': w.get('timming')} for w in rec['windows']],
        'status_rows': [{'date': c['date'], 'time': c['time'], 'status': c['status'],
                         'buy_url': c.get('buy_url', '')} for c in rows],
    })
    if i % 25 == 0:
        sys.stderr.write('  [%d/%d] 発売前%d 販売中%d 売切%d 過去%d 読めない%d\n'
                         % (i, len(urls), len(out['presale']), len(out['onsale']),
                            len(out['soldout']), len(out['past']), len(out['error'])))
    time.sleep(0.4)

json.dump(out, io.open('tmp/features_only_result_0912.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('見たページ %d件' % len(urls))
print('  🎯これから発売 %d件' % len(out['presale']))
print('  販売中       %d件' % len(out['onsale']))
print('  売り切れのみ  %d件' % len(out['soldout']))
print('  過去公演     %d件' % len(out['past']))
print('  読めない     %d件' % len(out['error']))
print('→ tmp/features_only_result_0912.json')
