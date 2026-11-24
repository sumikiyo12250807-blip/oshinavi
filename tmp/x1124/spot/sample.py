# -*- coding: utf-8 -*-
# 11/24 抜き打ち：振り分け済み・買える枠ありからランダム30件 → 15件ずつ2組（seed 11242026）
import io, json, os, random, sys
root = 'C:/Users/user/oshinavi/'
sys.path.insert(0, root + 'tools')
import compact_events as C
TODAY = '2026-11-24'
os.makedirs(root + 'tmp/x1124/spot', exist_ok=True)
E = C.load(io.open(root + 'index.html', encoding='utf-8', newline='').read())
def urls(e):
    return ' '.join(t.get('url') or '' for t in e.get('tickets') or []) + ' ' + ' '.join(str(v) for v in (e.get('links') or {}).values())
pool = [e for e in E if e.get('genre') != 'new' and (e.get('date') or '') >= TODAY
        and any((t.get('date') or '') >= TODAY and not t.get('soldout') for t in e.get('tickets') or [])
        and 'zaiko.io' not in urls(e) and 'livepocket' not in urls(e)]
random.seed(11242026)
pick = random.sample(pool, 30)
KEEP = ('id', 'artist', 'name', 'date', 'dateLabel', 'dateText', 'venue', 'prefecture', 'genre', 'extraGenres', 'links', 'tickets')
for g in range(2):
    part = [{k: e.get(k) for k in KEEP if k in e} for e in pick[g * 15:(g + 1) * 15]]
    json.dump(part, io.open(root + f'tmp/x1124/spot/sample_{g + 1}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
io.open(root + 'tmp/x1124/spot/ids.txt', 'w', encoding='utf-8').write(f'母数 {len(pool)}\n' + '\n'.join(f'{e["id"]} {e.get("name")}' for e in pick))
