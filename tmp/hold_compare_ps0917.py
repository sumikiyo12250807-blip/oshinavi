import io, json, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
built = {b['id']: b for b in json.load(io.open('tmp/built_ps_0917.json', encoding='utf-8'))}
src = io.open('index.html', encoding='utf-8').read()
ev = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))}
PAIRS = {
    11067: [5526, 5527, 5528, 7029], 11068: [6284, 6285, 6286, 7031], 11069: [6284, 6285, 6286, 7031],
    11073: [5848], 11074: [5848], 11081: [7858], 11085: [5346, 5347], 11093: [942, 4638],
    11111: [5755, 7470, 7471, 7472, 7473, 7474, 7475, 7948, 10762], 11112: [], 11113: [10762, 5755],
    11116: [7933], 11117: [], 11118: [], 11119: [], 11120: [], 11121: [], 11126: [7790], 11135: [3674], 11136: [],
}
def show(e, tag):
    print(f"  {tag} id{e['id']} {e.get('name') or e.get('artist')} | {e.get('dateLabel')} | {e.get('venue')} | {e.get('prefecture')} | genre={e.get('genre')} | pia={(e.get('links') or {}).get('pia')}")
    for t in e.get('tickets', [])[:12]:
        print(f"      - {t.get('type')} | {t.get('date')}{' SOLD' if t.get('soldout') else ''}")
    if len(e.get('tickets', [])) > 12:
        print(f"      … 他{len(e['tickets'])-12}枠")
seen = set()
for n, tg in PAIRS.items():
    print('=' * 60)
    show(built[n], '新')
    for t in tg:
        if t in seen: print(f'  (既 id{t} は上に表示済み)'); continue
        seen.add(t)
        if t in ev: show(ev[t], '既')
