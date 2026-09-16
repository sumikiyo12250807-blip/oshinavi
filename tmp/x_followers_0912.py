# -*- coding: utf-8 -*-
"""明日(9/12)発売の組を一意に並べ、tools/x_log.json に貯めたXフォロワー実測と突き合わせる（読むだけ）。
出力: tmp/x_followers_0912.md（実測がある組は多い順・無い組は名前だけ）"""
import io, json, re, datetime, collections
TOMORROW = '2026-09-12'
h = io.open('index.html', encoding='utf-8').read()
EV = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))
xl = json.load(io.open('tools/x_log.json', encoding='utf-8'))
arts = (xl.get('artists') or {}).get('data') or []
fol = {}
for a in arts:
    if isinstance(a, dict):
        nm = a.get('name') or a.get('artist')
        n = a.get('followers')
        if nm and isinstance(n, (int, float)):
            fol[nm] = (n, a.get('handle') or a.get('x') or '', a.get('date') or a.get('checked') or '')
rows = collections.OrderedDict()
for e in EV:
    if e.get('genre') == 'new':
        continue
    for t in e.get('tickets') or []:
        if t.get('startDate') == TOMORROW and not t.get('soldout'):
            key = e.get('artist') or e.get('name')
            r = rows.setdefault(key, {'ids': set(), 'genre': e.get('genre'), 'n': 0, 'times': set()})
            r['ids'].add(e['id']); r['n'] += 1
            m = re.search(r'(\d{1,2}:\d{2})発売', t.get('type') or '')
            if m: r['times'].add(m.group(1))
out = io.open('tmp/x_followers_0912.md', 'w', encoding='utf-8')
known = sorted([(fol[k][0], k) for k in rows if k in fol], reverse=True)
out.write('# 明日9/12発売の組 %d組 ／ フォロワー実測あり %d組\n\n' % (len(rows), len(known)))
for n, k in known:
    r = rows[k]
    out.write('- %s … %s人 %s（%s）[%s] %s枠 %s id%s\n' % (k, format(int(n), ','), fol[k][1], fol[k][2], r['genre'], r['n'], '/'.join(sorted(r['times'])), sorted(r['ids'])))
out.write('\n## 実測なし\n\n')
for k, r in rows.items():
    if k not in fol:
        out.write('- %s [%s] %s枠 %s id%s\n' % (k, r['genre'], r['n'], '/'.join(sorted(r['times'])), sorted(r['ids'])))
out.close()
print('組 %d / 実測あり %d → tmp/x_followers_0912.md' % (len(rows), len(known)))
