import sys, json, re, datetime
sys.path.insert(0, 'C:/Users/user/oshinavi/tools')
import compact_events as C
E = C.load(open('C:/Users/user/oshinavi/index.html', encoding='utf-8', newline='').read())
out = open('C:/Users/user/oshinavi/tmp/x1122/x/fcx2_count.txt', 'w', encoding='utf-8')
W = '月火水木金土日'
# sumo
out.write('### sumo\n')
for e in E:
    s = str(e.get('artist')) + str(e.get('name'))
    if '相撲' in s or '巡業' in s:
        out.write('%s | %s | %s | %s | %s | %s | %s\n' % (e.get('id'), e.get('artist'), e.get('name'), e.get('date'), e.get('dateLabel'), e.get('venue'), e.get('prefecture')))
        for t in e.get('tickets') or []:
            out.write('   ' + json.dumps(t, ensure_ascii=False) + '\n')
# per date/genre distinct events (by id + rough line key)
D = json.load(open('C:/Users/user/oshinavi/tmp/x1122/x/fcx_dump.json', encoding='utf-8'))
out.write('\n### date/genre ids\n')
agg = {}
for r in D:
    t = r['t']
    sd = str(t.get('startDate') or '')
    m = re.search(r'(\d\d?)/(\d\d?) ?(\d\d?:\d\d)発売', str(t.get('type')))
    if m:
        sd = '2026-%02d-%02d' % (int(m.group(1)), int(m.group(2)))
    key = (sd[:10], r['genre'])
    agg.setdefault(key, {})
    agg[key].setdefault(r['id'], str(r['artist'])[:30])
for k in sorted(agg):
    out.write('%s %s n=%d : %s\n' % (k[0], k[1], len(agg[k]), ' / '.join('%s:%s' % (i, a) for i, a in agg[k].items())))
for d in ['2026-11-30', '2026-12-03', '2026-12-07', '2026-12-08', '2026-12-09', '2026-12-20', '2026-11-29', '2026-12-02', '2026-12-04', '2026-12-06']:
    out.write('%s %s\n' % (d, W[datetime.date.fromisoformat(d).weekday()]))
out.close()
