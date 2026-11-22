import sys, json, datetime
sys.path.insert(0, 'C:/Users/user/oshinavi/tools')
import compact_events as C
E = C.load(open('C:/Users/user/oshinavi/index.html', encoding='utf-8', newline='').read())
ids = list(range(47748, 47760)) + [3533, 54916, 50717, 45549, 52446, 52448, 52452, 37803, 53851, 26864, 11080, 37656,
       44718, 36186, 50809, 55613, 56476, 56514, 56527, 45511, 55244, 54678, 54075, 57105]
out = open('C:/Users/user/oshinavi/tmp/x1122/x/fcx_detail.txt', 'w', encoding='utf-8')
by = {e.get('id'): e for e in E}
for i in ids:
    e = by.get(i)
    if not e:
        out.write('### %s NOT FOUND\n' % i)
        continue
    tk = e.get('tickets') or []
    if i == 3533:
        tk = [t for t in tk if '福岡' in str(t.get('type'))]
    out.write('### %s %s | %s | %s | %s | %s\n' % (i, e.get('artist'), e.get('name'), e.get('venue'), e.get('dateLabel'), e.get('prefecture')))
    for t in tk[:12]:
        out.write('   ' + json.dumps(t, ensure_ascii=False) + '\n')
out.write('\n### irei\n')
for e in E:
    if 'いれいす' in str(e.get('artist')) + str(e.get('name')):
        out.write('%s %s | %s | %s | %s\n' % (e.get('id'), e.get('name'), e.get('venue'), e.get('dateLabel'), e.get('prefecture')))
        for t in e.get('tickets') or []:
            out.write('   ' + json.dumps(t, ensure_ascii=False) + '\n')
out.write('\n### weekdays\n')
W = '月火水木金土日'
for d in ['2026-11-23', '2026-11-24', '2026-11-25', '2026-11-26', '2026-12-04', '2026-12-06', '2026-12-07', '2026-12-13', '2026-12-24', '2026-12-26', '2026-12-29',
          '2026-09-22', '2027-01-22', '2027-01-27', '2027-02-06', '2027-02-14', '2027-02-16', '2027-03-06', '2027-03-16', '2027-04-08', '2027-04-30', '2027-05-02']:
    out.write('%s %s\n' % (d, W[datetime.date.fromisoformat(d).weekday()]))
out.close()
