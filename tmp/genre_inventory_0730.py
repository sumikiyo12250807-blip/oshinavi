# -*- coding: utf-8 -*-
"""サイトのジャンル一覧（フィルタボタン）と実使用ジャンルの棚卸し"""
import io, json, re, collections

raw = io.open('index.html', encoding='utf-8', newline='').read()

btns = re.findall(r'class="filter-btn[^"]*"[^>]*data-genre="([^"]+)"', raw)
btns2 = re.findall(r'data-genre="([^"]+)"[^>]*class="filter-btn', raw)
out = ['■フィルタボタン data-genre: %s' % sorted(set(btns) | set(btns2))]

m = re.search(r'const\s+EVENTS\s*=\s*(\[.*?\]);', raw, re.S)
arr = json.loads(m.group(1))
c = collections.Counter(e.get('genre') for e in arr)
out.append('■実使用genre: %s' % json.dumps(dict(c.most_common()), ensure_ascii=False))
ex = collections.Counter()
for e in arr:
    for g in e.get('extraGenres') or []:
        ex[g] += 1
out.append('■extraGenres: %s' % json.dumps(dict(ex.most_common()), ensure_ascii=False))

used = set(c) - {'new'}
btnset = set(btns) | set(btns2)
out.append('■ボタンが無いジャンル: %s' % sorted(used - btnset))
out.append('■使われていないボタン: %s' % sorted(btnset - used - {'all'}))

io.open('tmp/out_genre_inv_0730.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('wrote tmp/out_genre_inv_0730.txt')
