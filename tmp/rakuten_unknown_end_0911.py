# -*- coding: utf-8 -*-
"""楽天チケットの枠のうち「販売の終わりが分からない」もの（saleEndUnknown）を一覧にする（読むだけ）。
あわせて「発売〜」形（終わりの無い表記）なのに saleEndUnknown が付いていない楽天枠も拾う。
出力: 画面＋ tmp/rakuten_unknown_end_0911.json（id・枠・URL）"""
import json, re, sys, urllib.parse
sys.stdout.reconfigure(encoding='utf-8')
src = open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))


def raw(u):
    m = re.search(r'murl=([^&]+)', u or '')
    return urllib.parse.unquote(m.group(1)) if m else (u or '')


rows = []
for e in ev:
    L = e.get('links') or {}
    for t in e.get('tickets') or []:
        u = raw(t.get('url') or '')
        if not u and not (L.get('pia') or L.get('eplus') or L.get('lawson')):
            u = raw(L.get('rakuten') or '')
        if 'rakuten' not in u:
            continue
        ty = t.get('type') or ''
        flag = bool(t.get('saleEndUnknown'))
        tail = bool(re.search(r'発売〜\s*$', ty))
        if flag or tail:
            rows.append({'id': e['id'], 'name': e.get('name'), 'genre': e.get('genre'), 'type': ty,
                         'date': t.get('date'), 'startDate': t.get('startDate'), 'flag': flag,
                         'url': u.split('?')[0], 'show': e.get('date')})
for r in rows:
    print('id%-5s %s | %s | date=%s start=%s flag=%s | %s' % (r['id'], (r['name'] or '')[:26], r['type'][:50], r['date'], r['startDate'], r['flag'], r['url']))
print('合計 %d枠 / %dエントリ / ページ %d本' % (len(rows), len({r['id'] for r in rows}), len({r['url'] for r in rows})))
json.dump(rows, open('tmp/rakuten_unknown_end_0911.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
