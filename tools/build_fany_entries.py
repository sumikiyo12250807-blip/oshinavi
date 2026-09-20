# -*- coding: utf-8 -*-
"""FANYチケット（吉本興業の売り場）のハーベスト結果から OSHINAVI のエントリを組む。

  python tools/build_fany_entries.py tmp/fany_0921.json --out tmp/built_fany_0921.json
  python tools/build_fany_entries.py --selftest

## 売り状態の読み方（2026-09-21 に実データ7,791枠の全語彙を数えて確かめた対応表）

| display_sales_status | アイコン           | 枠数  | OSHINAVI |
|----------------------|--------------------|-------|----------|
| 先着発売中           | fany_icon__sold    | 2,673 | 買える（〜終了日時） |
| 抽選受付中           | fany_icon__sold    |   148 | 買える（〜終了日時） |
| 先着発売前           | beforeRelease      |   148 | 発売前（M/D HH:MM発売） |
| 抽選受付前           | beforeRelease      |   100 | 発売前（M/D HH:MM発売） |
| 先着発売終了         | fany_icon__soldout |    73 | `soldout`＋`saleEnded`（販売終了） |
| 抽選受付終了         | fany_icon__soldout | 4,649 | `soldout`＋`presaleEnded`（**先行終了**） |

🚨**この6語しか無い＝「予定枚数終了（売り切れ）」の文言は一覧に出ない**。
   だから**売り切れを一覧から判定しない**（楽天と同じ型＝[[reference_rakuten_harvest]]）。
   「先着発売中」は「受付期間の中」という意味で、完売しているかは reception ページ側にしかない。

## エントリの単位＝**1公演（performance）＝1エントリ**（畳まない）

同じ event_id に78公演ある劇場の定期公演（なんばグランド花月「本公演　１回目」）で、
**出演者が51通りに日替わり**だった（2026-09-21 実測）。畳むと「誰が出るか」が壊れる＝
推し活サイトとしていちばん大事な情報が消えるので、**公演ごとに分ける**。
（[[feedback_tour_consolidate]]の「ツアーは1エントリ」は同じ出演者が会場を回る形の話）

- 飛び先＝`links.fany` は詳細ページ `/event/detail/<event_id>`、
  **各枠の url は申込ページ `destination_url`（/reception/<sales_id>/<performance_id>）**＝公演ごとに違う
- 同じ日・同じ会場で公演が2つ以上（480組あった）＝バッジに**開演時刻**を入れる
  （[[feedback_same_day_show_time_badge]]）
"""
import argparse
import collections
import datetime
import io
import json
import re
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

WD = '月火水木金土日'

# FANYの検索ジャンル → OSHINAVIのジャンル（**売り場の言う通りに機械で写す**
# ＝[[feedback_genre_pia_asis_and_other]]。人が1件ずつ判断する枠を作らない）
FANY_GENRE = {
    '30': 'owarai',    # お笑い
    '31': 'musicetc',  # 音楽（FANYに細分が無い＝邦楽その他に倒す）
    '32': 'engeki',    # 演劇/ステージ
    '33': 'sports',    # スポーツ
    '34': 'anime',     # アニメ
    '35': 'event',     # ゲーム（うちに game ジャンルが無い）
    '36': 'movie',     # 映画/ライブビューイング
    '37': 'art',       # アート/イベント
    # '38' 劇場以外＝**場所の話でジャンルではない**（お笑いと重複して付く）。写さない。
}
GENRE_FALLBACK = 'owarai'  # 吉本の売り場＝ジャンルが38だけの時はお笑い

PREF47 = ('北海道 青森県 岩手県 宮城県 秋田県 山形県 福島県 茨城県 栃木県 群馬県 埼玉県 千葉県 東京都 '
          '神奈川県 新潟県 富山県 石川県 福井県 山梨県 長野県 岐阜県 静岡県 愛知県 三重県 滋賀県 京都府 '
          '大阪府 兵庫県 奈良県 和歌山県 鳥取県 島根県 岡山県 広島県 山口県 徳島県 香川県 愛媛県 高知県 '
          '福岡県 佐賀県 長崎県 熊本県 大分県 宮崎県 鹿児島県 沖縄県').split()

# 出す側の申込は載せない（[[feedback_oshinavi_concept]]の内側の線引き）。
# 2026-09-21 の実データでは公演名・券種名とも0件だったが、門は置く。
SELLER_SIDE = re.compile(
    r'委託販売|即売会|出店|ブース(?:出展|申込)?|'
    r'エントリーフォーム|参加エントリ|出場エントリ|'
    r'駐車|案内登録|先行案内'
)

LIVE_ST = ('先着発売中', '抽選受付中')
PRE_ST = ('先着発売前', '抽選受付前')
END_SALE = '先着発売終了'
END_LOT = '抽選受付終了'
KNOWN_ST = set(LIVE_ST) | set(PRE_ST) | {END_SALE, END_LOT}

_PAIRS = ('（）', '「」', '『』', '【】', '＜＞', '〔〕', '［］', '〈〉')


def strip_tags(s):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s or '')).strip()


def era(y):
    """2027年以降は令和略記を付ける（[[feedback_r9_year_notation]]）。"""
    return 'R%d年 ' % (y - 2018) if y > datetime.date.today().year else ''


def md(iso):
    y, m, d = int(iso[:4]), int(iso[5:7]), int(iso[8:10])
    return '%s%d/%d' % (era(y), m, d)


def jp(iso, extra=''):
    y, m, d = int(iso[:4]), int(iso[5:7]), int(iso[8:10])
    s = '%d年%d月%d日(%s)' % (y, m, d, WD[datetime.date(y, m, d).weekday()])
    return (s + ' ' + extra).strip() if extra else s


def perf_date_iso(p):
    """'2026/09/21(<span…>月・祝</span>)' → '2026-09-21'。取れなければ None。"""
    m = re.match(r'\s*(\d{4})/(\d{2})/(\d{2})', p.get('performance_date') or '')
    if m:
        return '%s-%s-%s' % m.groups()
    # 期間もの（class!=01）は valid_period を使う
    v = p.get('valid_period_start_date') or ''
    m = re.match(r'\s*(\d{4})/(\d{2})/(\d{2})', v)
    return '%s-%s-%s' % m.groups() if m else None


def perf_end_iso(p):
    """期間もの（通し券など）の最終日。単日なら公演日と同じ。"""
    v = p.get('valid_period_finish_date') or ''
    m = re.match(r'\s*(\d{4})/(\d{2})/(\d{2})', v)
    if m:
        return '%s-%s-%s' % m.groups()
    return perf_date_iso(p)


def raw_dt(s):
    """'20260922080000' → ('2026-09-22', '8:00')。空なら (None, None)。"""
    if not s or len(s) < 12 or not s[:12].isdigit():
        return None, None
    return ('%s-%s-%s' % (s[:4], s[4:6], s[6:8]), '%d:%s' % (int(s[8:10]), s[10:12]))


def start_time(p):
    """開演時刻（'開場 09:40  開演 10:00' → '10:00'）。無ければ開場、それも無ければ None。"""
    t = p.get('start_time') or ''
    if len(t) >= 4 and t.isdigit():
        return '%d:%s' % (int(t[:2]), t[2:4])
    m = re.search(r'開演\s*(\d{1,2}):(\d{2})', p.get('open_start_time_text') or '')
    if m:
        return '%d:%s' % (int(m.group(1)), m.group(2))
    return None


def pref_of(p):
    """都道府県。①販売枠の prefecture_code ②会場名の「（大阪府）」の順で決める（推測しない）。"""
    for s in p.get('performance_sales') or []:
        c = (s.get('prefecture_code') or '').strip()
        if c.isdigit() and 1 <= int(c) <= 47:
            n = PREF47[int(c) - 1]
            return n if n == '北海道' else n[:-1]
    for n in PREF47:
        if n in (p.get('venue_name') or ''):
            return n if n == '北海道' else n[:-1]
    return ''


def venue_of(p):
    """会場名から「（大阪府）」を外す。"""
    v = (p.get('venue_name') or '').strip()
    return re.sub(r'\s*[（(][^（）()]*[都道府県][）)]\s*$', '', v).strip()


def _balanced(s):
    return all(s.count(a) == s.count(b) for a, b in _PAIRS)


def ticket_name(raw):
    """券種名を整える（28字・カッコの途中で切らない・記号をそろえる）。"""
    nm = (raw or '').strip()
    nm = re.sub(r'^[●○◆■▲☆★]+', '', nm).strip()     # FANYは先頭に●を付ける
    nm = re.sub(r'\s*\d{4}年\d{1,2}月\d{1,2}日.*$', '', nm).strip()
    if not nm:
        return 'チケット'
    nm = (nm.replace('／', '・').replace('(', '（').replace(')', '）')
            .replace('[', '［').replace(']', '］'))
    cut = nm[:28]
    while cut and not _balanced(cut):
        cut = cut[:-1]
    return cut.rstrip('・、 /') if cut else 'チケット'


def artist_of(p):
    """出演者。'[漫才・落語]中川家／海原やすよ ともこ／…' → '中川家／海原やすよ ともこ／タカアンドトシ'
    🚨FANYは出演者を[区分]ごとに改行で並べる。区分の札を落として先頭3組だけ出す
      （カードの見出しに出るので長いと読めない）。空なら公演名で代える。"""
    s = (p.get('performer_detail') or '').replace('\r', '\n')
    s = re.sub(r'[［\[][^］\]]*[］\]]', ' ', s)          # [漫才・落語] を落とす
    # 🚨≪9／21 出演アーティスト≫ のような**日付入りの見出し**も札なので落とす
    #   （落とさないと artist が「≪9／21 出演アーティスト≫／新しい学校のリーダーズ」になる）
    s = re.sub(r'[≪《〈【][^≫》〉】]*[≫》〉】]', ' ', s)
    parts = [x.strip() for x in re.split(r'[／/\n、]+', s) if x.strip()]
    parts = [x for x in parts if not re.fullmatch(r'ほか|他|など|MC|ゲスト', x)]
    if not parts:
        return strip_tags(p.get('name')) or 'FANYチケット'
    return '／'.join(parts[:3])


def build_one(p, today, genre_map, unknown):
    """1公演＝1エントリ。載せられないときは (None, 理由)。"""
    name = strip_tags(p.get('name'))
    if SELLER_SIDE.search(name):
        return None, '出す側の申込（出店・参加エントリー・駐車・案内登録）'
    d = perf_date_iso(p)
    if not d:
        return None, '公演日が読めない'
    dend = perf_end_iso(p) or d
    # 期間もの（通し券）は最終日が今日以降なら載せる
    if max(d, dend) < today:
        return None, '公演が終わっている'
    limit = (datetime.date.fromisoformat(today) + datetime.timedelta(days=730)).isoformat()
    if d > limit:
        return None, '公演日が2年より先＝主催者の試し書きの疑い'

    pref, venue = pref_of(p), venue_of(p)
    stime = start_time(p)
    # 同じ日・同じ会場・同じイベントで2公演以上なら、バッジに開演時刻を入れて見分ける
    key = (p.get('event_id'), d, p.get('venue_id'))
    multi = genre_map['_same_day'].get(key, 0) > 1
    when = '%s %s公演' % (md(d), stime) if (multi and stime) else '%s公演' % md(d)
    if dend and dend != d:
        when = '%s〜%s公演' % (md(d), md(dend))

    tickets, has_live = [], False
    sales = p.get('performance_sales') or []
    names = [ticket_name(s.get('sales_name')) for s in sales]
    for i, s in enumerate(sales):
        st = (s.get('display_sales_status') or '').strip()
        if st not in KNOWN_ST:
            unknown[st] += 1
            continue                     # 知らない文言は載せない（嘘を作らない）
        if SELLER_SIDE.search(s.get('sales_name') or ''):
            continue
        nm = names[i]
        if names.count(nm) > 1:          # 同じ券種名が並ぶと画面で見分けられない
            nm = '%s%s' % (nm, '（%d）' % (names[:i].count(nm) + 1))
        head = '%s（%s %s）' % (nm, pref, when) if pref else '%s（%s）' % (nm, when)
        sd, sdt = raw_dt(s.get('sales_start_datetime_raw'))
        ed, edt = raw_dt(s.get('sales_end_datetime_raw'))
        url = s.get('destination_url') or ''
        if not url:
            continue                     # 飛び先が無い枠は載せない（買えないので）
        if st in PRE_ST:
            if not sd or sd < today:
                continue                 # 発売前なのに開始日が過去＝推測で日付を作らない
            tickets.append({'type': ('%s%s %s発売' % (head, md(sd), sdt or '')).rstrip(),
                            'date': sd, 'startDate': sd, 'url': url})
            has_live = True
        elif st in LIVE_ST:
            if not ed:
                continue
            end, endt = ed, edt
            # 締切が公演日より後なら公演日で締める（配信・視聴は例外）
            if end > (dend or d) and not re.search(r'配信|視聴|アーカイブ', nm):
                end, endt = (dend or d), ''
            tk = {'type': ('%s〜%s %s' % (head, md(end), endt or '')).rstrip(),
                  'date': end, 'url': url}
            if sd and sd >= today:
                # 今日から受付が始まる枠＝「本日発売」で出す（[[reference_eplus_harvest]]の決まり）
                tk['startDate'] = sd
                tk['type'] = ('%s%s %s発売〜%s %s'
                              % (head, md(sd), sdt or '', md(end), endt or '')).replace('  ', ' ').rstrip()
            tickets.append(tk)
            has_live = True
        else:
            tk = {'type': ('%s〜%s %s' % (head, md(ed), edt or '')).rstrip() if ed else head,
                  'date': ed or (dend or d), 'url': url, 'soldout': True,
                  'soldoutSince': today}
            if st == END_SALE:
                tk['saleEnded'] = True
                tk['saleEndedSince'] = today
            else:                        # 抽選受付終了＝先行が終わった（2026-09-20 新設のバッジ）
                tk['presaleEnded'] = True
            tickets.append(tk)

    if not tickets:
        return None, '載せられる枠が無い'
    # 🚨🚨2026-09-18 ユーザー決定＝**全部載せる**（[[feedback_oshinavi_concept]]）。
    #   「カウントダウンがメインというわけではなく、推し活がしやすいを目指してるわけだから、
    #     全部載せてほしい」＝**公演がこれからなら**売切れ・先行終了だけでも印を付けて載せる。
    #   ⛔旧＝買える枠が1つも無ければ載せない。2026-09-21 の初回投入でこれを入れてしまい、
    #      85件を落としていた（TIGET側は9/18に同じ条件を外してある）。has_live は数えるだけ。

    # まったく同じ枠は1つに畳む（飛び先が違うなら畳まない＝[[feedback_dedup_badges_keeps_urls]]）
    seen, uniq = set(), []
    for t in tickets:
        k = (t.get('type'), t.get('date'), t.get('startDate'), t.get('url'),
             bool(t.get('soldout')), bool(t.get('saleEnded')), bool(t.get('presaleEnded')))
        if k in seen:
            continue
        seen.add(k)
        uniq.append(t)

    gs = [FANY_GENRE[g] for g in genre_map.get(str(p.get('id')), []) if g in FANY_GENRE]
    gs = list(dict.fromkeys(gs)) or [GENRE_FALLBACK]
    label = jp(d, ('%s開演' % stime) if stime else '')
    if dend and dend != d:
        label = '%s〜%s' % (jp(d), jp(dend))
    return {
        'id': None,
        'artist': artist_of(p),
        'name': name,
        'date': d,
        'dateLabel': label,
        'venue': venue,
        'prefecture': pref,
        'genre': 'new',
        '_genre': gs[0],
        '_extraGenres': gs[1:],
        '_srcgenre': 'fany:%s' % ','.join(genre_map.get(str(p.get('id')), []) or ['?']),
        'price': None,
        'links': {'rakuten': None, 'lawson': None, 'pia': None, 'eplus': None,
                  'fany': 'https://ticket.fany.lol/event/detail/%s' % p.get('event_id')},
        'tickets': uniq,
        'verified': True,
        'verifiedAt': today,
    }, None


def build_all(path, out_path, today):
    d = json.load(open(path, encoding='utf-8'))
    perfs = d['performances']
    gmap = dict(d.get('genre_map') or {})
    same = collections.Counter()
    for p in perfs:
        iso = perf_date_iso(p)
        if iso:
            same[(p.get('event_id'), iso, p.get('venue_id'))] += 1
    gmap['_same_day'] = same

    unknown = collections.Counter()
    built, why = [], collections.Counter()
    for p in perfs:
        e, reason = build_one(p, today, gmap, unknown)
        if e:
            built.append(e)
        else:
            why[reason] += 1
    with io.open(out_path, 'w', encoding='utf-8') as f:
        json.dump(built, f, ensure_ascii=False, indent=1)
    print('組めた %d件 / 公演 %d件 → %s' % (len(built), len(perfs), out_path))
    print('枠 %d枠（買える・発売前・終わった印すべて）'
          % sum(len(e['tickets']) for e in built))
    for k, n in why.most_common():
        print('  載せなかった: %-40s %d件' % (k, n))
    if unknown:
        print('🚨知らない売り状態の文言（載せていない）: %s' % dict(unknown))
    g = collections.Counter(e['_genre'] for e in built)
    print('  ジャンル: %s' % dict(g))
    return 0


def _selftest():
    today = '2026-09-21'
    gm = {'_same_day': {}}

    def mk(**kw):
        p = {'id': 1, 'event_id': 99, 'venue_id': 7, 'class': '01',
             'name': 'マンゲキお笑いライブSP', 'venue_name': 'よしもと漫才劇場（大阪府）',
             'performance_date': '2026/10/01(<span class="g-dayofweek">木</span>)',
             'valid_period_start_date': '', 'valid_period_finish_date': '',
             'start_time': '100000', 'open_start_time_text': '開場 09:40  開演 10:00',
             'performer_detail': '[漫才・落語]中川家／タカアンドトシ／トミーズ／レイザーラモン',
             'performance_sales': []}
        p.update(kw)
        return p

    def sale(st, s0='20260805100000', s1='20260930080000', nm='一般発売', url='https://x/reception/1/2'):
        return {'display_sales_status': st, 'sales_name': nm, 'prefecture_code': '27',
                'sales_start_datetime_raw': s0, 'sales_end_datetime_raw': s1,
                'destination_url': url}

    # ① 先着発売中＝買える枠。締切はそのまま、県と公演日が入る
    e, _ = build_one(mk(performance_sales=[sale('先着発売中')]), today, gm, collections.Counter())
    assert e and e['tickets'][0]['type'] == '一般発売（大阪 10/1公演）〜9/30 8:00', e['tickets'][0]
    assert e['artist'] == '中川家／タカアンドトシ／トミーズ', e['artist']
    assert e['venue'] == 'よしもと漫才劇場' and e['prefecture'] == '大阪'
    assert e['links']['fany'].endswith('/event/detail/99')
    assert e['dateLabel'] == '2026年10月1日(木) 10:00開演', e['dateLabel']

    # ② 締切が公演日より後なら公演日で締める
    e2, _ = build_one(mk(performance_sales=[sale('先着発売中', s1='20261010235900')]),
                      today, gm, collections.Counter())
    assert e2['tickets'][0]['date'] == '2026-10-01', e2['tickets'][0]
    assert e2['tickets'][0]['type'] == '一般発売（大阪 10/1公演）〜10/1', e2['tickets'][0]

    # ③ 抽選受付終了＝先行終了の印（消さずに残す）。
    #    🚨**買える枠が1つも無くても、公演がこれからなら載せる**（feedback_oshinavi_concept）
    e3, why3 = build_one(mk(performance_sales=[sale('抽選受付終了')]), today, gm, collections.Counter())
    assert e3 is not None, (e3, why3)
    assert e3['tickets'][0]['soldout'] and e3['tickets'][0]['presaleEnded'], e3['tickets'][0]
    e3b, _ = build_one(mk(performance_sales=[sale('先着発売中'), sale('抽選受付終了', nm='FANY ID抽選先行',
                                                                url='https://x/reception/9/2')]),
                       today, gm, collections.Counter())
    t = [x for x in e3b['tickets'] if 'FANY' in x['type']][0]
    assert t['soldout'] and t['presaleEnded'] and 'saleEnded' not in t, t

    # ④ 先着発売終了＝販売終了の印
    e4, _ = build_one(mk(performance_sales=[sale('先着発売中'), sale('先着発売終了', nm='早割',
                                                              url='https://x/reception/8/2')]),
                      today, gm, collections.Counter())
    t4 = [x for x in e4['tickets'] if '早割' in x['type']][0]
    assert t4['soldout'] and t4['saleEnded'], t4

    # ⑤ 発売前＝M/D HH:MM発売。開始日が過去の「発売前」は載せない（推測で日付を作らない）
    e5, _ = build_one(mk(performance_sales=[sale('先着発売前', s0='20260925110000')]),
                      today, gm, collections.Counter())
    assert e5['tickets'][0]['type'] == '一般発売（大阪 10/1公演）9/25 11:00発売', e5['tickets'][0]
    assert e5['tickets'][0]['startDate'] == '2026-09-25'
    e5b, why5 = build_one(mk(performance_sales=[sale('先着発売前', s0='20260901110000')]),
                          today, gm, collections.Counter())
    assert e5b is None, e5b

    # ⑥ 今日から受付が始まる枠＝本日発売の形（startDate==today）
    e6, _ = build_one(mk(performance_sales=[sale('先着発売中', s0='20260921100000')]),
                      today, gm, collections.Counter())
    assert e6['tickets'][0]['startDate'] == today
    assert e6['tickets'][0]['type'] == '一般発売（大阪 10/1公演）9/21 10:00発売〜9/30 8:00', e6['tickets'][0]

    # ⑦ 同じ日・同じ会場で2公演＝開演時刻をバッジに入れる
    gm2 = {'_same_day': {(99, '2026-10-01', 7): 3}}
    e7, _ = build_one(mk(performance_sales=[sale('先着発売中')]), today, gm2, collections.Counter())
    assert e7['tickets'][0]['type'].startswith('一般発売（大阪 10/1 10:00公演）'), e7['tickets'][0]

    # ⑧ 公演が終わっている／出す側／飛び先なし
    assert build_one(mk(performance_date='2026/09/20(<span>土</span>)',
                        performance_sales=[sale('先着発売中')]), today, gm,
                     collections.Counter())[0] is None
    assert build_one(mk(name='出店ブース申込', performance_sales=[sale('先着発売中')]),
                     today, gm, collections.Counter())[0] is None
    assert build_one(mk(performance_sales=[sale('先着発売中', url='')]),
                     today, gm, collections.Counter())[0] is None

    # ⑨ 知らない文言は載せない＋数える
    unk = collections.Counter()
    e9, why9 = build_one(mk(performance_sales=[sale('予定枚数終了')]), today, gm, unk)
    assert e9 is None and unk['予定枚数終了'] == 1, (e9, unk)

    # ⑩ 2027公演は R9年表記／期間もの（通し券）は「〜」で出す
    e10, _ = build_one(mk(performance_date='2027/02/11(<span>木</span>)',
                          performance_sales=[sale('先着発売中', s1='20270101120000')]),
                       today, gm, collections.Counter())
    assert 'R9年 2/11公演' in e10['tickets'][0]['type'], e10['tickets'][0]
    e11, _ = build_one(mk(class_='02', valid_period_start_date='2026/10/01(<span>木</span>)',
                          valid_period_finish_date='2026/10/03(<span>土</span>)',
                          performance_sales=[sale('先着発売中')]), today, gm, collections.Counter())
    assert '10/1〜10/3公演' in e11['tickets'][0]['type'], e11['tickets'][0]

    print('selftest OK')
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src', nargs='?')
    ap.add_argument('--out', default=None)
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.src:
        ap.error('ハーベスト結果のJSONを渡して（例 tmp/fany_0921.json）')
    today = datetime.date.today().isoformat()
    out = a.out or a.src.replace('.json', '_built.json')
    return build_all(a.src, out, today)


if __name__ == '__main__':
    sys.exit(main())
