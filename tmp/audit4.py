# -*- coding: utf-8 -*-
"""監査その4＝落ちた93件の本当の理由／12件の券種ゼロ／県が空の実態／出す側の券種。"""
import io, json, re, sys
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
reg_ids = set()
for e in TG:
    reg_ids |= set(re.findall(r'/events/(\d+)', json.dumps(e, ensure_ascii=False)))

# 組み上がりのskipped理由（道具が自分で書いたもの）
skip = {}
for f in ('built_wide_0918.json', 'built_tiget_0918.json', 'built_tiget2_0918.json',
          'built_tiget3_0918.json'):
    try:
        d = json.load(io.open(ROOT + r'\tmp\\' + f, encoding='utf-8'))
    except Exception:
        continue
    for s in d.get('skipped') or []:
        skip[str(s['id'])] = s['why']
P('== A. 道具が「載せない」と判断した理由の内訳（組み上がりのskipped） ==')
for k, v in Counter(skip.values()).most_common():
    P('   %s: %d件' % (k, v))

miss = [i for i in raw if i not in reg_ids]
P()
P('== B. 生データ %d件のうち登録に無い %d件の行き先 ==' % (len(raw), len(miss)))
c = Counter()
ex = defaultdict(list)
inj = io.open(ROOT + r'\tmp\inject_tiget_report.txt', encoding='utf-8').read()
for i in miss:
    r = raw[i]
    if i in skip:
        k = '道具が落とした：' + skip[i]
    elif ('/events/%s' % i) in inj:
        m = re.search(r'\n  (.{0,60}) … ([^\n]*)\n    https://tiget\.net/events/%s' % i, inj)
        k = '投入で保留：' + (m.group(2) if m else '要確認')
    else:
        k = '🚨説明できない'
    c[k] += 1
    if len(ex[k]) < 5:
        ex[k].append('events/%s %s' % (i, (r.get('name') or '')[:34]))
for k, v in c.most_common():
    P('   %s: %d件' % (k, v))
    for s in ex[k]:
        P('      %s' % s)

# 券種ゼロの生データ（ハーベスタの読み落とし疑い）
P()
P('== C. 生データで券種が1つも取れていないイベント ==')
zero = [r for r in raw.values() if not any(p.get('tickets') for p in r['programs'])]
P('   %d件（うち statuses が空でない＝一覧では売っていた: %d件）'
  % (len(zero), sum(1 for r in zero if r.get('statuses'))))
for r in zero[:14]:
    P('      events/%s %-30s programs=%d statuses=%s list=%s'
      % (r['id'], (r.get('name') or '')[:30], len(r['programs']),
         (r.get('statuses') or [])[:2], (r.get('list') or {}).get('status_tag')))

# 県が空の実態
P()
P('== D. 県が空 281件の実態（生データに何が入っているか） ==')
nop = [e for e in TG if not (e.get('prefecture') or '')]
c2 = Counter()
for e in nop:
    ids = sorted(set(re.findall(r'/events/(\d+)', json.dumps(e.get('links'), ensure_ascii=False))))
    r = raw.get(ids[0]) if ids else None
    if not r:
        c2['生データが無い'] += 1
        continue
    a = (r.get('list') or {}).get('area')
    c2['ld_region=%r list.area=%r' % (r.get('ld_region'), a)] += 1
for k, v in c2.most_common(8):
    P('   %s : %d件' % (k, v))
P('   ＝県が空の理由は「TIGET側にも県が無い」（推測で県を当てていない＝方針どおり）')

# 出す側の券種（辞書を広げて棚卸し）
P()
P('== E. 出す側・推し活でない券種の棚卸し（券種名を広い辞書で当てる） ==')
WORDS = ['出店', 'ブース', '委託', '即売', 'エントリー', '参加エントリ', '駐車', '案内登録',
         '先行案内', '出展', 'スペース', 'フリマ', '物販枠', '出演', '応募', '登録のみ', '賛助',
         '協賛', '広告', '寄付', '投げ銭', 'サポーター', '差し入れ']
hit = defaultdict(list)
for e in TG:
    for t in e['tickets']:
        base = re.sub(r'（[^（）]*\d{1,2}/\d{1,2}公演）.*$', '', t['type'])
        for w in WORDS:
            if w in base:
                hit[w].append((e['id'], base[:34]))
for w in WORDS:
    if hit[w]:
        P('   「%s」: %d枠  例=%s' % (w, len(hit[w]), hit[w][:3]))

# 「チケット」に倒れた枠の原因
P()
P('== F. 券種名が「チケット」に倒れた枠の原因（生データの元の名前） ==')
c3 = Counter()
ex3 = defaultdict(list)
for e in TG:
    ids = sorted(set(re.findall(r'/events/(\d+)', json.dumps(e, ensure_ascii=False))))
    names = []
    for i in ids:
        r = raw.get(i)
        if not r:
            continue
        for p in r['programs']:
            if p.get('date') and p['date'] >= TODAY:
                names += [t.get('name') or '' for t in (p.get('tickets') or [])]
    n_fall = sum(1 for t in e['tickets']
                 if re.sub(r'（[^（）]*\d{1,2}/\d{1,2}公演）.*$', '', t['type']).strip() in ('チケット',))
    if not n_fall:
        continue
    for nm in names:
        s = (nm or '').strip()
        if re.search(r'開場|開演|終演', s):
            k = '①進行案内（開場/開演/終演）が名前に入っている'
        elif not s:
            k = '②名前が空'
        elif s in ('チケット', 'チケット代'):
            k = '③TIGET側が本当に「チケット」'
        else:
            continue
        c3[k] += 1
        if len(ex3[k]) < 4:
            ex3[k].append((e['id'], s[:40]))
for k, v in c3.most_common():
    P('   %s: %d枠' % (k, v))
    for x in ex3[k]:
        P('      id%s 元の名前=%s' % x)

io.open(ROOT + r'\tmp\audit4_out.txt', 'w', encoding='utf-8').write('\n'.join(OUT))
