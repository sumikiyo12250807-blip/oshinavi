import re, json, datetime
today=datetime.date(2026,6,19)
src=open('index.html',encoding='utf-8').read()
m=re.search(r'=\s*(\[\s*\{.*?\}\s*\]);',src,re.S)
data=json.loads(m.group(1))
news=[e for e in data if e.get('genre')=='new']
print("genre:new 件数 =",len(news))
def mind(e):
    ds=[t.get('date') for t in e.get('tickets',[]) if t.get('date')]
    return min(ds) if ds else '9999'
news.sort(key=mind)
soon=[]
for e in news:
    md=mind(e)
    try:
        d=datetime.date.fromisoformat(md)
        days=(d-today).days
    except:
        days=999
    flag = '⚠️過ぎ' if days<0 else ('🔴当日' if days==0 else ('🟠'+str(days)+'日' if days<=3 else ''))
    if days<=3:
        soon.append((e['id'],md,days,e.get('name','')[:28]))
print("\n=== 締切3日以内/超過 ===")
for i,(eid,md,days,nm) in enumerate(soon):
    print(eid,md,f"({days}日)", nm)
print("\n合計 締切間近/超過:",len(soon))
