# -*- coding: utf-8 -*-
# 明日10/2発売の出演者（artist）を重複なしで並べ、半分ずつ2つのファイルに分ける＋過去に調べた数（tools/x_log.json）があれば添える
import io, json
root = 'C:/Users/user/oshinavi/'
rows = json.load(io.open(root + 'tmp/x1001/x/pick_1002.json', encoding='utf-8'))
seen, names = set(), []
for r in rows:
    a = (r.get('artist') or r.get('name') or '').strip()
    if a and a not in seen:
        seen.add(a)
        names.append((a, r['id'], r['genre'], (r.get('name') or '')[:40]))
half = (len(names) + 1) // 2
for k, part in (('a', names[:half]), ('b', names[half:])):
    io.open(root + 'tmp/x1001/x/follower_names_%s.txt' % k, 'w', encoding='utf-8').write(
        '\n'.join('%s\tid%s\t%s\t%s' % x for x in part) + '\n')
print(len(names), half)
