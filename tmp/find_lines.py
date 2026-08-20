import re,io
src=open('index.html',encoding='utf-8').read()
lines=src.split('\n')
ids={110,115,202,337,371,408,428,602,653,778,861,868,869,876}
import json
m=re.search(r'const EVENTS = (\[.*?\]);',src,re.S)
# find line of each '"id": N'
for i,l in enumerate(lines,1):
    mm=re.search(r'"id":\s*(\d+)\b',l)
    if mm and int(mm.group(1)) in ids:
        print(int(mm.group(1)), i)
