import sys,io,json
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
sys.path.insert(0,'tools')
from check_expired import extract_events_array
evs={e['id']:e for e in extract_events_array('index.html')}
for i in [617,763,987,992,413,348]:
    print(f"id={i}")
    for t in evs[i]['tickets']:
        print('   ', repr(t.get('url')))
