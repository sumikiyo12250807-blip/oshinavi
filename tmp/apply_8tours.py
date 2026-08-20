# -*- coding: utf-8 -*-
import json, io, sys, shutil, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
eight = json.load(open('tmp/eight_tours.json', encoding='utf-8'))
META = {
 129:('全国ツアー','全国','2026年6月〜10月 全国ツアー','2026-10-02'),
 237:('全国ツアー','全国','2026年9月〜12月 全国ツアー','2026-12-28'),
 529:('全国ツアー','全国','2026年8月〜2027年2月 全国ツアー','2027-02-07'),
 539:('全国ツアー','全国','2026年8月〜9月 全国ツアー','2026-09-06'),
 824:('全国ツアー','全国','2026年7月〜10月 全国ツアー','2026-10-31'),
 665:('全国ツアー','全国','2026年7月〜8月 全国ツアー','2026-08-16'),
 431:('全国ツアー','全国','2026年7月〜9月 全国ツアー','2026-09-03'),
 269:('日生劇場／梅田芸術劇場メインホール／御園座','全国','2026年9月〜11月 東京・大阪・愛知','2026-11-15'),
}
txt = open('index.html', encoding='utf-8').read()
i = txt.index('const EVENTS = [') + len('const EVENTS = ')
arr, _ = json.JSONDecoder().raw_decode(txt, i)
byid = {e['id']: e for e in arr}
def tb(t):
    d=json.dumps(t,ensure_ascii=False,indent=2);l=d.split('\n')
    return l[0]+'\n'+'\n'.join('    '+x for x in l[1:])
new=txt; done=[]
for eid_s,info in eight.items():
    eid=int(eid_s); e=byid[eid]; venue,pref,dl,date=META[eid]
    key=f'\n    "id": {eid},\n'; si=new.find(key)
    m=re.search(r'\n  \},?\n', new[si:]); ei=si+m.end(); span=new[si:ei]
    old_t='"tickets": '+tb(e['tickets'])
    assert span.count(old_t)==1,(eid,'tickets',span.count(old_t))
    span=span.replace(old_t,'"tickets": '+tb(info['tickets']))
    # scalars
    for field,newval in [('venue',venue),('prefecture',pref),('dateLabel',dl),('date',date)]:
        cur=e.get(field)
        a=f'"{field}": {json.dumps(cur,ensure_ascii=False)}'
        b=f'"{field}": {json.dumps(newval,ensure_ascii=False)}'
        if a==b: continue
        assert span.count(a)==1,(eid,field,span.count(a),a)
        span=span.replace(a,b)
    new=new[:si]+span+new[ei:]; done.append(eid)
shutil.copy('index.html','index.html.bak_0621_8tours')
open('index.html','w',encoding='utf-8').write(new)
print('applied 8tours:',done)
