# バレエ公演が既存でどのジャンルに入っているかを数える
import re, json, collections

s = open('index.html', encoding='utf-8').read()
m = re.search(r'const EVENTS\s*=\s*(\[.*?\n\s*\];)', s, re.S)
body = m.group(1).rstrip()
if body.endswith(';'):
    body = body[:-1]
EV = json.loads(body)

cnt = collections.Counter()
rows = []
for e in EV:
    name = (e.get('name') or '') + ' ' + (e.get('artist') or '')
    if 'バレエ' in name or 'Ballet' in name or 'BALLET' in name:
        g = e.get('genre')
        cnt[g] += 1
        rows.append((e['id'], g, e.get('name', '')[:50]))

with open('tmp/ballet_genre_0907.txt', 'w', encoding='utf-8') as f:
    f.write('=== バレエを含むエントリのジャンル内訳 ===\n')
    for g, c in cnt.most_common():
        f.write('  %-12s %d件\n' % (g, c))
    f.write('\n=== 一覧 ===\n')
    for r in sorted(rows, key=lambda x: x[1] or ''):
        f.write('  id=%-6s %-12s %s\n' % r)
print('EVENTS', len(EV), 'ballet-ish', len(rows))
