# -*- coding: utf-8 -*-
"""7/27の削除候補のid→公演名・確認用URLを index.html から機械抽出（捏造禁止）"""
import sys, io, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ENDED = [33, 38, 47, 198, 221, 257, 344, 360, 422, 937, 1225, 1352, 1388, 2383,
         2758, 3081, 3087, 3093, 3094, 3095, 3098, 3099, 3101, 3104, 3105, 3107]
DEAD_FUTURE = [310]

src = open('index.html', encoding='utf-8').read()
m = re.search(r'const EVENTS = (\[.*?\n\s*\]);', src, re.S)
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
        url = (links.get('pia') or links.get('eplus') or links.get('rakuten')
               or links.get('lawson') or links.get('official'))
        if not url:
            url = next((t.get('url') for t in (e.get('tickets') or []) if t.get('url')), None)
        label = 'ぴあ' if url and 't.pia.jp' in url else (
            'e+' if url and 'eplus.jp' in url else (
                'ローチケ' if url and 'l-tike' in url else (
                    '楽天' if url and 'rakuten' in url else '公式')))
        print(f"- {e['name']} — [{label}]({url})")
    print()


show(ENDED, f'公演終了済（7/26公演） {len(ENDED)}件')
show(DEAD_FUTURE, f'公演は未来だが一般発売が終了 {len(DEAD_FUTURE)}件')
