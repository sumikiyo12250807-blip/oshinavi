import json,sys,time,os
sys.path.insert(0,'C:/Users/user/oshinavi/tools')
sys.stdout.reconfigure(encoding='utf-8')
from eplus_detail import fetch,parse
urls=[l.strip() for l in open(sys.argv[1],encoding='utf-8') if l.strip()]
out=json.load(open(sys.argv[2],encoding='utf-8')) if os.path.exists(sys.argv[2]) else {}
for u in urls:
    if u in out: continue
    for k in range(3):
        try:
            h=fetch(u); out[u]=parse(h); break
        except Exception as e:
            print('ERR',u,e); time.sleep(10)
    time.sleep(1.2)
    json.dump(out,open(sys.argv[2],'w',encoding='utf-8'),ensure_ascii=False,indent=1)
for u in urls:
    for s in out.get(u,[]):
        print(u.split('/')[-1], s['date'], s['venue'], s['pref'])
        for t in s['tickets']: print('   ',t['status'],'|',t['name'],'|',t['period'])
