# -*- coding: utf-8 -*-
"""登録に出てくる楽天ページ43本を実際に引いて、
   「販売期間に終わりが書いてあるか」を1本ずつ確かめる。

書いていない枠に締切が付いていたら、それは build_rakuten_entries.py の180行目
  if not ed and card_end: ed, et = card_end[:10], card_end[11:16]
で **公演カードの販売終了日時の最大値を流用した嘘** の疑い。
"""
import io, json, re, sys, time
sys.path.insert(0, 'tools')
from rakuten_harvest import fetch, parse_page, win_dates
sys.stdout.reconfigure(encoding='utf-8')

urls = json.load(io.open('tmp/rakuten_urls_0909.json', encoding='utf-8'))
out = []
for n, (u, ids) in enumerate(urls.items(), 1):
    rec = {'url': u, 'ids': ids}
    try:
        body = fetch(u)
        r = parse_page(u, body)
        wins = []
        for w in r.get('windows') or []:
            f, t = win_dates(w.get('timming') or '')
            wins.append({'type': w.get('type'), 'from': f, 'to': t,
                         'timming': (w.get('timming') or '').strip()})
        rec['windows'] = wins
        rec['終わりが書かれていない枠'] = [w['type'] for w in wins if not w['to']]
        rec['shape'] = r.get('shape')
    except Exception as ex:
        rec['error'] = '%s: %s' % (type(ex).__name__, ex)
    out.append(rec)
    sys.stderr.write('[%d/%d] %s\n' % (n, len(urls), u))
    time.sleep(1.0)

json.dump(out, io.open('tmp/rakuten_ends_0909.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

ng = [r for r in out if r.get('終わりが書かれていない枠')]
er = [r for r in out if r.get('error')]
print('引いたページ %d本 / 取得失敗 %d本' % (len(out), len(er)))
print('🚨「販売期間に終わりが書かれていない枠」を持つページ = %d本' % len(ng))
for r in ng:
    print('  %s  id=%s  枠: %s' % (r['url'], r['ids'], '／'.join(r['終わりが書かれていない枠'])))
for r in er:
    print('  ❌取得失敗 %s  %s' % (r['url'], r['error']))
