# -*- coding: utf-8 -*-
import json, io, collections
d = json.load(io.open('tmp/_word_pool_miss_0901.json', encoding='utf-8'))
print('N=%d' % len(d))
print('KEYS=%s' % ', '.join(sorted({k for x in d for k in x})))
c = collections.Counter()
for x in d:
    for k in ('genre', 'category', 'cat', 'word', 'src', 'source'):
        if x.get(k):
            c[(k, str(x[k]))] += 1
with io.open('tmp/pool_keys_0905.txt', 'w', encoding='utf-8') as f:
    for k, v in c.most_common(30):
        f.write('%s = %s : %d\n' % (k[0], k[1], v))
