# -*- coding: utf-8 -*-
"""監査その10＝落ちた483枠の内訳と、いちばん困る形（売切れだけのカード）。"""
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


def st(cls):
    c = cls or ''
    if 'is-unopened' in c:
        return 'unopened'
    if 'is-closed' in c:
        return 'closed'
    if 'is-unavailable' in c or 'btn-unable' in c:
        return 'soldout'
    if 'is-available' in c:
        return 'live'
    return 'unknown'


lost = Counter()
worst = []
dup_by_time = Counter()
for e in TG:
    ids = sorted(set(re.findall(r'/events/(\d+)', json.dumps(e, ensure_ascii=False))))
    rt = []
    offs = set()
    for i in ids:
        r = raw.get(i)
        if not r:
            continue
        offs |= {o['valid_from'] for o in (r.get('ld_offers') or []) if o.get('valid_from')}
        for p in r['programs']:
            if p.get('date') and p['date'] >= TODAY:
                for t in p.get('tickets') or []:
                    rt.append((p.get('datetime_text') or '', t))
    gap = len(rt) - len(e['tickets'])
    if gap <= 0:
        continue
    n_unop_noper = sum(1 for _, t in rt if st(t.get('class')) == 'unopened'
                       and not [pp for pp in (t.get('periods') or []) if pp.get('parsed')])
    n_live_noper = sum(1 for _, t in rt if st(t.get('class')) == 'live'
                       and not [pp for pp in (t.get('periods') or []) if pp.get('parsed')])
    n_unknown = sum(1 for _, t in rt if st(t.get('class')) == 'unknown')
    # 畳まれた疑い＝同じ（名前,値段,状態,期間）が複数
    k = Counter(((t.get('name') or ''), t.get('price'), st(t.get('class')),
                 tuple(sorted(pp.get('text') or '' for pp in (t.get('periods') or []))))
                for _, t in rt)
    n_same = sum(v - 1 for v in k.values() if v > 1)
    # そのうち開場時刻が違う＝本当は別枠
    for key, v in k.items():
        if v > 1:
            times = {dt for dt, t in rt if ((t.get('name') or ''), t.get('price'),
                                            st(t.get('class')),
                                            tuple(sorted(pp.get('text') or '' for pp in (t.get('periods') or [])))) == key}
            if len(times) > 1:
                dup_by_time[e['id']] += v - 1
    lost['受付前で受付期間が無い（落とす）'] += min(gap, n_unop_noper)
    lost['当日払いで発売日も無い（落とす）'] += n_live_noper if not offs else 0
    lost['売り状態が読めない（落とす）'] += n_unknown
    lost['同じ見た目だから畳んだ'] += n_same
    if all(t.get('soldout') for t in e['tickets']) and n_unop_noper:
        worst.append((e['id'], e['name'][:30], len(e['tickets']), n_unop_noper))

P('== 落ちた枠の内訳（重なりあり・目安） ==')
for k, v in lost.most_common():
    P('   %s: %d枠' % (k, v))
P('   生4396 → 登録3913 ＝ %d枠が画面に出ていない' % (4396 - 3913))
P()
P('== 🚨いちばん困る形＝カードに出るのが売切れ/販売終了だけなのに、実は発売前の枠がある ==')
P('   %d件' % len(worst))
for x in worst[:10]:
    P('      id%s %s 登録%d枠（全部売切れ表示）／落とした受付前の枠%d' % x)
P()
P('== 開場時刻が違うのに同じ見た目として畳まれた（本当は別枠） ==')
P('   エントリ %d件 / 畳まれた枠 %d枠' % (len(dup_by_time), sum(dup_by_time.values())))
for i, v in dup_by_time.most_common(8):
    P('      id%s %d枠' % (i, v))

# 売切れだけのカード130件の内訳
only = [e for e in TG if e['tickets'] and all(t.get('soldout') for t in e['tickets'])]
P()
P('== 売切れ・販売終了の印だけのカード %d件（方針どおり載せる／ただし上の worst はもったいない） ==' % len(only))
io.open(ROOT + r'\tmp\audit10_out.txt', 'w', encoding='utf-8').write('\n'.join(OUT))
