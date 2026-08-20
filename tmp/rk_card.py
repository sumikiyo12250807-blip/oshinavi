import sys, re, html
sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_harvest as R

for u in ('https://ticket.rakuten.co.jp/music/fes/rtax026/',
          'https://ticket.rakuten.co.jp/event/rtvco5z/'):
    body = R.fetch(u)
    print('\n==========', u)
    for m in list(re.finditer(r"<div class='performance( active| hide)?'[^>]*>", body))[:2]:
        seg = body[m.start(): m.start() + 2200]
        print('--- カード生HTML(先頭1800字) ---')
        print(seg[:1800].replace('\n', ' '))
        print()
