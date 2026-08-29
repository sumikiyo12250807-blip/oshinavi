import json,sys
sys.stdout.reconfigure(encoding='utf-8')
old={e['id']:e for e in json.load(open('tmp/built_0827.json',encoding='utf-8'))}
new={e['id']:e for e in json.load(open('tmp/rebuilt_0827.json',encoding='utf-8'))}
for i in sorted(new):
    o,n=old.get(i),new[i]
    ot=[(t['type'],t['date'],t.get('url')) for t in o['tickets']]
    nt=[(t['type'],t['date'],t.get('url')) for t in n['tickets']]
    same=[x[:2] for x in ot]==[x[:2] for x in nt]
    print('id=%d 枠 %d→%d 券種/締切が同一=%s url有 %d→%d'%(
        i,len(ot),len(nt),same,sum(1 for x in ot if x[2]),sum(1 for x in nt if x[2])))
    if not same:
        print('   OLD:',[x[:2] for x in ot]); print('   NEW:',[x[:2] for x in nt])
