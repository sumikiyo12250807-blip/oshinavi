import json,math
entries=json.load(open('tmp/theater_entries.json',encoding='utf-8'))
out=[]
for e in entries:
    links=e.get('links',{}) or {}
    main=links.get('pia') or ''
    turls=[t.get('url') for t in e.get('tickets',[]) if t.get('url')]
    urls=[main]+[u for u in turls if u and u!=main]
    # give only id, artist NAME (so they can find it on page) and urls — NOT tickets/dates
    out.append({'id':e['id'],'name_hint':e.get('name'),'urls':urls})
n=5; per=math.ceil(len(out)/n)
for b in range(n):
    chunk=out[b*per:(b+1)*per]
    json.dump(chunk,open(f'tmp/tverify_{b}.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
    print(f'tverify_{b}: {len(chunk)}件 ids={[c["id"] for c in chunk]}')
