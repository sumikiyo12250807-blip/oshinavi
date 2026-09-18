# -*- coding: utf-8 -*-
"""TIGET投入分（id 11317〜13230）の独立監査。ネットには一切アクセスしない。"""
import io, json, re, sys, datetime
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
TODAY = '2026-09-18'
ROOT = r'C:\Users\user\oshinavi'

src = io.open(ROOT + r'\index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
TG = [e for e in EVENTS if 11317 <= e.get('id', 0) <= 13230]
OTHER = [e for e in EVENTS if not (11317 <= e.get('id', 0) <= 13230)]

raw = {}
for f in ('tmp/tiget_yt_vt2_0918.json', 'tmp/tiget_wide_0918.json'):
    d = json.load(io.open(ROOT + '\\' + f.replace('/', '\\'), encoding='utf-8'))
    for ev in d['events']:
        raw.setdefault(str(ev['id']), ev)

print('== 母数 ==')
print('EVENTS 全体 %d件 / TIGET分 %d件 / 枠 %d件 / 生データ %d件'
      % (len(EVENTS), len(TG), sum(len(e.get('tickets') or []) for e in TG), len(raw)))

R = defaultdict(list)   # 型名 -> [(id, 説明)]


def add(kind, e, detail):
    R[kind].append((e['id'], (e.get('name') or '')[:38], detail))


PREF_ALL = ['北海道', '青森', '岩手', '宮城', '秋田', '山形', '福島', '茨城', '栃木', '群馬', '埼玉',
            '千葉', '東京', '神奈川', '新潟', '富山', '石川', '福井', '山梨', '長野', '岐阜', '静岡',
            '愛知', '三重', '滋賀', '京都', '大阪', '兵庫', '奈良', '和歌山', '鳥取', '島根', '岡山',
            '広島', '山口', '徳島', '香川', '愛媛', '高知', '福岡', '佐賀', '長崎', '熊本', '大分',
            '宮崎', '鹿児島', '沖縄']
SUFFIX = re.compile(r'（([^（）]*?)\s?(\d{1,2}/\d{1,2})公演）(.*)$')
SELLER = re.compile(r'委託販売|即売会|出店|ブース|エントリーフォーム|参加エントリ|出場エントリ|'
                    r'駐車|案内登録|先行案内|出展|出演者|物販スペース|フリマ|スペース利用')
DATEISH = re.compile(r'\d{1,2}/\d{1,2}|\d{1,2}月\d{1,2}日|\d{1,2}:\d{2}')

url_to_ids = defaultdict(set)
slotkey_global = Counter()

for e in TG:
    ts = e.get('tickets') or []
    nm = e.get('name') or ''
    pref = e.get('prefecture') or ''
    # --- エントリ単位 ---
    if not ts:
        add('E00_枠ゼロ', e, '枠が無い')
    if e['date'] < TODAY:
        add('E01_公演日が過去', e, 'date=%s' % e['date'])
    if e['date'] > (datetime.date.fromisoformat(TODAY) + datetime.timedelta(days=730)).isoformat():
        add('E02_公演日が2年より先', e, 'date=%s' % e['date'])
    if SELLER.search(nm):
        add('E03_出す側の疑い（公演名）', e, nm)
    if not pref:
        add('E04_県が空', e, 'venue=%s' % (e.get('venue') or ''))
    if e.get('genre') != 'new':
        add('E05_新着プールに居ない', e, 'genre=%s' % e.get('genre'))
    if (e.get('links') or {}).get('tiget'):
        url_to_ids[e['links']['tiget']].append if False else url_to_ids[e['links']['tiget']].add(e['id'])
    # dateLabel と date
    lab = e.get('dateLabel') or ''
    labdays = re.findall(r'(\d{4})年(\d{1,2})月(\d{1,2})日', lab)
    if labdays:
        last = '%04d-%02d-%02d' % tuple(int(x) for x in labdays[-1])
        if last != e['date']:
            add('E06_dateLabelとdateが不一致', e, 'label末=%s date=%s' % (last, e['date']))
    # --- 枠単位 ---
    seen_exact = Counter()
    seen_badge = Counter()
    for t in ts:
        ty = t.get('type') or ''
        seen_exact[(ty, t.get('date'), t.get('url'), bool(t.get('soldout')), bool(t.get('saleEnded')))] += 1
        seen_badge[ty] += 1
        for u in re.findall(r'tiget\.net/events/(\d+)', t.get('url') or ''):
            url_to_ids['https://tiget.net/events/' + u].add(e['id'])
        m = SUFFIX.search(ty)
        base = ty[:m.start()] if m else ty
        tail = m.group(3) if m else ''
        tpref = (m.group(1) or '').strip() if m else ''
        if not m:
            add('T01_バッジの形が違う（（県 M/D公演）が無い）', e, ty)
        else:
            if tpref and tpref not in PREF_ALL and '・' not in tpref:
                add('T02_県の欄が県名でない', e, ty)
            if tpref and pref and tpref != pref and tpref not in pref.split('・'):
                add('T03_県とバッジの県が食い違い', e, 'pref=%s badge=%s' % (pref, tpref))
            if not tpref and pref:
                add('T04_県があるのにバッジに県が無い', e, 'pref=%s / %s' % (pref, ty))
            if tail and not re.fullmatch(r'〜\d{1,2}/\d{1,2}( \d{1,2}:\d{2})?|'
                                         r'\d{1,2}/\d{1,2}( \d{1,2}:\d{2})?発売(〜)?|', tail):
                add('T05_締切の書き方が規格外', e, 'tail=%r / %s' % (tail, ty))
        if base.strip() == '' :
            add('T06_券種名が空', e, ty)
        if base.strip() == 'チケット':
            add('T07_券種名が「チケット」に倒れている', e, ty)
        # カッコの不均衡
        for a, b in ('（）', '「」', '『』', '【】', '［］', '〈〉'):
            if base.count(a) != base.count(b):
                add('T08_券種名のカッコが閉じていない', e, ty)
                break
        if DATEISH.search(base):
            add('T09_券種名に日付・時刻の札が残っている', e, ty)
        if SELLER.search(base):
            add('T10_出す側の券種が混ざっている', e, ty)
        # 日付の整合
        td, sd = t.get('date'), t.get('startDate')
        if not td:
            add('T11_枠にdateが無い', e, ty)
        else:
            if td < TODAY and not t.get('saleEndUnknown'):
                add('T12_枠のdateが過去', e, 'date=%s / %s' % (td, ty))
            if sd and sd > td:
                add('T13_startDate>date', e, 'start=%s date=%s / %s' % (sd, td, ty))
            if td > e['date'] and not t.get('soldout'):
                add('T14_締切が公演日より後（公演日で締めていない）', e,
                    '締切=%s 公演=%s / %s' % (td, e['date'], ty))
        if t.get('saleEndUnknown'):
            if re.search(r'〜\d{1,2}/\d{1,2}', ty):
                add('T15_saleEndUnknownなのに締切が書かれている', e, ty)
            if not ty.endswith('発売〜'):
                add('T16_saleEndUnknownなのに末尾が「発売〜」でない', e, ty)
            if td != e['date'] and td not in [t2.get('date') for t2 in ts]:
                add('T17_saleEndUnknownのdateが公演日でない', e, 'date=%s 公演=%s' % (td, e['date']))
        if t.get('saleEnded') and not t.get('soldout'):
            add('T18_saleEndedにsoldoutが無い', e, ty)
        if not t.get('url'):
            add('T19_枠に飛び先が無い', e, ty)
        elif 'tiget.net/events/' not in t['url']:
            add('T20_枠の飛び先がTIGETでない', e, t['url'])
        # 発売前（発売〜ではない「発売」）のstartDateが過去
        if re.search(r'\d{1,2}/\d{1,2}( \d{1,2}:\d{2})?発売$', ty) and sd and sd < TODAY:
            add('T21_「発売」と書いてあるのに発売日が過去', e, 'start=%s / %s' % (sd, ty))
    for k, c in seen_exact.items():
        if c > 1:
            add('D01_まったく同じ枠の二重（券種名＋締切＋飛び先）', e, '%d本 / %s' % (c, k[0]))
    for k, c in seen_badge.items():
        if c > 1 and seen_exact[[x for x in seen_exact if x[0] == k][0]] < c:
            add('D02_同じバッジ文字が複数（締切か飛び先だけ違う）', e, '%d本 / %s' % (c, k))

# 同じURLが複数エントリ
for u, ids in url_to_ids.items():
    if len(ids) > 1:
        R['D03_同じTIGETページが複数エントリに散らばり'].append((sorted(ids)[0], u, 'id=%s' % sorted(ids)))

# 既存エントリ(非TIGET)とURLがかぶっていないか
other_urls = set()
for e in OTHER:
    blob = json.dumps(e, ensure_ascii=False)
    other_urls |= set(re.findall(r'tiget\.net/events/(\d+)', blob))
dupold = [u for u in url_to_ids if re.search(r'/events/(\d+)', u).group(1) in other_urls]
for u in dupold:
    R['D04_既存エントリと同じTIGETページ'].append((0, u, ''))

print()
print('== 型ごとの件数（エントリ数 / 指摘数） ==')
for k in sorted(R):
    ids = {x[0] for x in R[k]}
    print('%-52s 指摘%5d件 / エントリ%5d件' % (k, len(R[k]), len(ids)))

out = io.open(ROOT + r'\tmp\audit_tiget_raw.txt', 'w', encoding='utf-8')
for k in sorted(R):
    out.write('\n===== %s : %d件 =====\n' % (k, len(R[k])))
    for row in R[k][:40]:
        out.write('  id%s | %s | %s\n' % row)
out.close()
print('詳細 -> tmp/audit_tiget_raw.txt')
