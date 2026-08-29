# -*- coding: utf-8 -*-
"""id=753 を後継URL(2628494)の実データで差し替える。
   🚨index.html は CRLF。newline='' を付けずに読み書きすると全行LF化して sort_guard が誤ブロックする。"""
import json,re,io,sys,shutil
sys.stdout.reconfigure(encoding='utf-8')
new=json.load(open('tmp/rescue753_out.json',encoding='utf-8'))[0]
P='index.html'
shutil.copy(P,'index.html.bak_0827_rescue753')
src=io.open(P,encoding='utf-8',newline='').read()
m=re.search(r'(  const EVENTS = )(\[.*?\])(;)',src,re.S)
EV=json.loads(m.group(2))
for e in EV:
    if e['id']!=753: continue
    before=json.dumps(e,ensure_ascii=False)
    e['date']=new['date']; e['dateLabel']=new['dateLabel']
    e['venue']=new['venue']; e['prefecture']=new['prefecture']
    e['tickets']=new['tickets']
    e['links']['pia']=new['links'].get('pia') or e['links']['pia']
    e['verified']=True; e['verifiedAt']='2026-08-27'
    print('BEFORE:',before[:200])
    print('AFTER :',json.dumps(e,ensure_ascii=False)[:200])
    break
else:
    print('id=753 が見つからない'); sys.exit(1)
arr=json.dumps(EV,ensure_ascii=False,indent=2)
arr='\n'.join('  '+l if i else l for i,l in enumerate(arr.split('\n')))
out=src[:m.start(2)]+arr+src[m.end(2):]
if '\r\n' in src:                      # CRLFを保つ
    out=out.replace('\r\n','\n').replace('\n','\r\n')
io.open(P,'w',encoding='utf-8',newline='').write(out)
print('applied')
