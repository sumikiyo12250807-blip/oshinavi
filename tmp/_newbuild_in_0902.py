# -*- coding: utf-8 -*-
"""今朝の新規候補87件を build_pia_entries の入力形（newid / artist / urls）にする。
newid は index.html の最大id+1 から連番で振る（既存idは動かさない
＝feedback_new_list_order_lock）。"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
nid = max(e['id'] for e in EV) + 1
print('採番の開始id =', nid)

fresh = json.load(open('tmp/_newfresh_0902.json', encoding='utf-8'))
out = []
for x in fresh:
    out.append({'newid': nid, 'artist': x['artist'], 'urls': [x['url']]})
    nid += 1
json.dump(out, open('tmp/_newbuild_in_0902.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print(f'投入候補 {len(out)}件 → id {out[0]["newid"]}-{out[-1]["newid"]}')
print('→ tmp/_newbuild_in_0902.json')
