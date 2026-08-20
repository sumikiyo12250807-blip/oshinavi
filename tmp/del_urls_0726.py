# -*- coding: utf-8 -*-
"""削除候補のid→公演名・購入URLを index.html から機械抽出（捏造禁止）"""
import sys, io, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ENDED = [363, 392, 673, 674, 1153, 1252, 1257, 1317, 1338, 2300, 2361,
         3073, 3077, 3083, 3086, 3089, 3091, 3092]
FUTURE = [98, 2745, 2862, 3090]

src = open('index.html', encoding='utf-8').read()
m = re.search(r'const EVENTS = (\[.*?\n\s*\]);', src, re.S)
if not m:
    print('events配列が見つからない')
    sys.exit(1)
events = json.loads(m.group(1))
by_id = {e['id']: e for e in events}


def show(ids, title):
    print('### ' + title)
    for i in ids:
        e = by_id.get(i)
        if not e:
            print(f'{i}: (見つからない)')
            continue
        links = e.get('links') or {}
        url = links.get('pia') or links.get('eplus') or links.get('rakuten') or links.get('lawson')
        if not url:
            tk = e.get('tickets') or []
            url = next((t.get('url') for t in tk if t.get('url')), None)
        print(f"{e['name']}｜{e.get('date')}")
        print(f"  {url}")
    print()


show(ENDED, f'公演終了済 {len(ENDED)}件')
show(FUTURE, f'公演は未来・全枠終了 {len(FUTURE)}件')
