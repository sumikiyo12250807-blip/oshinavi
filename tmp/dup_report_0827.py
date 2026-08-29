# -*- coding: utf-8 -*-
import json,re,io,sys,collections
sys.stdout.reconfigure(encoding='utf-8')
d=json.load(open('tmp/batch_cand_0827.json',encoding='utf-8'))
dup=d['dup']
o=io.open('tmp/dup_0827.md','w',encoding='utf-8')
o.write('# 2026-08-27 統合待ち（既存エントリと同名/部分一致の未掲載枠）%d件\n\n'%len(dup))
o.write('| 既存id | ぴあの公演名 | 公演日 | 発売日 | 一致 | URL |\n|---|---|---|---|---|---|\n')
byid=collections.Counter()
for x in dup:
    it=x['it']; why=x['why']
    m=re.search(r'id(\d+)',why); eid=m.group(1) if m else '?'
    byid[eid]+=1
    o.write('| %s | %s | %s | %s | %s | %s |\n'%(eid,it['artist'].replace('|','｜')[:40],
            (it.get('perfdate') or '')[:26], it.get('rlsdate',''), why.split()[0], it['url']))
o.write('\n## 同じ既存idに複数ぶら下がっているもの（＝ツアーが分裂している疑い）\n\n')
for eid,n in byid.most_common():
    if n>=2: o.write('- id%s に %d枠\n'%(eid,n))
o.close()
print('統合待ち',len(dup),'／既存id数',len(byid),'／2枠以上ぶら下がるid',sum(1 for v in byid.values() if v>=2))
