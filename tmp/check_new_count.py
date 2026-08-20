import re,json
src=open('index.html',encoding='utf-8').read()
m=re.search(r'=\s*(\[\s*\{.*?\}\s*\]);',src,re.S)
data=json.loads(m.group(1))
print("総数",len(data))
from collections import Counter
c=Counter(e.get('genre') for e in data)
print("genre:new 残り =",c.get('new',0))
print("今回振り分け関連:",{g:c[g] for g in ['jpop','rock','idol','jazz','enka','classic','dento','fes'] if g in c})
