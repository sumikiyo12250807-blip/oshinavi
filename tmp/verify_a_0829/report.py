import re,os,json
D='C:/Users/user/oshinavi/tmp/verify_a_0829'
src=open(D+'/parse2.py',encoding='utf-8').read().split('man=json.load')[0]
g={}; exec(src,g)
RAW=D+'/raw'
key=g['key']; load=g['load']
data=json.load(open('C:/Users/user/oshinavi/tmp/verify_in_a_0829.json',encoding='utf-8'))
TI=r'href="(https://t\.pia\.jp/pia/ticketInformation\.do\?[^"]+)"'
EV=r'href="(https://t\.pia\.jp/pia/event/event\.do\?eventCd=\d+)"'
out=[]
for row in data:
    seen=set(); frontier=list(row['urls']); evs=[]; tis=set(); missing=[]
    while frontier:
        u=frontier.pop(0)
        if u in seen: continue
        seen.add(u)
        h=load(u)
        if len(h)<2000: missing.append(u); continue
        tis|=set(re.findall(TI,h))
        childs=set(re.findall(EV,h))
        for c in re.findall(r'ticketInformation\.do\?eventCd=(\d+)',h):
            childs.add('https://t.pia.jp/pia/event/event.do?eventCd=%s'%c)
        for c in sorted(childs):
            if c not in seen: frontier.append(c)
        evs.append(u)
    rec={'id':row['id'],'input':row['urls'],'missing':missing,
         'events':[g['parse_event_page'](u) for u in evs],
         'ti':[g['parse_ti_page'](u) for u in sorted(tis)]}
    rec['ti_missing']=[t['url'] for t in rec['ti'] if not t.get('ok')]
    out.append(rec)
json.dump(out,open(D+'/report.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print('ids',len(out),'missing pages',sum(len(r['missing']) for r in out),'missing ti',sum(len(r['ti_missing']) for r in out))
