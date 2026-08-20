# -*- coding: utf-8 -*-
"""AUTO群(617,763除く72件)の発売前→販売中変換案を作る。
ルール:
 - startDate==date かつ date<=today の券種(=昨日6/20開始の一般発売)を販売中形に変換
   type末尾の「M/D HH:MM発売」を「〜<endM>/<endD> <endHH:MM>」に置換、startDate削除、date=end
 - 終了済み先行/プレリザーブ(startDateなし & date<today)は削除
 - 受付中endはぴあページの単一受付中card由来(全opened券種に適用)
"""
import json, re, io, sys, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
d = json.load(open('tmp/presale_ends.json', encoding='utf-8'))
cats = json.load(open('tmp/convert_cats.json', encoding='utf-8'))
today = datetime.date(2026,6,21)
def pd(s):
    try: return datetime.date(*map(int,str(s).split('-')))
    except: return None
def when_to(w):
    m=re.search(r'(\d{4})/(\d{1,2})/(\d{1,2}).*?(\d{1,2}:\d{2})',w)
    if not m:
        m=re.search(r'(\d{4})/(\d{1,2})/(\d{1,2})',w)
        if not m: return None
        return (f'{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}','23:59',f'{int(m.group(2))}/{int(m.group(3))}')
    return (f'{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}',m.group(4),f'{int(m.group(2))}/{int(m.group(3))}')

txt=open('index.html',encoding='utf-8').read()
i=txt.index('const EVENTS = [')+len('const EVENTS = ')
arr,_=json.JSONDecoder().raw_decode(txt,i)
byid={e['id']:e for e in arr}

targets=[e for e in cats['AUTO'] if e not in ('617','763')]
proposal={}
for eid in targets:
    rec=d[eid]
    uk=[c for c in rec.get('uketsuke',[]) if c['state']=='受付中']
    ends=[when_to(c['when']) for c in uk]
    ends=[x for x in ends if x]
    if not ends: continue
    end_iso,end_hm,end_md=ends[0]  # single-end AUTO
    e=byid[int(eid)]
    newtks=[]
    for t in e['tickets']:
        sd=pd(t.get('startDate','')) if t.get('startDate') else None
        td=pd(t.get('date',''))
        if sd and td and sd==td and td<=today:
            # 発売前→販売中: strip trailing "M/D HH:MM発売" or "...発売"
            ntype=re.sub(r'\s*\d{1,2}/\d{1,2}\s*\d{1,2}:\d{2}発売\s*$','',t['type'])
            ntype=re.sub(r'\s*\d{1,2}:\d{2}発売\s*$','',ntype)
            ntype=re.sub(r'\s*発売前\s*$','',ntype)
            ntype=ntype.rstrip()
            ntype=f'{ntype}〜{end_md} {end_hm}'
            newtks.append({'type':ntype,'date':end_iso})
        elif sd and td and sd>today:
            newtks.append(t)  # まだ発売前(将来) keep
        elif (not sd) and td and td<today:
            continue  # 終了済み先行 drop
        else:
            newtks.append(t)  # その他keep
    proposal[eid]={'name':e['name'][:40],'old':[t['type'] for t in e['tickets']],
                   'new':[{'type':t['type'],'date':t['date'],'sd':t.get('startDate')} for t in newtks]}

json.dump(proposal,open('tmp/proposal.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
for eid,p in proposal.items():
    print(f"id{eid} {p['name']}")
    for t in p['new']:
        print(f"    NEW: {t['type']}  (date {t['date']})")
print("\n変換対象:",len(proposal),"件")
PY = None
