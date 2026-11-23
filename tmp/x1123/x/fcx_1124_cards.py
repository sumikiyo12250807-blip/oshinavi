import sys, json, datetime
sys.path.insert(0, 'C:/Users/user/oshinavi/tools')
import compact_events as C
E = C.load(open('C:/Users/user/oshinavi/index.html', encoding='utf-8', newline='').read())
IDS = {56015, 5400, 55686, 37424, 40647, 56755, 56764, 56758, 56772, 49238, 56974, 54075, 53841, 45930}
with open('C:/Users/user/oshinavi/tmp/x1123/x/fcx_1124_cards.txt', 'w', encoding='utf-8') as f:
    for e in E:
        if e.get('id') in IDS:
            d = {k: e.get(k) for k in ('id', 'name', 'artist', 'date', 'dateLabel', 'venue', 'prefecture', 'price', 'links')}
            d['tickets'] = [t for t in e.get('tickets', []) if str(t.get('startDate', ''))[:10] in ('2026-11-24',) or e.get('id') in (56015,)]
            f.write(json.dumps(d, ensure_ascii=False) + '\n')
    f.write('\n# 曜日\n')
    for s in ['2026-11-24', '2026-11-25', '2026-11-26', '2026-11-30', '2026-12-01', '2026-12-02', '2026-12-03',
              '2027-01-05', '2027-01-14', '2027-01-15', '2027-01-23', '2027-01-24', '2027-02-20', '2027-02-24',
              '2027-03-06', '2027-03-13', '2027-03-27']:
        dt = datetime.date.fromisoformat(s)
        f.write(s + ' ' + '月火水木金土日'[dt.weekday()] + '\n')
print('ok')
