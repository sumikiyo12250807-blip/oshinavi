import sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
sys.path.insert(0,'tools')
from check_expired import extract_events_array
evs={e['id']:e for e in extract_events_array('index.html')}
e=evs[992]
print(e['name'],'| genre=',e.get('genre'))
import json
for t in e.get('tickets',[]):
    print(json.dumps(t,ensure_ascii=False))
