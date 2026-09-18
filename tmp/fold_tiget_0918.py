# -*- coding: utf-8 -*-
"""TIGETの「日付を名前の頭に付けて1日1ページ」型を1エントリに畳む（2026-09-18 ユーザー指示）。

ユーザー「MY.st たくさんあるからひとつにたたんで」「Studio Lこれもたためる　全部確認して」

🚨畳むのは**公演日が全部バラバラな組だけ**＝連日公演・シリーズ。
   同じ日に複数エントリある組は**部ごと・対バンごと・出演者ごとの別ページ**なので畳まない
   （ブイ×カケのチェキ撮影会は出演者が違う＝畳むと片方の名前で探した人が見つけられない）。
   決まり＝[[feedback_tour_consolidate]]／畳まない側は[[feedback_sports_home_away_never_merge]]と同じ理屈。

  python tmp/fold_tiget_0918.py            … 調べるだけ
  python tmp/fold_tiget_0918.py --apply
"""
import re, json, io, sys, unicodedata, datetime

APPLY = '--apply' in sys.argv
WD = '月火水木金土日'
DATEHEAD = re.compile(r'^\s*(?:\d{4}年)?\d{1,2}[月/]\d{1,2}日?\s*(?:\([^)]*\))?\s*(?:\d{1,2}[:：]\d{2})?\s*[-–—/｜|]?\s*')


def core(nm):
    s = DATEHEAD.sub('', nm or '').strip()
    s = unicodedata.normalize('NFKC', s).lower()
    return re.sub(r'[\s　・･,，.。!！?？~〜\-—–_/／\(\)（）\[\]【】「」『』"\'’💐☆★]', '', s)


def jp(iso):
    y, m, d = [int(x) for x in iso.split('-')]
    return '%d年%d月%d日(%s)' % (y, m, d, WD[datetime.date(y, m, d).weekday()])


h = io.open('index.html', encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in h else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

groups = {}
for e in EVENTS:
    if 'tiget.net' not in json.dumps(e, ensure_ascii=False):
        continue
    groups.setdefault((core(e.get('name')), e.get('venue') or ''), []).append(e)

o = io.open('tmp/fold_tiget_0918.txt', 'w', encoding='utf-8')
fold, keepsep = [], []
for k, v in groups.items():
    if len(v) < 2:
        continue
    days = [x.get('date') for x in v]
    (fold if len(set(days)) == len(days) else keepsep).append((k, v))

o.write('畳む %d組（%d件→%d件）／畳まない %d組（%d件）\n'
        % (len(fold), sum(len(v) for _, v in fold), len(fold),
           len(keepsep), sum(len(v) for _, v in keepsep)))
o.write('\n=== 畳まない（同じ日に複数＝部ごと・出演者ごとの別ページ）===\n')
for k, v in sorted(keepsep, key=lambda kv: -len(kv[1])):
    o.write('  %d件 %s ｜%s ｜公演%s\n' % (len(v), (v[0].get('name') or '')[:40], k[1][:22],
                                          sorted({x.get('date') for x in v})))

drop, arrdrop = [], set()
o.write('\n=== 畳む ===\n')
for k, v in sorted(fold, key=lambda kv: -len(kv[1])):
    v.sort(key=lambda x: (x.get('date') or '', x['id']))
    keep = v[0]
    name = DATEHEAD.sub('', keep.get('name') or '').strip() or keep.get('name')
    tickets = []
    for x in v:
        tickets += x['tickets']
    first, last = v[0]['date'], v[-1]['date']
    o.write('  %d件→1 ｜%s ｜%s ｜%s〜%s ｜残すid%d 消すid%s\n'
            % (len(v), name[:42], k[1][:22], first, last, keep['id'],
               ','.join(str(x['id']) for x in v[1:])))
    if APPLY:
        keep['name'] = name
        keep['tickets'] = tickets
        keep['date'] = last
        keep['dateLabel'] = ('%s〜%s %s' % (jp(first), jp(last), keep.get('prefecture') or '')).strip() \
            if first != last else ('%s %s' % (jp(first), keep.get('prefecture') or '')).strip()
        for x in v[1:]:
            drop.append(x['id'])
            arrdrop.add(x['id'])

if APPLY:
    EVENTS = [e for e in EVENTS if e['id'] not in arrdrop]
    mo = re.search(r'(NEW_ORDER\s*=\s*)\[([0-9,\s]*)\]', h)
    arr = [int(x) for x in re.findall(r'\d+', mo.group(2)) if int(x) not in arrdrop]
    h2 = re.sub(r'(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]', r'\g<1>' + '[' + ', '.join(map(str, arr)) + ']', h, count=1)
    m2 = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h2, re.S)
    io.open('index.html', 'w', encoding='utf-8', newline='').write(
        h2[:m2.start()] + m2.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
        + m2.group(3) + h2[m2.end():])
    pool = {e['id'] for e in EVENTS if e.get('genre') == 'new'}
    o.write('\n消した %d件 / EVENTS %d件 / プール %d件 / NEW_ORDER %d件 / 一致=%s\n'
            % (len(drop), len(EVENTS), len(pool), len(arr), pool == set(arr)))
o.close()
