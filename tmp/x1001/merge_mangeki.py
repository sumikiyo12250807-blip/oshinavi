# -*- coding: utf-8 -*-
"""神保町マンゲキお笑いライブ（FANY・1公演1エントリ）62件を「10月公演」「11月公演」の2枚に畳む
 ユーザー「神保町マンゲキお笑いライブ　まとめれる　日付は発売と公演で分けないと　かなりの量だから」(10/1夜)
 ＝発売（10月公演＝発売中／11月公演＝10/5発売）と公演月で分ける。枠は全部残す（飛び先は公演ごとのFANY）。
 同じ日に2公演ある日は、券種の（東京 M/D公演）に開演の時刻を入れて見分ける。_fanyEvents に元のFANYのイベント番号を全部持たせる（番人用）。
使い方: python tmp/x1001/merge_mangeki.py [--apply] → merge_mangeki.txt"""
import io, json, re, sys, collections
root = 'C:/Users/user/oshinavi/'
APPLY = '--apply' in sys.argv
WD = '月火水木金土日'
src = io.open(root + 'index.html', encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[)', src)
st = m.start(1)
E, end = json.JSONDecoder().raw_decode(src, st)
hit = [e for e in E if e.get('name') == '神保町マンゲキお笑いライブ']
out = io.open(root + 'tmp/x1001/merge_mangeki.txt', 'w', encoding='utf-8')
import datetime
def jp(iso):
    y, mo, d = map(int, iso.split('-'))
    return '%d年%d月%d日(%s)' % (y, mo, d, WD[datetime.date(y, mo, d).weekday()])
gone = set()
for month in sorted({e['date'][:7] for e in hit}):
    g = sorted([e for e in hit if e['date'][:7] == month], key=lambda e: (e['date'], e['dateLabel'], e['id']))
    head = min(g, key=lambda e: e['id'])
    perday = collections.Counter(e['date'] for e in g)
    tks, fids, genres = [], [], []
    for e in g:
        tm = re.search(r'(\d{1,2}:\d{2})開演', e.get('dateLabel') or '')
        fu = (e.get('links') or {}).get('fany') or ''
        fm = re.search(r'detail/(\d+)', fu)
        if fm:
            fids.append(fm.group(1))
        for gg in [e.get('genre')] + list(e.get('extraGenres') or []):
            if gg and gg != 'new' and gg not in genres:
                genres.append(gg)
        for t in e['tickets']:
            n = dict(t)
            if perday[e['date']] > 1 and tm:
                n['type'] = re.sub(r'（([^（）]*?\d{1,2}/\d{1,2})公演）', lambda x: '（%s %s公演）' % (x.group(1), tm.group(1)), n['type'], count=1)
            if not n.get('url') and fu:
                n['url'] = fu
            tks.append(n)
    first, last = g[0]['date'], g[-1]['date']
    mo = int(month[5:])
    head['name'] = '神保町マンゲキお笑いライブ（%d月公演）' % mo
    head['dateLabel'] = '%s〜%s 東京' % (jp(first), jp(last))
    head['date'] = last
    head['tickets'] = tks
    head['_fanyEvents'] = fids
    head['artist'] = '神保町マンゲキお笑いライブ'
    if head.get('genre') == 'new':
        head['_genre'] = genres[0] if genres else head.get('_genre')
    else:
        head['genre'] = genres[0]
        if genres[1:]:
            head['extraGenres'] = genres[1:]
    for e in g:
        if e is not head:
            gone.add(e['id'])
    out.write('%s → id%d ＜ %d件 ／ 枠%d ／ 同日2公演の日 %d ／ %s\n' % (head['name'], head['id'], len(g), len(tks),
              sum(1 for v in perday.values() if v > 1), head['dateLabel']))
out.write('欠番 %d\n' % len(gone))
if APPLY:
    E2 = [e for e in E if e['id'] not in gone]
    body = '[\n' + ',\n'.join(json.dumps(x, ensure_ascii=False, separators=(',', ':')) for x in E2) + '\n]'
    text = src[:st] + body.replace('\n', '\r\n') + src[end:]
    mo_ = re.search(r'NEW_ORDER\s*=\s*\[([^\]]*)\]', text)
    ids = [x.strip() for x in mo_.group(1).split(',') if x.strip() and int(x.strip()) not in gone]
    text = text[:mo_.start(1)] + ','.join(ids) + text[mo_.end(1):]
    io.open(root + 'index.html', 'wb').write(text.encode('utf-8'))
    out.write('書いた\n')
