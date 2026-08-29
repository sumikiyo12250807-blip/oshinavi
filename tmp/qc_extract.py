# -*- coding: utf-8 -*-
import json, re, collections, io, sys
src = open(r'C:\Users\user\oshinavi\index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
new = [e for e in events if e.get('genre') == 'new']
print('new件数', len(new))
print('id範囲', min(e['id'] for e in new), max(e['id'] for e in new))
c = collections.Counter((e.get('_piaSub') or '(空)') for e in new)
for k,v in c.most_common(): print(f'{v:4d}  {k}')
print('--- _genre分布 ---')
c2 = collections.Counter((e.get('_genre') or '(空)') for e in new)
for k,v in c2.most_common(): print(f'{v:4d}  {k}')
print('--- _extraGenres有 ---')
for e in new:
    if e.get('_extraGenres'): print(e['id'], e.get('_genre'), e['_extraGenres'], e.get('_piaSub'))
json.dump(new, open(r'C:\Users\user\oshinavi\tmp\qc_new.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
