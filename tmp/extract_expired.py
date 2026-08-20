import sys
sys.path.insert(0, 'tools')
from check_expired import extract_events_array

ids = [110,128,203,256,337,348,413,425,434,438,448,468,471,533,617,652,658,692,763,803,832,846,866,875,921,927,978,979,980,982,983,984,985,986,987,988,989,990,991,992,997,998,999,1000,1129]
evs = {e['id']: e for e in extract_events_array('index.html')}
import json
out = {}
for i in ids:
    e = evs.get(i)
    if not e:
        print(i, 'NOT FOUND'); continue
    out[i] = e
    pia = (e.get('links') or {}).get('pia')
    print(f"{i}\t{e.get('name','?')[:28]}\t{pia}")
json.dump(out, open('tmp/expired_data.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
