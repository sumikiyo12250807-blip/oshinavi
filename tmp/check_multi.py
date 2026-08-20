import sys,io,json
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
sys.path.insert(0,'tools')
from check_expired import extract_events_array
evs={e['id']:e for e in extract_events_array('index.html')}
conv=[348,413,533,617,692,763,832,846,875,921,927,979,980,983,984,985,986,987,989,990,991,992,997,998,999,1000]
for i in conv:
    e=evs[i]; ts=e.get('tickets',[])
    urls=set((t.get('url') or '').split('eventCd=')[-1].split('eventBundleCd=')[-1].split('&')[0] for t in ts)
    if len(ts)>1:
        print(f"id={i} tickets={len(ts)} urls={urls}")
        for t in ts: print(f"    {t.get('type')}")
