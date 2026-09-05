# -*- coding: utf-8 -*-
"""既存ツアー4件に、まだ載っていない公演の枠を足す（2026-09-05・e+受付中ぶん）。

足すだけで既存の枠は1つも触らない＝飛び先の破壊が起きない。
会場・県・dateLabel は、足した公演を反映して作り直す。

🚨 index.html は newline='' で読み書き＋json.dumps の改行を元の改行コードへ置換（CRLFを壊さない）。
"""
import json, io, re, datetime

PATH = 'index.html'
TODAY = datetime.date.today().isoformat()
WD = '月火水木金土日'

h = io.open(PATH, encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
events = json.loads(m.group(2))
by = {e['id']: e for e in events}

merge = json.load(io.open('tmp/batch2_merge_0905.json', encoding='utf-8'))
built = {b['id']: b for b in json.load(io.open('tmp/eplus_batch2_0905.json', encoding='utf-8'))}
SRC = {5879: 6958, 5251: 6980, 3892: 6989, 579: 6994}

log = []
for tid_s, adds in merge.items():
    tid = int(tid_s)
    e = by[tid]
    before = len(e['tickets'])
    have = {(t.get('type'), t.get('date')) for t in e['tickets']}
    added = 0
    for t in adds:
        if (t.get('type'), t.get('date')) in have:
            continue
        e['tickets'].append(t)
        added += 1
    # 会場＝候補側の会場を取り込んでユニオンにする
    b = built[SRC[tid]]

    def venues(x):
        v = re.sub(r'^全国ツアー（|）$', '', x.get('venue') or '')
        return [s for s in re.split(r'[／]', v) if s.strip()]

    vs = venues(e)
    for v in venues(b):
        if v not in vs:
            vs.append(v)
    e['venue'] = ('全国ツアー（%s）' % '／'.join(vs)) if len(vs) > 1 else (vs[0] if vs else e.get('venue'))
    # 公演日の範囲を作り直す（tickets の「M/D公演」から）
    days = set()
    for t in e['tickets']:
        for mm in re.finditer(r'(?:(R\d)年\s*)?(\d{1,2})/(\d{1,2})公演', t.get('type') or ''):
            y = 2027 if mm.group(1) else 2026
            days.add(datetime.date(y, int(mm.group(2)), int(mm.group(3))))
    if days:
        lo, hi = min(days), max(days)
        e['date'] = hi.isoformat()

        def jp(d):
            return '%d年%d月%d日(%s)' % (d.year, d.month, d.day, WD[d.weekday()])
        e['dateLabel'] = (jp(lo) + '〜' + jp(hi) + ' 全国ツアー') if lo != hi else (jp(lo) + ' ' + (e.get('prefecture') or ''))
    e['verified'] = True
    e['verifiedAt'] = TODAY
    log.append('id%d: tickets %d -> %d (+%d) venues=%d date=%s'
               % (tid, before, len(e['tickets']), added, len(vs), e['date']))

bak = 'index.html.bak_0905_merge2'
io.open(bak, 'w', encoding='utf-8', newline='').write(h)
NL = '\r\n' if '\r\n' in h else '\n'
arr = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', NL)
io.open(PATH, 'w', encoding='utf-8', newline='').write(
    h[:m.start()] + m.group(1) + arr + m.group(3) + h[m.end():])
print('\n'.join(log))
print('backup=%s' % bak)
