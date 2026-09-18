# -*- coding: utf-8 -*-
import io, json, re
from collections import Counter, defaultdict
OUT = []


def P(s=''):
    OUT.append(s)


TODAY = '2026-09-18'
ROOT = r'C:\Users\user\oshinavi'
src = io.open(ROOT + r'\index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
TG = [e for e in EVENTS if 11317 <= e.get('id', 0) <= 13230]
raw = {}
for f in ('tiget_yt_vt2_0918.json', 'tiget_wide_0918.json'):
    d = json.load(io.open(ROOT + r'\tmp\\' + f, encoding='utf-8'))
    for ev in d['events']:
        raw.setdefault(str(ev['id']), ev)


def ids_of(e):
    return sorted(set(re.findall(r'/events/(\d+)', json.dumps(e, ensure_ascii=False))))


P('== A. 同じ日に公演が2つ以上（昼の部・夜の部）＝開場時刻がバッジから落ちている ==')
n_ev, n_slot = 0, 0
ex = []
for e in TG:
    for i in ids_of(e):
        r = raw.get(i)
        if not r:
            continue
        c = Counter(p['date'] for p in r['programs'] if p.get('date') and p['date'] >= TODAY)
        multi = [d for d, k in c.items() if k > 1]
        if multi:
            n_ev += 1
            n_slot += sum(len(p.get('tickets') or []) for p in r['programs']
                          if p.get('date') in multi)
            if len(ex) < 6:
                ex.append((e['id'], (e['name'] or '')[:26], multi[0],
                           [p.get('datetime_text', '')[:24] for p in r['programs']
                            if p.get('date') in multi][:3]))
            break
P('   エントリ %d件 / 関わる枠 %d枠' % (n_ev, n_slot))
for x in ex:
    P('      id%s %s %s 公演の見出し=%s' % x)

P()
P('== B. 畳んだエントリの元ページ名（別物を畳んでいないか） ==')
for e in TG:
    idl = ids_of(e)
    if len(idl) < 2:
        continue
    names = [((raw.get(i) or {}).get('name') or '?') for i in idl]
    P('   id%s 「%s」← %d ページ' % (e['id'], e['name'][:30], len(idl)))
    for i, nm in list(zip(idl, names))[:6]:
        P('        events/%s %s' % (i, nm[:52]))

P()
P('== C. 発売日が1年以上前の枠（主催者の常設ページ・雛形の疑い） ==')
old = [(e['id'], e['name'][:26], t['type'], t.get('startDate'), e['date'])
       for e in TG for t in e['tickets'] if (t.get('startDate') or '9999') < '2025-09-18']
P('   %d枠 / エントリ %d件' % (len(old), len({x[0] for x in old})))
for x in old[:10]:
    P('      id%s %s / %s start=%s 公演=%s' % x)
P()
P('   発売日が半年以上前の枠: %d枠'
  % len([1 for e in TG for t in e['tickets'] if (t.get('startDate') or '9999') < '2026-03-18']))

P()
P('== D. 枠がまとめられた（同じ見た目で値段も同じ）ケースの元データ ==')
r = raw.get('516086')
if r:
    for p in r['programs']:
        P('   events/516086 公演%s %s' % (p.get('date'), (p.get('datetime_text') or '')[:30]))
        for t in p.get('tickets') or []:
            P('      %r price=%s class=%s periods=%s' % (t.get('name'), t.get('price'),
                                                         t.get('class'),
                                                         [pp.get('text') for pp in (t.get('periods') or [])]))

P()
P('== E. いまの枠数の内訳（生データ→登録） ==')
tot_raw, tot_reg = 0, 0
diff = []
for e in TG:
    n = 0
    for i in ids_of(e):
        r2 = raw.get(i)
        if not r2:
            continue
        for p in r2['programs']:
            if p.get('date') and p['date'] >= TODAY:
                n += len(p.get('tickets') or [])
    tot_raw += n
    tot_reg += len(e['tickets'])
    if n != len(e['tickets']):
        diff.append((e['id'], e['name'][:24], n, len(e['tickets'])))
P('   生データの券種（今日以降の公演分） %d枠 → 登録 %d枠 / 数が違うエントリ %d件'
  % (tot_raw, tot_reg, len(diff)))
for x in sorted(diff, key=lambda y: y[2] - y[3], reverse=True)[:12]:
    P('      id%s %s 生%d → 登録%d' % x)

io.open(ROOT + r'\tmp\audit8_out.txt', 'w', encoding='utf-8').write('\n'.join(OUT))
