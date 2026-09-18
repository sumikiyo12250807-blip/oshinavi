# -*- coding: utf-8 -*-
"""監査その3＝畳み漏れ・畳み過ぎ・落とした枠の内訳・過去締切の内訳・その他。"""
import io, json, re, sys, datetime, unicodedata
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


def eids(e):
    return sorted(set(re.findall(r'/events/(\d+)', json.dumps(e, ensure_ascii=False))))


# --- A. 過去締切の内訳 ---
P('== A. 枠のdateが今日より前の252枠の内訳 ==')
c = Counter()
ex = defaultdict(list)
for e in TG:
    for t in e['tickets']:
        if (t.get('date') or '9999') < TODAY:
            k = ('販売終了(saleEnded)' if t.get('saleEnded') else
                 '売切れ(soldout)' if t.get('soldout') else
                 '🚨印なし＝画面から黙って消える')
            c[k] += 1
            if len(ex[k]) < 4:
                ex[k].append((e['id'], t['type'], t['date']))
for k, v in c.most_common():
    P('   %s: %d枠' % (k, v))
    for x in ex[k]:
        P('      id%s %s (date=%s)' % x)

# --- B. 締切が公演日より後 ---
P()
P('== B. 締切が公演日より後（公演日で締めていない） ==')
b = [(e['id'], t['type'], t['date'], e['date'], bool(t.get('soldout')))
     for e in TG for t in e['tickets']
     if (t.get('date') or '') > e['date'] and not t.get('saleEndUnknown')]
P('   %d枠 / エントリ %d件（うち売切・終了の印つき %d枠）'
  % (len(b), len({x[0] for x in b}), sum(1 for x in b if x[4])))
for x in b[:10]:
    P('      id%s %s 締切=%s 公演=%s soldout=%s' % x)

# --- C. 同じ公演名が複数エントリに散らばる（畳み漏れ） ---
P()
P('== C. 同じ公演名が複数エントリに散らばる（長期公演・連日公演の畳み漏れ） ==')


def norm(s):
    s = unicodedata.normalize('NFKC', s or '').lower()
    return re.sub(r'[\s　・･,，.。!！?？~〜\-—–_/／\(\)（）\[\]【】「」『』"\'’]', '', s)


g = defaultdict(list)
for e in TG:
    g[norm(e['name'])].append(e)
multi = {k: v for k, v in g.items() if len(v) > 1}
P('   同名グループ %d組 / 関わるエントリ %d件' % (len(multi), sum(len(v) for v in multi.values())))
for k, v in sorted(multi.items(), key=lambda x: -len(x[1]))[:12]:
    P('      %-34s %2d件 id=%s 会場=%s' % (v[0]['name'][:34], len(v),
                                         [x['id'] for x in v][:8], v[0]['venue'][:18]))
same_venue = [v for v in multi.values() if len({x['venue'] for x in v}) == 1]
P('   うち会場も同じ（＝ほぼ確実に1エントリにすべき）: %d組 / %d件'
  % (len(same_venue), sum(len(v) for v in same_venue)))

# --- D. 同じ公演日・同じ会場の別エントリ ---
P()
P('== D. 同じ会場・同じ公演日で別エントリ（重複の疑い） ==')
g2 = defaultdict(list)
for e in TG:
    g2[(e['venue'], e['date'])].append(e)
d2 = {k: v for k, v in g2.items() if len(v) > 1}
P('   組 %d / エントリ %d件' % (len(d2), sum(len(v) for v in d2.values())))
for k, v in sorted(d2.items(), key=lambda x: -len(x[1]))[:6]:
    P('      %s %s → id=%s' % (k[0][:20], k[1], [(x['id'], x['name'][:18]) for x in v][:4]))

# --- E. 畳んだエントリ（複数URL）の中身 ---
P()
P('== E. ツアーとして畳んだエントリ ==')
merged = [e for e in TG if len(eids(e)) > 1]
P('   複数ページを畳んだエントリ %d件' % len(merged))
for e in sorted(merged, key=lambda x: -len(eids(x)))[:10]:
    P('      id%s %-30s ページ%2d 県=%s' % (e['id'], e['name'][:30], len(eids(e)),
                                         (e['prefecture'] or '')[:40]))
# 畳んだのに公演日がバラバラ＝別イベントを畳んだ疑い（名前の骨格が短いもの）
sus = [e for e in merged if len(e['name']) <= 8]
P('   ⚠️畳んだ後の公演名が8字以下（別イベントを畳んだ疑い）: %d件' % len(sus))
for e in sus[:10]:
    P('      id%s 名前=%s ページ%d 県=%s' % (e['id'], e['name'], len(eids(e)), e['prefecture'][:30]))

# --- F. 生データにあって登録枠にならなかった券種（黙って落ちた枠） ---
P()
P('== F. 生データにあるのに登録枠にならなかった券種の理由 ==')
LIVE, UNOP, SOLD, CLOSED = 'is-available', 'is-unopened', ('is-unavailable', 'btn-unable'), 'is-closed'


def state_of(cls):
    c = cls or ''
    if UNOP in c:
        return 'unopened'
    if CLOSED in c:
        return 'closed'
    if any(s in c for s in SOLD):
        return 'soldout'
    if LIVE in c:
        return 'live'
    return 'unknown'


c = Counter()
ex = defaultdict(list)
for e in TG:
    n_reg = len(e['tickets'])
    ids = eids(e)
    rawt = []
    for i in ids:
        r = raw.get(i)
        if not r:
            continue
        offs = {o['valid_from'] for o in (r.get('ld_offers') or []) if o.get('valid_from')}
        for p in r['programs']:
            if p.get('date') and p['date'] >= TODAY:
                for t in p.get('tickets') or []:
                    rawt.append((t, state_of(t.get('class')),
                                 bool([pp for pp in (t.get('periods') or []) if pp.get('parsed')]),
                                 len(offs)))
    if len(rawt) == n_reg:
        continue
    for t, st, hasper, noffs in rawt:
        if st == 'unopened' and not hasper:
            k = '受付前だが受付期間が読めない（推測しないので落とす）'
        elif st == 'live' and not hasper and noffs != 1:
            k = '当日払いで発売日も取れない（落とす）'
        elif st == 'unknown':
            k = '🚨売り状態が読めない class（落とす）'
        else:
            continue
        c[k] += 1
        if len(ex[k]) < 5:
            ex[k].append((e['id'], (t.get('name') or '')[:26], t.get('class')))
for k, v in c.most_common():
    P('   %s: %d枠' % (k, v))
    for x in ex[k]:
        P('      id%s 券種=%s class=%s' % x)

# --- G. classが読めない券種が全体でいくつあるか ---
allst = Counter()
for i, r in raw.items():
    for p in r['programs']:
        if p.get('date') and p['date'] >= TODAY:
            for t in p.get('tickets') or []:
                allst[state_of(t.get('class'))] += 1
P('   生データ全体の売り状態: %s' % dict(allst))

# --- H. その他の点検 ---
P()
P('== H. その他 ==')
P('   _genre の内訳: %s' % dict(Counter(e.get('_genre') for e in TG)))
P('   カテゴリ対応表に無い（musicetc）: %d件' % sum(1 for e in TG if e.get('_genre') == 'musicetc'))
P('   artist が公演名と同じ（出演者が取れていない）: %d件'
  % sum(1 for e in TG if e['artist'] == e['name']))
P('   venue が（会場未定）: %d件' % sum(1 for e in TG if e['venue'] == '（会場未定）'))
P('   price が null: %d件' % sum(1 for e in TG if e.get('price') is None))
P('   verified が true でない: %d件' % sum(1 for e in TG if e.get('verified') is not True))
P('   公演名に テスト/test/サンプル: %d件'
  % sum(1 for e in TG if re.search(r'テスト|ﾃｽﾄ|サンプル|sample|test', e['name'], re.I)))
P('   公演日が今日より前: %d件' % sum(1 for e in TG if e['date'] < TODAY))
P('   公演日が1年より先: %d件' % sum(1 for e in TG if e['date'] > '2027-09-18'))
P('   公演日が2年より先: %d件' % sum(1 for e in TG if e['date'] > '2028-09-17'))
far = sorted((e for e in TG if e['date'] > '2027-09-18'), key=lambda x: x['date'], reverse=True)[:6]
for e in far:
    P('      id%s %s %s %s' % (e['id'], e['date'], e['name'][:26], e['venue'][:16]))
# 券種名の長さ
lens = [len(re.sub(r'（[^（）]*\d{1,2}/\d{1,2}公演）.*$', '', t['type'])) for e in TG for t in e['tickets']]
P('   券種名の長さ 28字ちょうど（＝カットされた疑い）: %d枠' % sum(1 for x in lens if x == 28))
P('   券種名が1字以下: %d枠' % sum(1 for x in lens if x <= 1))
# 「様」だけ・アンダースコア残り
P('   券種名に _ が残っている: %d枠'
  % sum(1 for e in TG for t in e['tickets'] if '_' in t['type']))
P('   券種名に 円 が入っている（値段が名前に混ざる）: %d枠'
  % sum(1 for e in TG for t in e['tickets'] if re.search(r'[¥￥]|\d,\d{3}円', t['type'])))
P('   券種名に 開場/開演 が残っている: %d枠'
  % sum(1 for e in TG for t in e['tickets'] if re.search(r'開場|開演|終演', t['type'])))
P('   バッジの県が2県以上（畳んだもの）: %d件'
  % sum(1 for e in TG if '・' in (e['prefecture'] or '')))
# 同じ公演日が複数のticketに散らばるがdateLabelが1日だけ
nodup = [e for e in TG if len({re.search(r'(\d{1,2}/\d{1,2})公演', t['type']).group(1)
                               for t in e['tickets'] if re.search(r'(\d{1,2}/\d{1,2})公演', t['type'])}) > 1
         and '〜' not in (e['dateLabel'] or '')]
P('   🚨枠の公演日が2日以上あるのに dateLabel が1日だけ: %d件' % len(nodup))
for e in nodup[:6]:
    P('      id%s %s label=%s' % (e['id'], e['name'][:24], e['dateLabel']))

io.open(ROOT + r'\tmp\audit3_out.txt', 'w', encoding='utf-8').write('\n'.join(OUT))
