# -*- coding: utf-8 -*-
"""3166 真田ナオキLIVE2026 浅草ディスコ の後継URL貼り替え＋実態反映。
旧URL(3489620001-P0030053P02100{1,2})は404。実ページは 3489620002 系に移っており、
10/23・10/24とも「予定枚数終了」＝販売終了ではない（e+実ページで確認 tmp/sanada_urls.txt）。
配信の視聴券が受付中（〜10/29 21:00）なので枠を足す。
  python tmp/fix_3166.py [--apply]
"""
import re, json, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
APPLY = '--apply' in sys.argv

NEW = {'2026-10-20': 'https://eplus.jp/sf/detail/3489620002-P0030053P021001',
       '2026-10-21': 'https://eplus.jp/sf/detail/3489620002-P0030053P021002'}

h = open('index.html', encoding='utf-8').read()
mm = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(mm.group(2))
e = {x['id']: x for x in EVENTS}[3166]

e['links']['eplus'] = 'https://eplus.jp/sf/detail/3489620002-P0030053P021001'
for t in e['tickets']:
    if t.get('date') in NEW:
        t['url'] = NEW[t['date']]
        t['soldout'] = True
        t.setdefault('soldoutSince', TODAY)
        t.pop('saleEnded', None)          # 404で弱いほうに倒したが実ページは予定枚数終了
        t.pop('saleEndedSince', None)

if not any('視聴券' in (t.get('type') or '') for t in e['tickets']):
    e['tickets'].append({
        'type': '配信 視聴券受付（東京 10/23〜10/24公演）〜10/29 21:00',
        'date': '2026-10-29',
        'url': 'https://eplus.jp/sf/detail/3489620003-P0030054P021001',
    })

for t in e['tickets']:
    print(' -', t.get('type'), '|', t.get('date'), '| soldout=', t.get('soldout'), '|', t.get('url'))

if APPLY:
    bak = 'index.html.bak_%s_fix3166' % datetime.date.today().strftime('%m%d')
    open(bak, 'w', encoding='utf-8').write(h)
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    open('index.html', 'w', encoding='utf-8').write(h[:mm.start()] + mm.group(1) + new_arr + mm.group(3) + h[mm.end():])
    print('適用しました (backup: %s)' % bak)
