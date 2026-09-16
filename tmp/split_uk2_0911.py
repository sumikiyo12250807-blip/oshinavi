# -*- coding: utf-8 -*-
"""受付中2バッチ目を「投入」と「既存に足す」に分ける（2026-09-11）。
  既存に足す＝8144 FREEDOM NAGOYA【限定ラバーバンド】→833（同日同名）／
             8090 TRAeLL→7601 ／ 8121 ゴホウビ→7684 ／ 8123 SunSet Swish→7692 ／ 8146 bokula.→8015
  保留＝8102 FIELDS SO GOOD（発売前の2枠の日付が読めない表記）
  （8090/8121/8123/8146 は dedup の「既存に無い窓あり」なので fresh に入っていない＝built から拾う）
使い方: python tmp/split_uk2_0911.py [--fixlabel]
  --fixlabel … 足し込み後に、会期の初日を「既存ラベルの初日」と「足した公演の初日」の早い方に直す
"""
import datetime, io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
MERGE = {8144: 833, 8090: 7601, 8121: 7684, 8123: 7692, 8146: 8015}
HOLD = {8102}
WD = '月火水木金土日'


def first_date(label):
    m = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', label or '')
    return '%s-%02d-%02d' % (m.group(1), int(m.group(2)), int(m.group(3))) if m else None


built = {e['id']: e for e in json.load(io.open('tmp/built_uk2_0911.json', encoding='utf-8-sig'))}
if '--fixlabel' in sys.argv:
    src = open('index.html', encoding='utf-8').read()
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
    ev = json.loads(m.group(2))
    by = {e['id']: e for e in ev}
    for s, d in MERGE.items():
        e = by[d]
        bf, ef = first_date(built[s].get('dateLabel')), first_date(e.get('dateLabel'))
        if bf and ef and bf < ef:
            y, mo, dd = map(int, bf.split('-'))
            new = '%d年%d月%d日(%s)' % (y, mo, dd, WD[datetime.date(y, mo, dd).weekday()])
            old = e['dateLabel']
            e['dateLabel'] = re.sub(r'^\d{4}年\d{1,2}月\d{1,2}日(\([^)]*\))?', new, old, count=1)
            print('id%s 初日を直した: %s → %s' % (d, old, e['dateLabel']))
    open('index.html', 'w', encoding='utf-8').write(src[:m.start()] + m.group(1) + json.dumps(ev, ensure_ascii=False, indent=2) + m.group(3) + src[m.end():])
    sys.exit(0)

fresh = json.load(io.open('tmp/built_uk2_0911_fresh.json', encoding='utf-8-sig'))
inj = [e for e in fresh if e['id'] not in MERGE and e['id'] not in HOLD]
mb, mc = [], []
for s, d in MERGE.items():
    e = json.loads(json.dumps(built[s]))
    url = (e.get('links') or {}).get('pia')
    for t in e['tickets']:
        t['url'] = t.get('url') or url
    e['id'] = d
    mb.append(e)
    mc.append({'newid': d, 'artist': e['artist'], 'urls': [url]})
json.dump(inj, io.open('tmp/inject_uk2_0911.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(mb, io.open('tmp/built_mergeU2_0911.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(mc, io.open('tmp/cand_mergeU2_0911.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('投入 %d件 ／ 既存に足す %d件 ／ 保留 %s' % (len(inj), len(mb), sorted(HOLD)))
