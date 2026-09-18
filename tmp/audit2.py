# -*- coding: utf-8 -*-
"""監査その2＝表示影響・県欠落の原因・取りこぼし・生データ突合。"""
import io, json, re, sys, datetime
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
TODAY = '2026-09-18'
ROOT = r'C:\Users\user\oshinavi'
src = io.open(ROOT + r'\index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
TG = [e for e in EVENTS if 11317 <= e.get('id', 0) <= 13230]
OTH = [e for e in EVENTS if not (11317 <= e.get('id', 0) <= 13230)]

# --- (1) 既存（非TIGET）のsaleEndUnknown券種名の作法 ---
print('== 1. 既存エントリの saleEndUnknown 券種名の書き方（TIGETと比べる） ==')
samp = []
for e in OTH:
    for t in e.get('tickets') or []:
        if t.get('saleEndUnknown'):
            samp.append((e['id'], t['type']))
print('  既存のsaleEndUnknown枠 %d件' % len(samp))
tail = Counter()
for i, ty in samp:
    m = re.search(r'公演）(.*)$', ty)
    tail[(m.group(1) if m else '(形なし)')[-12:]] += 1
for k, v in tail.most_common(8):
    print('   末尾 %-16r %d件' % (k, v))
for i, ty in samp[:5]:
    print('   例 id%s %s' % (i, ty))
tgunk = [(e['id'], t['type']) for e in TG for t in (e.get('tickets') or []) if t.get('saleEndUnknown')]
print('  TIGETのsaleEndUnknown枠 %d件 / 末尾が「発売〜」 %d件'
      % (len(tgunk), sum(1 for i, ty in tgunk if ty.endswith('発売〜'))))

# --- (2) バッジ整形（画面と同じ正規表現）を通した後に日付が残るか ---
STRIP1 = re.compile(r'\s*〜\s*(?:R\d+年\s*)?\d{1,2}/\d{1,2}(?:\s*\d{1,2}:\d{2})?\s*$')
STRIP2 = re.compile(r'\s*(?:R\d+年\s*)?\d{1,2}/\d{1,2}(?:\s*\d{1,2}:\d{2})?\s*(?:発売開始|発売予定|発売|販売開始|受付開始|受付)\s*$')


def badge(ty):
    b = STRIP2.sub('', STRIP1.sub('', ty or '')).strip()
    return b or ty


leftover = [(e['id'], t['type'], badge(t['type'])) for e in TG for t in (e.get('tickets') or [])
            if re.search(r'公演）.+$', badge(t['type']))]
print()
print('== 2. 画面のバッジ整形を通しても（…公演）の後ろに文字が残る枠 %d件 / エントリ %d件 =='
      % (len(leftover), len({x[0] for x in leftover})))
for x in leftover[:6]:
    print('   id%s %s  →  %s' % x)

# --- (3) 画面に出る枠を数える（描画ロジックの再現） ---
def shown(t, ev):
    if t.get('soldout'):
        return 'soldout' if ev['date'] >= TODAY else 'hidden'
    sd, d = t.get('startDate'), t.get('date')
    if (not sd or sd <= TODAY) and d < TODAY:
        return 'hidden'
    return 'live'


cnt = Counter()
zero, only_sold = [], []
for e in TG:
    st = [shown(t, e) for t in (e.get('tickets') or [])]
    cnt.update(st)
    if not any(s != 'hidden' for s in st):
        zero.append(e)
    elif not any(s == 'live' for s in st):
        only_sold.append(e)
print()
print('== 3. 画面に出る枠 ==')
print('   買える/発売前 %d枠 / 印だけ（売切・販売終了） %d枠 / 画面から消える %d枠'
      % (cnt['live'], cnt['soldout'], cnt['hidden']))
print('   🚨バッジが1つも出ないカード %d件' % len(zero))
for e in zero[:8]:
    print('      id%s %s（枠%d 全部消える）' % (e['id'], (e['name'])[:30], len(e['tickets'])))
print('   売切・販売終了の印だけのカード %d件' % len(only_sold))

# --- (4) 県が空の原因＝生データに県の手がかりがあるか ---
raw = {}
for f in ('tiget_yt_vt2_0918.json', 'tiget_wide_0918.json'):
    d = json.load(io.open(ROOT + r'\tmp\\' + f, encoding='utf-8'))
    for ev in d['events']:
        raw.setdefault(str(ev['id']), ev)
print()
print('== 4. 県が空 281件の原因 ==')
nop = [e for e in TG if not (e.get('prefecture') or '')]
have_hint = 0
ex = []
for e in nop:
    ids = re.findall(r'/events/(\d+)', json.dumps(e.get('links'), ensure_ascii=False))
    r = raw.get(ids[0]) if ids else None
    if r and (r.get('ld_region') or (r.get('list') or {}).get('area')):
        have_hint += 1
        if len(ex) < 6:
            ex.append((e['id'], e['name'][:26], r.get('ld_region'), (r.get('list') or {}).get('area')))
print('   県が空 %d件 / うち生データに県の手がかり（ld_region か list.area）あり %d件' % (len(nop), have_hint))
for x in ex:
    print('      id%s %s ld_region=%r list.area=%r' % x)

# --- (5) 生データ→投入の取りこぼし ---
print()
print('== 5. 生データ %d件 → 登録 %d件 ==' % (len(raw), len(TG)))
reg_ids = set()
for e in TG:
    reg_ids |= set(re.findall(r'/events/(\d+)', json.dumps(e, ensure_ascii=False)))
miss = [i for i in raw if i not in reg_ids]
print('   登録に入っていない生データ %d件' % len(miss))
why = Counter()
exm = defaultdict(list)
for i in miss:
    r = raw[i]
    ds = sorted({p['date'] for p in r['programs'] if p.get('date')})
    fu = [d for d in ds if d >= TODAY]
    if not fu:
        k = '公演が終わっている'
    elif fu[0] > '2028-09-17':
        k = '公演日が2年より先'
    elif re.search(r'委託販売|即売会|出店|ブース|エントリーフォーム|参加エントリ|出場エントリ|駐車|案内登録|先行案内', r.get('name') or ''):
        k = '出す側の申込'
    elif not r['programs'] or not any(p.get('tickets') for p in r['programs']):
        k = '券種が読めない'
    else:
        k = '⚠️理由が説明できない（取りこぼしの疑い）'
    why[k] += 1
    if len(exm[k]) < 6:
        exm[k].append('events/%s %s 公演%s' % (i, (r.get('name') or '')[:30], fu[:1]))
for k, v in why.most_common():
    print('   %s: %d件' % (k, v))
    for s in exm[k]:
        print('        %s' % s)

# --- (6) 生データの券種と登録枠の数の突合（ネット不要の簡易ゲート） ---
print()
print('== 6. 生データの券種数 vs 登録枠数（今日以降の公演分だけ） ==')
bad = []
for e in TG:
    ids = sorted(set(re.findall(r'/events/(\d+)', json.dumps(e, ensure_ascii=False))))
    n = 0
    ok = True
    for i in ids:
        r = raw.get(i)
        if not r:
            ok = False
            break
        for p in r['programs']:
            if p.get('date') and p['date'] >= TODAY:
                n += len(p.get('tickets') or [])
    if ok and n != len(e.get('tickets') or []):
        bad.append((e['id'], e['name'][:28], n, len(e['tickets'])))
print('   枠数が生データと合わないエントリ %d件' % len(bad))
for x in bad[:10]:
    print('      id%s %s 生%d枠 → 登録%d枠' % x)

# --- (7) 0円の券種／抽選で締切がparsed出来ていない券種 ---
print()
print('== 7. 生データ側の気になる券種 ==')
zeroprice, lottery = [], []
for e in TG:
    ids = sorted(set(re.findall(r'/events/(\d+)', json.dumps(e, ensure_ascii=False))))
    for i in ids:
        r = raw.get(i)
        if not r:
            continue
        for p in r['programs']:
            if not p.get('date') or p['date'] < TODAY:
                continue
            for t in p.get('tickets') or []:
                if t.get('price') in (0, None):
                    zeroprice.append((e['id'], r['name'][:24], t.get('name', '')[:30], t.get('price')))
                if any((pp.get('pay') or '').find('抽選') >= 0 and not pp.get('parsed')
                       for pp in (t.get('periods') or [])):
                    lottery.append((e['id'], t.get('name', '')[:24]))
print('   価格0円/価格なしの券種 %d件（エントリ %d件）' % (len(zeroprice), len({x[0] for x in zeroprice})))
for x in zeroprice[:10]:
    print('      id%s %s / 券種=%s price=%r' % x)
print('   抽選日の行が読めていない券種 %d件（エントリ %d件）' % (len(lottery), len({x[0] for x in lottery})))

# --- (8) 28字カットで別の券種名が同じになった件数（D01の原因） ---
print()
print('== 8. 二重バッジの原因 ==')
def ticket_name(raw):
    nm = (raw or '').strip()
    nm = re.sub(r'\s*\d{4}年\d{1,2}月\d{1,2}日.*$', '', nm).strip()
    nm = re.sub(r'^[\[［][\d/・:：\s\-—〜~]+[\]］]\s*', '', nm).strip()
    if not nm:
        return 'チケット'
    if re.search(r'開場|開演|終演', nm):
        return 'チケット'
    nm = (nm.replace('／', '・').replace('(', '（').replace(')', '）')
            .replace('[', '［').replace(']', '］'))
    PAIRS = ('（）', '「」', '『』', '【】', '＜＞', '〔〕', '［］', '〈〉')
    cut = nm[:28]
    while cut and not all(cut.count(a) == cut.count(b) for a, b in PAIRS):
        cut = cut[:-1]
    return cut.rstrip('・、 /') if cut else 'チケット'


cause = Counter()
exc = defaultdict(list)
for e in TG:
    ids = sorted(set(re.findall(r'/events/(\d+)', json.dumps(e, ensure_ascii=False))))
    names = []
    for i in ids:
        r = raw.get(i)
        if not r:
            continue
        for p in r['programs']:
            if p.get('date') and p['date'] >= TODAY:
                names += [t.get('name', '') for t in (p.get('tickets') or [])]
    seen = defaultdict(list)
    for n in names:
        seen[ticket_name(n)].append(n)
    for k, v in seen.items():
        if len(v) > 1 and len(set(v)) > 1:
            if all(re.search(r'開場|開演|終演', x) for x in v):
                c = '進行案内で「チケット」に倒れて衝突'
            elif len({x[:28] for x in v}) == 1:
                c = '28字カットで衝突'
            else:
                c = 'その他の整形で衝突'
            cause[c] += 1
            if len(exc[c]) < 4:
                exc[c].append((e['id'], k, v[:3]))
for k, v in cause.most_common():
    print('   %s: %d件' % (k, v))
    for x in exc[k]:
        print('      id%s 「%s」 ← %s' % x)
