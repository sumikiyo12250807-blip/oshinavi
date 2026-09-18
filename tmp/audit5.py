# -*- coding: utf-8 -*-
"""監査その5＝落とした78件に発売日の手がかりがあるか／券種名が空の実態／その他の詰め。"""
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
reg = set()
for e in TG:
    reg |= set(re.findall(r'/events/(\d+)', json.dumps(e, ensure_ascii=False)))
skip = {}
for f in ('built_wide_0918.json', 'built_tiget_0918.json', 'built_tiget2_0918.json',
          'built_tiget3_0918.json'):
    try:
        d = json.load(io.open(ROOT + r'\tmp\\' + f, encoding='utf-8'))
    except Exception:
        continue
    for s in d.get('skipped') or []:
        skip[str(s['id'])] = s['why']

P('== A. 「枠が読めない」で落とした件に発売日の手がかりがあるか ==')
lost = [raw[i] for i in raw if i not in reg and skip.get(i) == '枠が読めない']
P('   落とした %d件' % len(lost))
c = Counter()
ex = defaultdict(list)
for r in lost:
    offs = {o['valid_from'] for o in (r.get('ld_offers') or []) if o.get('valid_from')}
    st = Counter()
    for p in r['programs']:
        if p.get('date') and p['date'] >= TODAY:
            for t in p.get('tickets') or []:
                cl = t.get('class') or ''
                st['unopened' if 'is-unopened' in cl else
                   'closed' if 'is-closed' in cl else
                   'soldout' if ('is-unavailable' in cl or 'btn-unable' in cl) else
                   'live' if 'is-available' in cl else 'unknown'] += 1
    if not sum(st.values()):
        k = '券種が1つも無い（ハーベスタが読めていない）'
    elif len(offs) == 1:
        k = '🚨JSON-LDに発売日が1つある＝救える（%s）' % ('/'.join(sorted(st)))
    elif len(offs) > 1:
        k = 'JSON-LDの発売日が食い違う（%s）' % ('/'.join(sorted(st)))
    else:
        k = 'JSON-LDにも発売日が無い（%s）' % ('/'.join(sorted(st)))
    c[k] += 1
    if len(ex[k]) < 6:
        ex[k].append('events/%s %s offs=%s' % (r['id'], (r.get('name') or '')[:28], sorted(offs)[:2]))
for k, v in c.most_common():
    P('   %s: %d件' % (k, v))
    for s in ex[k]:
        P('      %s' % s)

P()
P('== B. 登録エントリの中で落ちた枠（受付前で期間が読めない）に発売日があるか ==')
n_save, n_no = 0, 0
exs = []
for e in TG:
    ids = sorted(set(re.findall(r'/events/(\d+)', json.dumps(e, ensure_ascii=False))))
    for i in ids:
        r = raw.get(i)
        if not r:
            continue
        offs = {o['valid_from'] for o in (r.get('ld_offers') or []) if o.get('valid_from')}
        for p in r['programs']:
            if not p.get('date') or p['date'] < TODAY:
                continue
            for t in p.get('tickets') or []:
                cl = t.get('class') or ''
                per = [pp for pp in (t.get('periods') or []) if pp.get('parsed')]
                if 'is-unopened' in cl and not per:
                    if len(offs) == 1:
                        n_save += 1
                        if len(exs) < 6:
                            exs.append((e['id'], (t.get('name') or '')[:24], sorted(offs)[0]))
                    else:
                        n_no += 1
P('   受付前で期間が読めない枠 %d枠 … うちJSON-LDに発売日が1つ＝救える %d枠 / 手がかり無し %d枠'
  % (n_save + n_no, n_save, n_no))
for x in exs:
    P('      id%s 券種=%s 発売日=%s' % x)

P()
P('== C. 生データの券種名が空の実態 ==')
tot, empt = 0, 0
per_ev = Counter()
for r in raw.values():
    for p in r['programs']:
        for t in p.get('tickets') or []:
            tot += 1
            if not (t.get('name') or '').strip():
                empt += 1
                per_ev[r['id']] += 1
P('   生データの券種 %d枠中 名前が空 %d枠（%.1f%%）／関わるイベント %d件'
  % (tot, empt, 100.0 * empt / tot, len(per_ev)))
multi = [k for k, v in per_ev.items() if v > 1]
P('   1イベントに空名の券種が2つ以上 = %d件（＝バッジが同じ名前で並ぶ原因）' % len(multi))
for k in multi[:5]:
    r = raw[k]
    P('      events/%s %s 空名%d枠 / 全%d枠' % (k, (r.get('name') or '')[:24], per_ev[k],
                                            sum(len(p.get('tickets') or []) for p in r['programs'])))

P()
P('== D. 券種名が空の枠の値段（見分けの材料になるか） ==')
withp = 0
for r in raw.values():
    for p in r['programs']:
        for t in p.get('tickets') or []:
            if not (t.get('name') or '').strip() and t.get('price'):
                withp += 1
P('   空名の枠のうち値段が取れている %d枠' % withp)

P()
P('== E. いま登録にある「チケット」バッジが同じカードに2つ以上 ==')
n = 0
for e in TG:
    lab = [re.sub(r'（[^（）]*\d{1,2}/\d{1,2}公演）.*$', '', t['type']).strip() for t in e['tickets']]
    if lab.count('チケット') > 1:
        n += 1
        if n <= 6:
            P('      id%s %s → 「チケット」%d枠' % (e['id'], e['name'][:26], lab.count('チケット')))
P('   %d件' % n)

io.open(ROOT + r'\tmp\audit5_out.txt', 'w', encoding='utf-8').write('\n'.join(OUT))
