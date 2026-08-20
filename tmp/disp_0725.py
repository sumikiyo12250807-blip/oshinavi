import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

TODAY = '2026-07-25'
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EV = {e['id']: e for e in json.loads(m.group(2))}

# index.html の表示ルール: (!startDate || startDate<=today) && date<today なら非表示
def hidden(t):
    sd, d = t.get('startDate'), t.get('date')
    return (not sd or sd <= TODAY) and (d or '') < TODAY

for i in (299, 2331):
    e = EV.get(i)
    if not e:
        print(i, 'なし'); continue
    ts = e.get('tickets', [])
    vis = [t for t in ts if not hidden(t)]
    print(f"\nid={i} {e.get('name')} 公演日={e.get('date')}")
    print(f"  全{len(ts)}枠 / 画面に出る枠 {len(vis)}")
    for t in ts:
        print(f"   {'表示' if not hidden(t) else '非表示'} | {t.get('type')} | date={t.get('date')} start={t.get('startDate')}")
