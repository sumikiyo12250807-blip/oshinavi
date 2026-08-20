import re, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ids = [876,1119,1120,1212,1704,1805,1810,1835,1836,1837,1838,1839,1892,2036,2037,2038,2039]
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
byid = {e['id']: e for e in EVENTS}
cands = []
for i in ids:
    e = byid.get(i)
    if not e:
        print("MISSING", i); continue
    pia = e['links'].get('pia')
    if not pia:
        print("NO-PIA", i); continue
    cands.append({'newid': i, 'artist': e['artist'], 'urls': [pia]})
json.dump(cands, open('tmp/cand_conv_0708.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print("wrote", len(cands), "candidates")
