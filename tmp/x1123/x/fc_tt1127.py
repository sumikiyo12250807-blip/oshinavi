import sys, datetime, json
sys.path.insert(0,'C:/Users/user/oshinavi/tools')
import compact_events as C
E=C.load(open('C:/Users/user/oshinavi/index.html',encoding='utf-8',newline='').read())
out=open('C:/Users/user/oshinavi/tmp/x1123/x/fc_tt1127.txt','w',encoding='utf-8')
def p(*a): print(*a,file=out)
p('weekday',datetime.date(2026,11,27).strftime('%a'))
names=['中村雅俊','Reol','GOOD BYE APRIL','GOTCHAROCKA','LOSTAGE']
def g(e):
    x=e.get('genre') or e.get('genres') or ''
    return x if isinstance(x,list) else [x]
for n in names:
    p('==',n)
    for e in E:
        s=json.dumps(e,ensure_ascii=False)
        if n.lower() not in s.lower(): continue
        for t in e.get('tickets',[]):
            if str(t.get('startDate','')).startswith('2026-11-27'):
                p(e.get('id'),g(e),e.get('name') or e.get('title'),'|',t.get('label') or t.get('type') or t.get('name'),t.get('startDate'),t.get('startTime'),t.get('date'))
p('== all jpop/rock on 11/27')
for e in E:
    gg=g(e)
    if not any(x in ('jpop','rock') for x in gg): continue
    for t in e.get('tickets',[]):
        if str(t.get('startDate','')).startswith('2026-11-27'):
            p(e.get('id'),gg,(e.get('name') or e.get('title'))[:40],'|',t.get('label') or t.get('type') or t.get('name'),t.get('startDate'),t.get('startTime'))
out.close()
