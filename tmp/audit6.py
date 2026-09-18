# -*- coding: utf-8 -*-
"""監査その6＝残っている二重バッジ・発売前の取り違え・雛形疑い・県名の妥当性。"""
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

PREF = ['北海道', '青森', '岩手', '宮城', '秋田', '山形', '福島', '茨城', '栃木', '群馬', '埼玉',
        '千葉', '東京', '神奈川', '新潟', '富山', '石川', '福井', '山梨', '長野', '岐阜', '静岡',
        '愛知', '三重', '滋賀', '京都', '大阪', '兵庫', '奈良', '和歌山', '鳥取', '島根', '岡山',
        '広島', '山口', '徳島', '香川', '愛媛', '高知', '福岡', '佐賀', '長崎', '熊本', '大分',
        '宮崎', '鹿児島', '沖縄']

P('== A. saleEndUnknown の発売日が未来（本当は販売中なのに「発売前」に見える） ==')
fut = [(e['id'], t['type'], t['startDate']) for e in TG for t in e['tickets']
       if t.get('saleEndUnknown') and (t.get('startDate') or '') > TODAY]
nosd = [(e['id'], t['type']) for e in TG for t in e['tickets']
        if t.get('saleEndUnknown') and not t.get('startDate')]
P('   発売日が未来 %d枠 / startDateが無い %d枠' % (len(fut), len(nosd)))
for x in fut[:6]:
    P('      id%s %s start=%s' % x)

P()
P('== B. 同じカードに出る同じバッジ文字（画面で見分けがつかない） ==')
STRIP1 = re.compile(r'\s*〜\s*(?:R\d+年\s*)?\d{1,2}/\d{1,2}(?:\s*\d{1,2}:\d{2})?\s*$')
STRIP2 = re.compile(r'\s*(?:R\d+年\s*)?\d{1,2}/\d{1,2}(?:\s*\d{1,2}:\d{2})?\s*(?:発売開始|発売予定|発売|販売開始|受付開始|受付)\s*$')


def badge(ty):
    return (STRIP2.sub('', STRIP1.sub('', ty or '')).strip()) or ty


same_all, same_txt = [], []
for e in TG:
    g = defaultdict(list)
    for t in e['tickets']:
        g[badge(t['type'])].append(t)
    for k, v in g.items():
        if len(v) < 2:
            continue
        same_txt.append((e['id'], k, len(v)))
        shown = {(t.get('startDate') if t.get('saleEndUnknown') else t.get('date'),
                  bool(t.get('soldout')), bool(t.get('saleEnded'))) for t in v}
        if len(shown) < len(v):
            same_all.append((e['id'], k, len(v), len(shown)))
P('   同じバッジ文字が2つ以上 %d組（エントリ %d件）' % (len(same_txt), len({x[0] for x in same_txt})))
P('   🚨そのうち出る日付・印まで同じ＝完全に見分けがつかない %d組（エントリ %d件）'
  % (len(same_all), len({x[0] for x in same_all})))
for x in same_all[:8]:
    P('      id%s 「%s」 %d枠→見える形は%d通り' % x)
for x in same_txt[:6]:
    P('      （参考）id%s 「%s」 %d枠' % x)

P()
P('== C. 券種名が意味を持たない枠 ==')
def base(ty):
    return re.sub(r'（[^（）]*\d{1,2}/\d{1,2}公演）.*$', '', ty).strip()


b = Counter(base(t['type']) for e in TG for t in e['tickets'])
P('   バッジの券種名の出方（上位12）:')
for k, v in b.most_common(12):
    P('      %-24s %d枠' % (k[:24], v))
P('   「チケット」だけの枠: %d枠 / 値段付き「チケット N円」: %d枠'
  % (b.get('チケット', 0), sum(v for k, v in b.items() if re.fullmatch(r'チケット [\d,]+円', k))))

P()
P('== D. 生データ側で名前も値段も取れていない券種（ハーベスタの読み落ち疑い） ==')
noname_noprice = 0
noname_price = 0
ev_all = []
for r in raw.values():
    n = 0
    tot = 0
    for p in r['programs']:
        for t in p.get('tickets') or []:
            tot += 1
            if not (t.get('name') or '').strip():
                if t.get('price'):
                    noname_price += 1
                else:
                    noname_noprice += 1
                    n += 1
    if n and n == tot:
        ev_all.append((r['id'], (r.get('name') or '')[:30], tot))
P('   名前が空で値段あり %d枠（＝TIGETが値段だけ書いている＝値段で見分けられる）' % noname_price)
P('   🚨名前も値段も空 %d枠（＝読み落ちの疑い）／全券種がそれ %d件' % (noname_noprice, len(ev_all)))
for x in ev_all[:6]:
    P('      events/%s %s 全%d枠' % x)

P()
P('== E. 公演名が意味を持たない・雛形の疑い ==')
sus = [e for e in TG if len(e['name']) <= 4 or re.fullmatch(r'[予約当日払いテスト\s]+', e['name'])]
P('   公演名が4字以下 %d件' % len(sus))
for e in sus[:12]:
    P('      id%s 名前=%s 公演=%s 会場=%s' % (e['id'], e['name'], e['date'], e['venue'][:20]))

P()
P('== F. 県の妥当性 ==')
bad = [(e['id'], e['prefecture']) for e in TG
       if e.get('prefecture') and any(p not in PREF for p in e['prefecture'].split('・'))]
P('   prefecture が47都道府県の名前でない: %d件 %s' % (len(bad), bad[:6]))
mismatch = []
for e in TG:
    for t in e['tickets']:
        m = re.search(r'（([^（）]*?)\s(\d{1,2}/\d{1,2})公演）', t['type'])
        if m and m.group(1) and e.get('prefecture') and m.group(1) not in e['prefecture'].split('・'):
            mismatch.append((e['id'], e['prefecture'], m.group(1)))
P('   バッジの県がエントリの県に無い: %d件 %s' % (len(mismatch), mismatch[:6]))

P()
P('== G. 公演日の突合（バッジの公演日が生データの公演日にあるか） ==')
ng = []
for e in TG:
    ids = sorted(set(re.findall(r'/events/(\d+)', json.dumps(e, ensure_ascii=False))))
    days = set()
    for i in ids:
        r = raw.get(i)
        if r:
            days |= {p['date'] for p in r['programs'] if p.get('date')}
    if not days:
        continue
    md = {'%d/%d' % (int(d[5:7]), int(d[8:10])) for d in days}
    for t in e['tickets']:
        m = re.search(r'(\d{1,2}/\d{1,2})公演）', t['type'])
        if m and m.group(1) not in md:
            ng.append((e['id'], t['type'][:40], sorted(md)[:3]))
P('   バッジの公演日が生データに無い: %d枠 %s' % (len(ng), ng[:4]))

P()
P('== H. エントリのdateが生データの最終公演日と合っているか ==')
ng2 = []
for e in TG:
    ids = sorted(set(re.findall(r'/events/(\d+)', json.dumps(e, ensure_ascii=False))))
    days = set()
    for i in ids:
        r = raw.get(i)
        if r:
            days |= {p['date'] for p in r['programs'] if p.get('date') and p['date'] >= TODAY}
    if days and e['date'] != max(days):
        ng2.append((e['id'], e['date'], max(days)))
P('   合わない: %d件 %s' % (len(ng2), ng2[:6]))

io.open(ROOT + r'\tmp\audit6_out.txt', 'w', encoding='utf-8').write('\n'.join(OUT))
