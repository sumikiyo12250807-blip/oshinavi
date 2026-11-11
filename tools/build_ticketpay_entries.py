# -*- coding: utf-8 -*-
"""チケットペイのハーベスト結果から OSHINAVI のエントリを組む（T-SQUARE形テンプレート・2026-11-12 新設）。

  python tools/build_ticketpay_entries.py tmp/ticketpay_MMDD.json --out tmp/built_ticketpay_MMDD.json
  python tools/build_ticketpay_entries.py --selftest

## ページの形と枠の単位
チケットペイの公演ページは **1ページ＝1公演日＝1つの販売期間**。その下に
  ・券種（`ticket_type_select` の「テーブル席(指定) 8,000円」）か
  ・席種ごとの状態（販売情報の「指定席 : 受付中」）
が並ぶ（無いページは「価格 : 4,000円」だけ）。締切は販売期間の終わり1つ。
＝**券種（無ければ席種）ごとに1枠**（TIGETと同じ＝券種ごとの売り切れを印で残せる）。どちらも無ければ「チケット」1枠。
抽選販売（販売情報の下に「抽選販売となります」）は枠名に「（抽選）」を足す。

## 売り状態（2026-11-12 実ページで確かめた文言）
| ページ上の札（event_mark） | 券種・席種 | OSHINAVI |
|---|---|---|
| 受付前     | ― | 発売前＝「M/D HH:MM発売〜M/D HH:MM」・startDate＝発売日・date＝締切 |
| 受付期間中 | 受付中・残りわずか・（印なし） | 買える＝「〜M/D HH:MM」・date＝締切 |
| 受付期間中 | 完売・売切 | `soldout`（予定枚数終了） |
| 完売       | ― | 全枠 `soldout` |
| 受付終了   | ― | 全枠 `soldout`＋`saleEnded`（販売終了） |
| それ以外   | 読めない札 | 🚨推測しない＝枠を作らず報告（発売中にしない） |

🚨発売前で開始日時が読めない＝日付を作らない＝その枠は載せない（報告）。
🚨締切が書いていない受付中＝「〜公演日」の販売中（TIGET・livePocket と同じ 2026-09-27 ユーザー決定）。
🚨締切が公演日（最終日）より後なら公演日で締める（配信・視聴・アーカイブは例外）。
🚨2027年以降の公演日は「R9年 」を付ける（締切・発売日の側は年なし＝livePocket・ZAIKO と同じ流儀）。

## 載せないもの
- 出す側の申込（出店・出展・出演者募集・参加エントリー・案内登録）＝[[feedback_oshinavi_concept]]
- セミナー・ビジネス系（チケットペイのカテゴリ「トーク・セミナー」に混ざる）＝TIGETの CAT_SKIP と同じ線
- 公演が終わっている／公演日が2年より先（主催者の試し書き）

## ジャンル＝売り場のカテゴリを機械で写す（[[feedback_genre_pia_asis_and_other]]）
カテゴリは個別ページに無いので、ハーベストが一覧から引いた `cats` を使う。
迷うカテゴリ（レジャー＝ボートレース・観光など）は写さない＝ `_genre` 空（人が振り分ける）。
"""
import argparse
import collections
import datetime
import io
import json
import re
import sys
import unicodedata

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

WD = '月火水木金土日'
CAT_GENRE = {
    'Music': 'musicetc',     # 音楽・フェス … 売り場の分け方がこれ1つ＝細かいジャンル（jazz 等）は名前から当てない＝その他
    'Drama': 'engeki',       # 舞台・演劇
    'Sports': 'sports',      # スポーツ・格闘技（プロレス DDT・東京女子 等）
    'Talk': 'talkshow',      # トーク・セミナー（セミナーは下の SEMINAR で外す）
    'Screening': 'movie',    # 上映会
    'Animation': 'anime',    # アニメ・特撮
    'Event': 'event',        # イベント
    'Leisure': '',           # レジャー … ボートレース・観光・体験が混ざる＝迷ったら写さない（_genre 空）
}
CAT_NAME = {'Music': '音楽・フェス', 'Drama': '舞台・演劇', 'Sports': 'スポーツ・格闘技', 'Talk': 'トーク・セミナー',
            'Screening': '上映会', 'Animation': 'アニメ・特撮', 'Leisure': 'レジャー', 'Event': 'イベント'}

SELLER_SIDE = re.compile(
    r'委託販売|即売会|出店|出展|ブース(?:出展|出店|申込)|サークル参加|'
    r'エントリーフォーム|参加エントリ|出場エントリ|出演エントリ|出演者募集|出演申込|出演者[】\]]?\s*参加受付|'
    r'案内登録|先行案内|協賛'
)
# セミナー・ビジネス系（推しに会いに行く枠ではない）。⚠️「講演会」「トークショー」は載せる（TIGETの46と同じ）
SEMINAR = re.compile(r'セミナー|勉強会|ビジネス|経営|投資|資産運用|起業|研修|説明会|相談会|講習会|資格試験|ウェビナー')
STREAM = re.compile(r'配信(?!なし|無し)|視聴(?!覚)|アーカイブ')

MARK_STATE = {'受付期間中': 'live', '受付前': 'unopened', '完売': 'soldout', '受付終了': 'closed'}
LIVE_SUB = ('受付中', '残りわずか', '残り僅か', '残少', '')
SOLD_SUB = ('完売', '売切', '売切れ', '売り切れ', '予定枚数終了', 'SOLD OUT')
CLOSED_SUB = ('受付終了', '販売終了')


def era(y, today_year):
    return 'R%d年 ' % (y - 2018) if y > today_year else ''


def md(iso, today_year):
    """公演日のバッジ用＝翌年以降は令和略記（[[feedback_r9_year_notation]]）。"""
    y, m, d = int(iso[:4]), int(iso[5:7]), int(iso[8:10])
    return '%s%d/%d' % (era(y, today_year), m, d)


def mdp(iso):
    """発売日・締切用＝年を付けない（livePocket・ZAIKO と同じ流儀）。"""
    return '%d/%d' % (int(iso[5:7]), int(iso[8:10]))


def jp(iso):
    y, m, d = int(iso[:4]), int(iso[5:7]), int(iso[8:10])
    return '%d年%d月%d日(%s)' % (y, m, d, WD[datetime.date(y, m, d).weekday()])


def short_pref(p):
    p = (p or '').strip()
    if p and p != '北海道' and p[-1] in '都府県':
        return p[:-1]
    return p


_PAIRS = ('（）', '「」', '『』', '【】', '＜＞', '〔〕', '［］', '〈〉')


def _balanced(s):
    return all(s.count(a) == s.count(b) for a, b in _PAIRS)


def ticket_name(raw, suffix=''):
    """券種名を整える（記号を check_badges が通す形に・28字・カッコの途中で切らない）。足す札は切った後に足す。"""
    nm = re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', raw or '')).strip()
    nm = re.sub(r'\s*\d{4}年\d{1,2}月\d{1,2}日.*$', '', nm).strip()
    nm = re.sub(r'\s*[\d,]+\s*円\s*$', '', nm).strip()          # 後ろの値段は落とす（値段の違いは別の枠で見える）
    if re.search(r'開場|開演|終演', nm):
        nm = 'チケット'
    nm = (nm.replace('／', '・').replace('(', '（').replace(')', '）')
            .replace('[', '［').replace(']', '］').replace('～', '〜').replace('<', '＜').replace('>', '＞'))
    if not nm or re.fullmatch(r'[・\s]*', nm):
        nm = 'チケット'
    if suffix and suffix.strip('（）') in nm:
        suffix = ''
    cut = nm[:28 - len(suffix)]
    while cut and not _balanced(cut):
        cut = cut[:-1]
    cut = cut.rstrip('・、 ')
    return (cut or 'チケット') + suffix


def sub_state(status, soldout_flag=False):
    s = (status or '').strip()
    if soldout_flag or any(x in s for x in SOLD_SUB):
        return 'soldout'
    if any(x in s for x in CLOSED_SUB):
        return 'closed'
    if s in LIVE_SUB:
        return 'live'
    return 'unknown'


LIST_STATE = {'after_release': 'live', 'before_release': 'unopened'}


def page_state_of(ev):
    """ページの札 → 状態。🚨「公演日時をお選びください」の型（65436〜65443 POP☆SWEET・65336〜65340 わたあめ工場）は
    ページの上に札が出ない＝**カテゴリ一覧の札**（販売中(…まで)／受付前(…から)／完売／受付終了）を使う（どちらも売り場の表示）。
    どちらも無い・読めない＝None（発売中にしない）。返り値＝(状態, どこから読んだか)"""
    mark = (ev.get('mark') or '').strip()
    if mark:
        return MARK_STATE.get(mark), 'ページの札'
    lc, ls = ev.get('list_class') or '', (ev.get('list_status') or '').strip()
    if lc in LIST_STATE and ls.startswith(('販売中', '受付前')):
        return LIST_STATE[lc], '一覧の札'
    if lc == 'sold_out':
        if ls == '完売':
            return 'soldout', '一覧の札'
        if ls == '受付終了':
            return 'closed', '一覧の札'
    return None, ''


def artist_of(ev, name):
    """出演者の欄。「あり/なし/未定/TBA」は名前にしない（2026-11-12 ぴあの抜き打ちと同じ型）。
    楽器の札「(Vo/key)」を落とし、読点・スラッシュ・2つ以上の空白で区切って「／」でつなぐ。
    1つの空白は名前の中の空白かもしれないので区切らない（推測しない）。無ければ公演名。"""
    raw = unicodedata.normalize('NFKC', ev.get('performers_raw') or '').strip()
    # 名前の前に付いた楽器・役の札「(Vo/key)」「(作編曲/Key/G)」を落とす（名前の後ろの読み「(しのあやね)」は残す）
    raw = re.sub(r'(?:(?<=^)|(?<=[\s、,／/]))[(（][^()（）]{1,20}[)）](?=\S)', '', raw)
    if not raw or re.fullmatch(r'(あり|なし|無し|未定|TBA|調整中|後日発表|ほか|他|-|ー)+', raw.replace(' ', '')):
        return name
    parts = [p.strip() for p in re.split(r'[、,，/／]|\s{2,}|　', raw) if p.strip()]
    # 役の札（「主演・」「出演：」「MC：」「レジデントDJ:」）と後ろの「他」「ほか」は名前ではない
    parts = [re.sub(r'\s*(他|ほか|ほか多数|他多数)$', '',
                    re.sub(r'^(主演|出演|出演者|MC|ゲスト|司会)\s*[・:：]\s*|^[^:：\s]{1,12}[:：]\s*', '', p)).strip()
             for p in parts]
    parts = [p for p in parts if p and p not in ('未定', 'TBA', '調整中')]
    # 文章の形（「◎11月13日…出演：…」・空白で10人並べた型）は名前と言い切れない＝公演名のまま（推測しない）
    if not parts or any(re.search(r'[:：◎]', p) or p.count(' ') > 3 for p in parts):
        return name
    out = '／'.join(dict.fromkeys(parts))
    return out if len(out) <= 80 else name


def build(ev, today, unknown=None):
    """1ページ＝1エントリ。載せられないときは (None, 理由)。"""
    unknown = unknown if unknown is not None else collections.Counter()
    ty = int(today[:4])
    name = re.sub(r'\s+', ' ', ev.get('name') or '').strip()
    if not name:
        return None, '公演名が読めない'
    # 公演名が出す側なら丸ごと外す。券種だけ出す側（「出店ブース」券）は下でその枠だけ外す
    if SELLER_SIDE.search(name):
        return None, '出す側の申込（出店・出展・出演エントリー・案内登録）'
    if SEMINAR.search(name):
        return None, 'セミナー・ビジネス系＝推しに会いに行く枠ではない'
    dates = sorted(set(ev.get('dates') or []))
    if not dates:
        return None, '開催日が読めない'
    first, last = dates[0], dates[-1]
    stream_ev = bool(STREAM.search(name)) or bool(re.match(r'\s*(オンライン|配信)', ev.get('venue') or ''))
    per = ev.get('period') or {}
    st, en = per.get('start'), per.get('end')
    if last < today and not (stream_ev and en and en[0] >= today):
        return None, '公演が終わっている'
    if first > (datetime.date.fromisoformat(today) + datetime.timedelta(days=730)).isoformat():
        return None, '公演日が2年より先＝主催者の試し書きの疑い'

    pref = short_pref(ev.get('prefecture'))
    stime = ev.get('start_time') or ''
    if first == last:
        when = '%s %s公演' % (md(first, ty), stime) if stime else '%s公演' % md(first, ty)
        label = jp(first) + (' %s開演' % stime if stime else '')
    else:
        # 同じ年の範囲は頭だけ年の札（「R9年 2/20〜2/21」＝ぴあの mdbadge と同じ）
        when = '%s〜%s' % (md(first, ty), md(last, ty) if last[:4] != first[:4] else mdp(last))
        label = '%s〜%s' % (jp(first), jp(last))
    url = ev['url']
    page_state, state_src = page_state_of(ev)
    if page_state is None:
        unknown[('ページの札', ev.get('mark') or '', ev.get('list_status') or '')] += 1
        return None, '読めない札：%s（発売中にしない）' % (ev.get('mark') or ev.get('list_status') or '札なし')
    # 🚨受付中の札でも販売期間の終わりが過ぎていたら買えない（一覧の札が遅れる＝65437 11/11 22:00 締切が11/12も「販売中」）
    #   ＝販売期間どおり「販売終了」にする（発売中にしない）
    if page_state == 'live' and en and en[0] < today:
        page_state, state_src = 'closed', '販売期間の終わりが過ぎた'

    # 枠の単位＝券種 → 無ければ席種 → 無ければ「チケット」1枠
    units = []
    for t in ev.get('types') or []:
        units.append({'name': t.get('name') or '', 'price': t.get('price'),
                      'sub': 'soldout' if t.get('soldout') else 'live'})
    if not units:
        for s in ev.get('seats') or []:
            st_ = s.get('status') or ''
            if s.get('soldout'):
                sub = 'soldout'
            elif s.get('price') is not None or st_ in LIVE_SUB:
                sub = 'live'                       # 「S席 : 7,800円」＝値段だけ＝印なし＝受付中の札に従う
            elif st_ == '受付前':
                sub = 'live' if page_state == 'unopened' else 'unknown'
            else:
                sub = sub_state(st_)
            units.append({'name': s.get('name') or '', 'price': s.get('price'), 'sub': sub, 'raw_status': st_})
    if not units:
        units.append({'name': 'チケット', 'price': None, 'sub': 'live'})
    lot = '（抽選）' if ev.get('lottery') else ''
    names = [ticket_name(u['name'], lot) for u in units]
    tickets, skipped = [], []

    def cap(e, is_stream):
        if e and e[0] > last and not is_stream:
            return (last, '')
        return e
    for u, nm in zip(units, names):
        if SELLER_SIDE.search(u['name']):
            skipped.append((u['name'], '出す側の券種'))
            continue
        if names.count(nm) > 1 and u.get('price') is not None:
            nm = '%s %s円' % (nm, format(u['price'], ','))
        is_stream = stream_ev or bool(STREAM.search(nm))
        head = '%s（%s %s）' % (nm, pref, when) if pref else '%s（%s）' % (nm, when)
        state = page_state
        if page_state == 'live':
            if u['sub'] == 'unknown':
                unknown[('席種の札', u.get('raw_status'))] += 1
                skipped.append((u['name'], '読めない札：%s' % u.get('raw_status')))
                continue
            state = u['sub']
        if state == 'unopened':
            if not st:
                skipped.append((u['name'], '発売前なのに開始日時が読めない＝日付を作らない'))
                continue
            e2 = cap(en, is_stream) if en else (last, '')
            tickets.append({'type': ('%s%s %s発売〜%s %s' % (head, mdp(st[0]), st[1], mdp(e2[0]), e2[1]))
                            .replace('  ', ' ').rstrip(), 'date': e2[0], 'startDate': st[0], 'url': url})
        elif state == 'live':
            if en:
                e2 = cap(en, is_stream)
                tickets.append({'type': ('%s〜%s %s' % (head, mdp(e2[0]), e2[1])).rstrip(), 'date': e2[0], 'url': url})
            else:
                tickets.append({'type': '%s〜%s' % (head, mdp(last)), 'date': last, 'url': url})
        elif state in ('soldout', 'closed'):
            e2 = cap(en, is_stream) if en else None
            tk = {'type': ('%s〜%s %s' % (head, mdp(e2[0]), e2[1])).rstrip() if e2 else head,
                  'date': e2[0] if e2 else last, 'url': url, 'soldout': True, 'soldoutSince': today}
            if state == 'closed':
                tk['saleEnded'] = True
                tk['saleEndedSince'] = today
            tickets.append(tk)
    if last < today:
        tickets = [t for t in tickets if (t.get('date') or '') >= today]
    seen, uniq = set(), []
    for t in tickets:
        k = (t['type'], t['date'], t.get('startDate'), t['url'], bool(t.get('soldout')), bool(t.get('saleEnded')))
        if k not in seen:
            seen.add(k)
            uniq.append(t)
    if not uniq:
        return None, '載せられる枠が無い' + ('：' + skipped[0][1] if skipped else '')

    genres = []
    for c in ev.get('cats') or []:
        if c not in CAT_GENRE:
            unknown[('カテゴリ', c)] += 1
            continue
        g = CAT_GENRE[c]
        if g and g not in genres:
            genres.append(g)
    e = {
        'artist': artist_of(ev, name),
        'name': name,
        'date': last,
        'dateLabel': label,
        'venue': re.sub(r'\s*会場座席図を確認する\s*', ' ', ev.get('venue') or '').strip() or '（会場未定）',
        'prefecture': pref,
        'genre': 'new',
        '_genre': genres[0] if genres else '',
        '_extraGenres': genres[1:],
        '_srcgenre': 'ticketpay:' + ','.join(ev.get('cats') or []),
        'price': None,
        'links': {'rakuten': None, 'lawson': None, 'pia': None, 'eplus': None, 'ticketpay': url},
        'tickets': uniq,
        'verified': True,
        'verifiedAt': today,
    }
    if skipped:
        e['_skipped_slots'] = skipped
    if state_src != 'ページの札':
        e['_stateFrom'] = state_src
    if ev.get('sibling_ids'):
        e['_siblings'] = ev['sibling_ids']        # 同じ公演の別日時（それぞれ別ページ＝別カード）
    if not genres:
        e['_review'] = ['ジャンル未決（カテゴリ：%s）' % ('・'.join(CAT_NAME.get(c, c) for c in ev.get('cats') or []) or 'なし')]
    return e, None


def _selftest():
    today = '2026-11-12'

    def ev(**kw):
        base = {'id': 1, 'url': 'https://www.ticketpay.jp/booking/?event_id=1', 'name': 'JAYWALK 不思議で素敵なクリスマス',
                'mark': '受付期間中', 'venue': '目黒 BLUES ALLEY JAPAN', 'prefecture': '東京', 'dates': ['2026-12-03'],
                'start_time': '19:00', 'performers_raw': '(Vo/key)杉田裕  (Vo/G)知久光康',
                'period': {'start': ['2026-10-27', '14:00'], 'end': ['2026-11-30', '23:59']},
                'types': [], 'seats': [], 'lottery': False, 'cats': ['Music']}
        base.update(kw)
        return base
    # ① 受付中・券種なし＝1枠「チケット」・締切＝販売期間の終わり・カードの date＝公演日
    e, why = build(ev(), today)
    assert e and e['tickets'] == [{'type': 'チケット（東京 12/3 19:00公演）〜11/30 23:59', 'date': '2026-11-30',
                                   'url': 'https://www.ticketpay.jp/booking/?event_id=1'}], e['tickets']
    assert e['date'] == '2026-12-03' and e['dateLabel'] == '2026年12月3日(木) 19:00開演', e
    assert e['artist'] == '杉田裕／知久光康', e['artist']
    assert e['_genre'] == 'musicetc' and e['genre'] == 'new' and e['links']['ticketpay'].endswith('=1')
    # ② 券種ごとに1枠・券種の完売は soldout の印で残す（取りこぼさない）
    e, _ = build(ev(types=[{'name': 'テーブル席(指定)', 'price': 8000, 'soldout': False},
                           {'name': 'DinnerSet(指定）', 'price': 16500, 'soldout': True}]), today)
    assert len(e['tickets']) == 2, e['tickets']
    assert e['tickets'][0]['type'] == 'テーブル席（指定）（東京 12/3 19:00公演）〜11/30 23:59' and not e['tickets'][0].get('soldout')
    assert e['tickets'][1]['soldout'] is True and 'saleEnded' not in e['tickets'][1]
    # ③ 受付前＝発売日つき・date＝締切（発売日にしない）・2027年は R9年（締切側は年なし）
    e, _ = build(ev(mark='受付前', dates=['2027-04-03'], start_time='18:00',
                    period={'start': ['2027-02-02', '12:00'], 'end': ['2027-04-03', '0:00']}), today)
    t = e['tickets'][0]
    assert t['type'] == 'チケット（東京 R9年 4/3 18:00公演）2/2 12:00発売〜4/3 0:00', t
    assert t['date'] == '2027-04-03' and t['startDate'] == '2027-02-02', t
    assert e['dateLabel'].startswith('2027年4月3日'), e['dateLabel']
    # ④ 受付前で開始が読めない＝日付を作らない＝載せない
    e, why = build(ev(mark='受付前', period={'start': None, 'end': ['2026-11-30', '23:59']}), today)
    assert e is None and '開始日時' in why, why
    # ⑤ 完売・受付終了は売り場の表示どおり
    e, _ = build(ev(mark='完売'), today)
    assert e['tickets'][0]['soldout'] and 'saleEnded' not in e['tickets'][0]
    e, _ = build(ev(mark='受付終了'), today)
    assert e['tickets'][0]['soldout'] and e['tickets'][0]['saleEnded']
    # ⑥ 分からない札は発売中にしない
    e, why = build(ev(mark='一時停止中'), today)
    assert e is None and '読めない札' in why, why
    e, why = build(ev(seats=[{'name': '指定席', 'status': '調整中'}]), today)
    assert e is None, e
    # ⑦ 席種の完売・受付中
    e, _ = build(ev(seats=[{'name': '指定席', 'status': '受付中'}, {'name': '自由席', 'status': '完売'}]), today)
    assert [bool(x.get('soldout')) for x in e['tickets']] == [False, True], e['tickets']
    # ⑧ 締切が公演日より後なら公演日で締める
    e, _ = build(ev(period={'start': ['2026-10-01', '10:00'], 'end': ['2026-12-31', '23:59']}), today)
    assert e['tickets'][0]['date'] == '2026-12-03' and e['tickets'][0]['type'].endswith('〜12/3'), e['tickets']
    # ⑨ 公演が終わった・出す側・セミナーは外す
    assert build(ev(dates=['2026-11-01']), today)[0] is None
    assert build(ev(name='冬の即売会 出店者募集'), today)[0] is None
    assert build(ev(name='副業で稼ぐ起業セミナー', cats=['Talk']), today)[0] is None
    assert build(ev(name='〇〇講演会', cats=['Talk']), today)[0]['_genre'] == 'talkshow'
    # ⑩ 抽選は枠名に（抽選）
    e, _ = build(ev(lottery=True), today)
    assert e['tickets'][0]['type'].startswith('チケット（抽選）（東京'), e['tickets'][0]
    # ⑪ 出演者「未定」は名前にしない・県が無ければバッジから県を落とす
    e, _ = build(ev(performers_raw='未定', prefecture=''), today)
    assert e['artist'] == e['name'] and e['tickets'][0]['type'].startswith('チケット（12/3 19:00公演）'), e
    # ⑫ レジャー＝ジャンルを写さない（_genre 空・人が見る）
    e, _ = build(ev(cats=['Leisure']), today)
    assert e['_genre'] == '' and e['_review'], e
    # ⑬ 締切の無い受付中＝〜公演日
    e, _ = build(ev(period={'start': ['2026-10-01', '10:00'], 'end': None}), today)
    assert e['tickets'][0]['type'].endswith('〜12/3') and e['tickets'][0]['date'] == '2026-12-03'
    # ⑱ 出演者の札・文章の形
    e, _ = build(ev(performers_raw='(作編曲/Key/G/B/Ds)松井秋彦 (Vo)前田祐希'), today)
    assert e['artist'] == '松井秋彦 前田祐希' or e['artist'] == '松井秋彦／前田祐希', e['artist']
    e, _ = build(ev(performers_raw='レジデントDJ：Okyo、UKKEY / ゲストDJ：未定'), today)
    assert e['artist'] == 'Okyo／UKKEY', e['artist']
    e, _ = build(ev(performers_raw='◎11月13日(金)13時 「落語演劇」 出演：関 智一 長沢美樹'), today)
    assert e['artist'] == e['name'], e['artist']
    e, _ = build(ev(performers_raw='主演・村田寛奈／安未紗', venue='新木場1stRING 会場座席図を確認する'), today)
    assert e['artist'] == '村田寛奈／安未紗' and e['venue'] == '新木場1stRING', e
    # ⑲ 同じ年の範囲は頭だけ R9年
    e, _ = build(ev(dates=['2027-02-20', '2027-02-21'], period={'start': ['2026-11-01', '10:00'], 'end': ['2027-02-21', '18:59']}), today)
    assert '（東京 R9年 2/20〜2/21）' in e['tickets'][0]['type'], e['tickets'][0]
    # ⑭ ページに札が無い型は一覧の札を使う・どちらも無ければ載せない
    e, _ = build(ev(mark='', list_class='after_release', list_status='販売中(2026/11/30 (月) 23:59まで)'), today)
    assert e and not e['tickets'][0].get('soldout') and e['_stateFrom'] == '一覧の札', e
    e, _ = build(ev(mark='', list_class='sold_out', list_status='完売'), today)
    assert e['tickets'][0]['soldout'] and 'saleEnded' not in e['tickets'][0]
    assert build(ev(mark='', list_class='', list_status=''), today)[0] is None
    # ⑮ 受付中の札でも販売期間が過ぎていたら販売終了（発売中にしない）
    e, _ = build(ev(dates=['2026-11-12'], period={'start': ['2026-11-01', '12:00'], 'end': ['2026-11-11', '22:00']}), today)
    assert e['tickets'][0]['saleEnded'] and e['tickets'][0]['soldout'], e['tickets']
    # ⑯ 席種の行が値段だけ＝受付中・「※完売」＝soldout
    e, _ = build(ev(seats=[{'name': 'SS席', 'status': '8,800円 ※完売', 'price': 8800, 'soldout': True},
                           {'name': 'S席', 'status': '7,800円', 'price': 7800, 'soldout': False}]), today)
    assert [bool(x.get('soldout')) for x in e['tickets']] == [True, False], e['tickets']
    # ⑰ 開催期間（物販・配信）＝初日〜最終日の会期
    e, _ = build(ev(dates=['2026-11-18', '2026-12-09'], name='＜アーカイブ視聴券＞公演', start_time='12:00',
                    period={'start': ['2026-11-07', '12:00'], 'end': ['2026-12-09', '20:59']}), today)
    assert e['dateLabel'] == '2026年11月18日(水)〜2026年12月9日(水)' and e['date'] == '2026-12-09', e
    assert e['tickets'][0]['type'] == 'チケット（東京 11/18〜12/9）〜12/9 20:59', e['tickets'][0]
    print('selftest OK（一覧の札・期間切れは販売終了・席種の値段行・開催期間／1枠/券種・券種の完売・受付前の締切・R9年・開始なしは作らない・完売/受付終了・読めない札・'
          '締切を公演日で締める・終演/出す側/セミナー・抽選・未定・県なし・レジャー）')
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('--out', default='tmp/built_ticketpay.json')
    ap.add_argument('--today', default=datetime.date.today().isoformat())
    a = ap.parse_args()
    d = json.load(open(a.src, encoding='utf-8'))
    out, skipped, unknown = [], [], collections.Counter()
    for ev in d['events']:
        e, why = build(ev, a.today, unknown)
        if e:
            out.append(e)
        else:
            skipped.append({'id': ev['id'], 'name': ev.get('name'), 'why': why, 'url': ev['url']})
    out.sort(key=lambda e: (e['date'], e['name']))
    json.dump({'entries': out, 'skipped': skipped, 'unknown': [[list(k), v] for k, v in unknown.items()]},
              io.open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('=== 組み上がり %d件 / 載せない %d件 → %s ===' % (len(out), len(skipped), a.out))
    why = collections.Counter(re.sub(r'：.*', '', s['why']) for s in skipped)
    for k, v in why.most_common():
        print('  %s: %d件' % (k, v))
    for k, v in unknown.most_common():
        print('  ⚠️読めない %s: %d' % (k, v))
    g = collections.Counter(e['_genre'] or '(空)' for e in out)
    print('  ジャンル: ' + ' / '.join('%s %d' % kv for kv in g.most_common()))


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        _selftest()
        sys.exit(0)
    main()
