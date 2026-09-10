# -*- coding: utf-8 -*-
"""ぴあで見つかった公演が、もう登録にあるかを eventCd で突き合わせる。

🚨名前の部分一致だけで「載っていない」と言わない
   （京まふ＝KYOMAF、XMF＝Xnterstellar のように**表記が違うだけ**で載っていることがある）。
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

h = io.open('index.html', encoding='utf-8').read()
codes = set(re.findall(r'event(?:Bundle)?Cd=([\w]+)', h))
print('登録にある eventCd/eventBundleCd: %d本' % len(codes))

hunt = json.load(io.open('tmp/hunt_big_0910.json', encoding='utf-8'))
for nm, d in hunt.items():
    if not d['hits']:
        continue
    for x in d['hits']:
        m = re.search(r'event(?:Bundle)?Cd=([\w]+)', x['url'])
        cd = m.group(1) if m else ''
        mark = '✅登録済み' if cd in codes else '🚨未登録'
        print('%-22s %s [%s] %-42s %s' % (nm[:22], mark, x['state'], x['name'][:42], x['date'][:22]))
        if cd not in codes:
            print('       %s' % x['url'])
            if x['sale']:
                print('       発売 %s' % x['sale'])
