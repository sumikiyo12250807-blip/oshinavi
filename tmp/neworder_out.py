# -*- coding: utf-8 -*-
import re, json
h = open('index.html', encoding='utf-8').read()
mo = re.search(r'(  const NEW_ORDER = )(\[.*?\])(;)', h, re.S)
N = json.loads(mo.group(2))
from collections import Counter
dup = {k: v for k, v in Counter(N).items() if v > 1}
out = f"NEW_ORDER件数: {len(N)}\n重複: {dup}\n一凛5件in: {[i for i in (2759,2760,2761,2762,2763) if i in N]}\n全: {N}\n"
open('tmp/neworder_result.txt', 'w', encoding='utf-8').write(out)
