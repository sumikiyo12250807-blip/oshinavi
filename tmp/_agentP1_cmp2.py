# -*- coding: utf-8 -*-
import re,io,sys,json,unicodedata,collections
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
ev={str(e['id']):e for e in json.load(open('tmp/_agentP1_events.json',encoding='utf-8'))}
pia=json.load(open('tmp/_agentP1_parsed.json',encoding='utf-8'))
CHILD={'5747':'音楽 フェスティバル','5766':'音楽 J-POP・ROCK','5784':'音楽 J-POP・ROCK',
       '5794':'音楽 J-POP・ROCK','5824':'音楽 海外ROCK・POPS'}
for eid,v in pia.items():
    g=v['genre']
    if not g:
        h=open('tmp/_agentP1_html/%s.html'%eid,encoding='utf-8').read()
        t=re.search(r'<title>[^<]*?\[([^\[\]]*?)のチケット購入・予約\]',h)
        g=t.group(1) if t else CHILD.get(eid,'')
    v['genre2']=g
def norm(s):
    return re.sub(r'[\s　]+','',unicodedata.normalize('NFKC',s or '')).lower()
gbad=[]
for eid,v in pia.items():
    r=(ev[eid].get('_piaSub') or '')
    if norm(r.replace('/','')) != norm(v['genre2']):
        gbad.append((eid,r,v['genre2']))
print('ジャンル不一致:',gbad if gbad else 'なし（81/81一致）')
print()
# 販売日の突合
def pia_dates(c):
    w=c['when']
    m=re.search(r'(\d{4})/(\d{1,2})/(\d{1,2})',w)
    d='%04d-%02d-%02d'%tuple(int(x) for x in m.groups()) if m else ''
    return d
bad=[]
for eid,v in pia.items():
    e=ev[eid]
    buy=[c for c in v['cards'] if c['state'] in ('受付中','発売前')]
    pset=collections.Counter()
    for c in buy:
        pset[(c['state'],pia_dates(c))]+=1
    rset=collections.Counter()
    for t in e['tickets']:
        rset[('発売前' if t.get('startDate') else '受付中', t.get('startDate') or t.get('date'))]+=1
    if pset!=rset:
        bad.append((eid,e['artist'],dict(rset),dict(pset),[c['when'] for c in buy],[t['type'] for t in e['tickets']]))
print('販売日(締切/発売日)の不一致', len(bad),'件')
for b in bad:
    print('---',b[0],b[1])
    print('  登録:',b[2])
    print('  ぴあ:',b[3])
    print('  ぴあ表記:',b[4])
    print('  登録type:',b[5])
