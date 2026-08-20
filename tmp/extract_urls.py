import re, json
ids = [110,115,202,337,348,371,408,428,602,653,778,861,868,869,876]
src = open('index.html',encoding='utf-8').read()
m = re.search(r'const EVENTS = (\[.*?\]);', src, re.S)
data = json.loads(m.group(1))
for e in data:
    if e.get('id') in ids:
        links = e.get('links',{})
        url = links.get('pia') or links.get('rakuten') or links.get('eplus') or links.get('lawson') or ''
        print(f"id={e['id']} | {e.get('name','')[:30]} | {url}")
