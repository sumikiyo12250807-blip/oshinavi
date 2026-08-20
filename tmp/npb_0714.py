# -*- coding: utf-8 -*-
"""NPBレギュラー戦8件の確認用URLを index.html から機械抽出"""
import io, json, re

IDS = [2628, 2629, 2630, 2631, 2632, 2633, 2634, 2635]

s = io.open('index.html', encoding='utf-8').read()
m = re.search(r'const EVENTS = (\[.*?\n\]);', s, re.S)
ev = json.loads(m.group(1))
d = {e['id']: e for e in ev}

with io.open('tmp/npb_0714.md', 'w', encoding='utf-8') as f:
    f.write('| 公演名 | 会場 | 確認URL |\n|---|---|---|\n')
    for i in IDS:
        e = d[i]
        f.write('| %s | %s | [ぴあ](%s) |\n' % (
            e['name'], e['venue'], e['links']['pia']))
print('done')
