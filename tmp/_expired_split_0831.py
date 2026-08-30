import re,sys,json
sys.stdout.reconfigure(encoding='utf-8')
lines=open('tmp/_expired_0831.log',encoding='utf-8').read().split('\n')
ended=[];recheck=[]
for ln in lines:
    m=re.match(r'\s+id=(\d+): (.*)',ln)
    if not m: continue
    body=m.group(2)
    if '開催終了' in body: ended.append((int(m.group(1)),body))
    else: recheck.append((int(m.group(1)),body))
print('公演終了済',len(ended),'/ 要再確認',len(recheck))
open('tmp/_ended_ids_0831.txt','w').write(','.join(str(i) for i,_ in ended))
open('tmp/_recheck_ids_0831.txt','w').write(','.join(str(i) for i,_ in recheck))
with open('tmp/_ended_list_0831.md','w',encoding='utf-8') as f:
    for i,b in ended: f.write(f"- id={i} {b}\n")
