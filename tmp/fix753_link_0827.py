# -*- coding: utf-8 -*-
import json,re,io,sys,shutil
sys.stdout.reconfigure(encoding='utf-8')
P='index.html'
shutil.copy(P,'index.html.bak_0827_fix753link')
src=io.open(P,encoding='utf-8',newline='').read()
m=re.search(r'(  const EVENTS = )(\[.*?\])(;)',src,re.S)
EV=json.loads(m.group(2))
for e in EV:
    if e['id']==753:
        old=e['links']['pia']
        e['links']['pia']='https://t.pia.jp/pia/event/event.do?eventCd=2628494'
        print('pia:',old,'->',e['links']['pia'])
        break
arr=json.dumps(EV,ensure_ascii=False,indent=2)
arr='\n'.join('  '+l if i else l for i,l in enumerate(arr.split('\n')))
out=src[:m.start(2)]+arr+src[m.end(2):]
if '\r\n' in src:
    out=out.replace('\r\n','\n').replace('\n','\r\n')
io.open(P,'w',encoding='utf-8',newline='').write(out)
print('applied')
