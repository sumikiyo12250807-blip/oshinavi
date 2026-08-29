# -*- coding: utf-8 -*-
import json, re
new = json.load(open(r'C:\Users\user\oshinavi\tmp\qc_new.json', encoding='utf-8'))
pat = re.compile(r'[\uac00-\ud7af]|キム|パク|チョン|イ・|チェ・|カン・|チャン・|ユン・|ソン・|シン・|オ・|ハン・|ソ・|チョ・|K-?POP|韓国|コリア|Korea|BTS|SEVENTEEN|TWICE|NCT|IVE|aespa|ATEEZ|Stray')
out=[]
for e in new:
    s = (e.get('name') or '') + ' ' + (e.get('artist') or '')
    if pat.search(s):
        out.append(f"id={e['id']} sub={e.get('_piaSub')} _genre={e.get('_genre')} name={e.get('name')} artist={e.get('artist')}")
open(r'C:\Users\user\oshinavi\tmp\qc_kpop.txt','w',encoding='utf-8').write(
  f'韓国系の可能性がある名前 {len(out)}件\n' + '\n'.join(out))
print('ok')
