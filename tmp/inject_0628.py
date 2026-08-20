# -*- coding: utf-8 -*-
"""built_0628.json(genre:new・売切skip済)を先頭50件に絞り、id 1494〜で採番して
index.htmlのEVENTS末尾に投入＋NEW_ORDER更新。配列round-trip方式(他エントリ無傷)。"""
import re, json, io, sys, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
TAKE = int(sys.argv[1]) if len(sys.argv) > 1 else 50
START_ID = 1494

built = json.load(open('tmp/built_0628.json', encoding='utf-8'))
take = built[:TAKE]
ids = list(range(START_ID, START_ID + len(take)))
for newid, e in zip(ids, take):
    e['id'] = newid

txt = open('index.html', encoding='utf-8').read()
m = re.search(r'const EVENTS = (\[.*?\]);', txt, re.S)
arr = json.loads(m.group(1))
exist_ids = {e['id'] for e in arr}
assert not (set(ids) & exist_ids), 'id衝突: %s' % (set(ids) & exist_ids)
arr.extend(take)
new_block = json.dumps(arr, ensure_ascii=False, indent=2)
new_txt = txt[:m.start(1)] + new_block + txt[m.end(1):]

# NEW_ORDER更新
no_new = '[' + ', '.join(str(i) for i in ids) + ']'
new_txt, n = re.subn(r'(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]', r'\g<1>' + no_new, new_txt, count=1)
assert n == 1, 'NEW_ORDER置換=%d' % n

# 妥当性
json.loads(re.search(r'const EVENTS = (\[.*?\]);', new_txt, re.S).group(1))
shutil.copy('index.html', 'index.html.bak_0628_newpool')
open('index.html', 'w', encoding='utf-8').write(new_txt)
print(f"投入 {len(take)}件 id{ids[0]}..{ids[-1]} / NEW_ORDER更新")
print("backup: index.html.bak_0628_newpool")
