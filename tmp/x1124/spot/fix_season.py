# -*- coding: utf-8 -*-
# 57757 と同じ型（シーズンシート・席パック＝器の日付に試合なし）の載っている5件を、試合に見えない形に（鍵の中）
import io, os, re, sys, time
os.chdir('C:/Users/user/oshinavi')
sys.path.insert(0, 'tools')
import compact_events as C
LK = 'tmp/x1112/index.lock'
IDS = (56314, 56435, 57106, 57107, 57758)
out = io.open('tmp/x1124/spot/fix_season.txt', 'w', encoding='utf-8')
while True:
    try:
        fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'fix_season24'); os.close(fd); break
    except FileExistsError:
        time.sleep(15)
try:
    t = io.open('index.html', encoding='utf-8', newline='').read()
    E = C.load(t)
    by = {x['id']: x for x in E}
    for i in IDS:
        e = by[i]
        old = dict(artist=e.get('artist'), name=e['name'], dateLabel=e.get('dateLabel'), date=e['date'], types=[x['type'] for x in e['tickets']])
        team = re.sub(r'\s+', ' ', (e.get('artist') or '').split('／')[0]).strip()
        team = re.sub(r'\s*(ハーフシーズンシート|20\d\d-\d\dシーズンチケット.*)$', '', team).strip() or team
        nm = re.sub(r'^.+?対.+?（.*?）\s*', '', e['name']).strip()
        if team not in nm:
            nm = team + ' ' + nm
        e['artist'] = team
        e['name'] = re.sub(r'\s+', ' ', nm)
        e['dateLabel'] = 'ホームゲームの席のセット販売（%s）' % (e.get('prefecture') or e.get('venue') or '')
        for x in e['tickets']:
            x['type'] = re.sub(r'^([^（]*)（[^）]*公演）', r'\1（シーズンシート・席のセット）', x['type'])
        e['date'] = max(x['date'] for x in e['tickets'])
        e['verifiedAt'] = '2026-11-24'
        out.write('%d %s\n   → artist=%s name=%s dateLabel=%s date=%s types=%s\n' % (i, old, e['artist'], e['name'], e['dateLabel'], e['date'], [x['type'] for x in e['tickets']]))
    s, end, _ = C.locate(t)
    t = t[:s] + C.dump(E, True, '\r\n') + t[end:]
    io.open('index.html', 'w', encoding='utf-8', newline='').write(t)
finally:
    os.remove(LK)
out.close()
print('ok')
