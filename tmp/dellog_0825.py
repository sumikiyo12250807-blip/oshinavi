# 削除ログ用の行を作る（削除前に実行）
import re, io, json, sys
sys.stdout.reconfigure(encoding='utf-8')

IDS = [835, 862, 979, 1138, 1224, 2086, 2542, 2726, 2809, 2927, 3209]

s = io.open('index.html', encoding='utf-8').read()
m = re.search(r'const EVENTS\s*=\s*(\[)', s)
i = m.start(1); depth = 0
for j in range(i, len(s)):
    if s[j] == '[': depth += 1
    elif s[j] == ']':
        depth -= 1
        if depth == 0: break
ev = json.loads(s[i:j+1])
by = {e['id']: e for e in ev}

rows = []
for eid in IDS:
    e = by[eid]
    links = e.get('links') or {}
    url = ''
    for k in ('pia', 'eplus', 'lawson', 'rakuten'):
        if links.get(k):
            url = links[k]; break
    if not url:
        for t in e.get('tickets') or []:
            if t.get('url'):
                url = t['url']; break
    last = max([t.get('date', '') for t in (e.get('tickets') or [])] or [''])
    rows.append('| %d | %s | %s | %s | %s | %s |' % (
        eid, e.get('name', ''), e.get('date', ''), last, e.get('venue', ''), url))

print('| id | 公演名 | 千秋楽 | 最終締切 | 会場 | 確認用URL |')
print('|---|---|---|---|---|---|')
for r in rows:
    print(r)
