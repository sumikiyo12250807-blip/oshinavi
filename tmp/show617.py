import json,sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
d=json.load(open('tmp/parsed.json',encoding='utf-8'))
for i in [617,763]:
    print(f"\n=== id={i} 全枠 ({d[str(i)]['url']}) ===")
    for row in d[str(i)]['rows']:
        print(f"  [{row['state']}|{row['stat_text']}] {row['pd']}~{row['pe']} {row['pref']} {row['venue'][:20]} | {row['when']}")
# 現エントリのtickets確認
sys.path.insert(0,'tools')
from check_expired import extract_events_array
evs={e['id']:e for e in extract_events_array('index.html')}
for i in [617,763,348,425]:
    e=evs[i]
    print(f"\n--- 現エントリ id={i} {e['name']} ---")
    for t in e.get('tickets',[]):
        print(f"   type={t.get('type')} date={t.get('date')} startDate={t.get('startDate')} url={(t.get('url') or '')[-20:]}")
