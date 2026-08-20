import re,json
# current new-pool ids
src=open('index.html',encoding='utf-8').read()
m=re.search(r'=\s*(\[\s*\{.*?\}\s*\]);',src,re.S)
data=json.loads(m.group(1))
new_ids={e['id'] for e in data if e.get('genre')=='new'}
name_map={e['id']:e.get('name','') for e in data}
# table
tbl={}
for line in open('tmp/genre_table.tsv',encoding='utf-8').read().splitlines():
    if not line.strip():continue
    i,g,nm=line.split('\t');tbl[int(i)]=g
override={899:'jpop+hiphop',922:'jpop+rock',903:'rock+fes',907:'rock+fes'}
from collections import defaultdict
groups=defaultdict(list)
missing=[]
for i in sorted(new_ids):
    if i in tbl:
        groups[tbl[i]].append(i)
    else:
        missing.append(i)
order=['jpop','rock','idol','jazz','enka','classic','dento','fes','kpop','hiphop']
for g in order+[x for x in groups if x not in order]:
    if g in groups:
        ids=groups[g]
        print(f"\n■ {g} ({len(ids)}件)")
        for i in ids:
            nm=name_map.get(i,'')[:30]
            ex=f"  ★両方方式={override[i]}" if i in override else ""
            print(f"  {i} {nm}{ex}")
if missing:
    print("\n⚠️ 表に無い(新規/要確認):",missing)
