# -*- coding: utf-8 -*-
"""削除候補の確認用URLを index.html から機械抽出（手書き・推測URL厳禁）"""
import io, json, re

IDS = [694, 906, 1156, 1495, 1594, 1600, 1609, 1610, 1569, 1668, 1680, 2180, 2189, 2280, 2312]

s = io.open('index.html', encoding='utf-8').read()
m = re.search(r'const EVENTS = (\[.*?\n\]);', s, re.S)
events = json.loads(m.group(1))
by_id = {e['id']: e for e in events}

out = []
for i in IDS:
    e = by_id.get(i)
    if not e:
        out.append('| %d | (エントリ見つからず) | | |' % i)
        continue
    links = e.get('links') or {}
    urls = []
    for k in ('pia', 'rakuten', 'lawson', 'eplus'):
        if links.get(k):
            urls.append((k, links[k]))
    for t in (e.get('tickets') or []):
        if t.get('url'):
            urls.append(('ticket', t['url']))
    seen = set()
    uniq = []
    for k, u in urls:
        if u not in seen:
            seen.add(u)
            uniq.append((k, u))
    label = {'pia': 'ぴあ', 'rakuten': '楽天', 'lawson': 'ローチケ', 'eplus': 'e+', 'ticket': '枠別'}
    linkstr = ' / '.join('[%s](%s)' % (label[k], u) for k, u in uniq) or '**URL無し**'
    out.append('| %d | %s | %s | %s | %s |' % (
        i, e.get('artist', ''), e.get('name', ''), e.get('venue', ''), linkstr))

with io.open('tmp/del_cand_0714.md', 'w', encoding='utf-8') as f:
    f.write('| id | アーティスト | 公演名 | 会場 | 確認URL |\n')
    f.write('|---|---|---|---|---|\n')
    for r in out:
        f.write(r + '\n')
print('written')
