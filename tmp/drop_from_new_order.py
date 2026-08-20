# -*- coding: utf-8 -*-
"""削除したidを NEW_ORDER 配列からも外す（feedback_new_order_array）。
  python tmp/drop_from_new_order.py 4323
"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
drop = {int(x) for x in sys.argv[1:]}

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(const NEW_ORDER = )(\[[^\]]*\])', h)
order = json.loads(m.group(2))
new = [i for i in order if i not in drop]
print('NEW_ORDER %d → %d 件（除外 %s）' % (len(order), len(new), sorted(drop)))
if new != order:
    open('index.html', 'w', encoding='utf-8').write(
        h[:m.start()] + m.group(1) + json.dumps(new) + h[m.end():])
    print('更新しました')
