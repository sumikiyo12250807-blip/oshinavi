# -*- coding: utf-8 -*-
"""🚨統合で足した91枠に ticket.url が付いていない＝クリックすると既存エントリの links.pia
（=別会場の売り場）に飛ぶ。memory: feedback_build_pia_multiurl_loses_ticket_url

直し方＝統合の入力 tmp/build_in_merge_0830.json は「既存id → 今日拾った新しいぴあURL」1対1なので、
今朝この統合で足した枠にだけ、そのURLを ticket.url として付ける。既存の枠には触らない。"""
import io,re,json,sys,shutil
sys.stdout.reconfigure(encoding='utf-8')

url_by_id={x['newid']:x['urls'][0] for x in json.load(io.open('tmp/build_in_merge_0830.json',encoding='utf-8')) if len(x['urls'])==1}
# 今朝の統合で足した枠 (id, type, date)
added=set()
cur=None
for ln in io.open('logs/merged_2026-08-30.md',encoding='utf-8'):
    m=re.match(r'## id=(\d+)',ln)
    if m: cur=int(m.group(1)); continue
    m=re.match(r'  \+ (.*?) \| 締切/発売 (\S+) \|',ln)
    if m and cur: added.add((cur,m.group(1),m.group(2)))
print('今朝足した枠:',len(added),'／URLが引ける既存id:',len(url_by_id))

P='index.html'
shutil.copy(P,'index.html.bak_0830_fixurl')
src=io.open(P,encoding='utf-8',newline='').read()
m=re.search(r'(  const EVENTS = )(\[.*?\])(;)',src,re.S)
EVENTS=json.loads(m.group(2))
n=0; skipped=[]
for e in EVENTS:
    u=url_by_id.get(e['id'])
    if not u: continue
    for t in e.get('tickets',[]):
        if (e['id'],t.get('type'),t.get('date')) in added:
            if t.get('url'):
                skipped.append((e['id'],t.get('type'))); continue
            t['url']=u; n+=1
print('url を付けた枠:',n,'／既にurlがあって触らなかった:',len(skipped))
arr=json.dumps(EVENTS,ensure_ascii=False,indent=2)
arr='\n'.join('  '+l if i else l for i,l in enumerate(arr.split('\n')))
out=src[:m.start(2)]+arr+src[m.end(2):]
if '\r\n' in src: out=out.replace('\r\n','\n').replace('\n','\r\n')
io.open(P,'w',encoding='utf-8',newline='').write(out)
print('applied')
