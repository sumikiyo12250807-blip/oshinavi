# -*- coding: utf-8 -*-
"""楽天チケットの収集結果(rakuten_harvest.py)を OSHINAVI エントリに機械構築する。

  python tools/build_rakuten_entries.py tmp/rakuten_fresh.json --start-id 3236 > tmp/built_rakuten.json
  python tools/build_rakuten_entries.py --selftest

【設計メモ】
- **締切が書かれていない販売枠**（楽天は「一般発売 2026/07/25(土) 10:00 〜」で終わりが空のことが多い）は
  嘘の締切を作らず **date=公演日（千秋楽）＋ saleEndUnknown=true** にする。
  ＝[[feedback_sale_end_cap_show_date]]（受付終了が公演日より後なら公演日で締める）と
    [[feedback_no_placeholder_dates]]（仮置き禁止）の両立。check_expired が⚠️要再確認に出してくれる。
- **startDate==date の単日形は作らない**。隠れ枠ヒール(heal_stale_deadlines)は**ぴあ専用**なので、
  楽天で単日形を作ると発売日の翌日から画面から消えたまま誰も直せない（[[feedback_delete_nonpia_blindspot]]）。
- バッジ表記は [[feedback_badge_date_full_form]]（完全M/D形・（県 M/D公演）を必ず入れる）に合わせる。
- 楽天URLは必ず Deep Link 化（[[feedback_rakuten_deeplink]]）。素URLは収益が出ない。
"""
import argparse
import datetime
import json
import re
import sys
import unicodedata
import urllib.parse

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, 'tools')

TODAY = datetime.date.today()

_HALF_KANA_RE = re.compile(r'[｡-ﾟ]+')


def venue_key(v):
    """会場名の表記ゆれを吸収した重複判定キー（半角/全角・空白・住所の〔〕[]注記を無視）"""
    s = unicodedata.normalize('NFKC', v or '')
    s = re.sub(r'〔.*?〕|\[.*?\]|（[^（）]*?[0-9-]+[^（）]*?）', '', s)
    return re.sub(r'\s+', '', s)


def fix_half_kana(s):
    """楽天HTMLは会場名に半角カナを返すことがある（ｽﾎﾟｰﾂﾊﾟｰｸ／Cｹﾞｰﾄ／ﾋﾞﾚｯｼﾞﾎｰﾙ）。
    OSHINAVI既存は全角なので、**半角カナの連続だけ** NFKC で全角化する。
    ぴあ側の norm_fw と違い全角ラテンや（）／〜には触らない＝最小限の正規化。
    2026-07-30 の目視で id3516 諏訪湖祭「Cｹﾞｰﾄ観覧席」を発見（既存も3224/3229/3232が汚染）。
    """
    if not isinstance(s, str) or not s:
        return s
    return _HALF_KANA_RE.sub(lambda m: unicodedata.normalize('NFKC', m.group(0)), s)
CD_GENRES = {'jpop', 'rock', 'idol', 'classic', 'jazz', 'anime', 'enka', 'kpop', 'yougaku', 'fes', 'dento'}
WD = '月火水木金土日'


def pref_short(p):
    p = (p or '').strip()
    if p == '北海道':
        return p
    return re.sub(r'[都府県]$', '', p)


def md(iso_s):
    y, m, d = iso_s.split('-')
    return '%d/%d' % (int(m), int(d))


def jp_date(iso_s):
    y, m, d = [int(x) for x in iso_s.split('-')]
    w = WD[datetime.date(y, m, d).weekday()]
    return '%d年%d月%d日(%s)' % (y, m, d, w)


def r9(iso_s):
    """2027年公演は R9年 表記（[[feedback_r9_year_notation]]）。"""
    y = int(iso_s[:4])
    return ('R9年 ' if y >= 2027 else '') + md(iso_s)


def perf_span(perfs):
    """公演日の範囲文字列（バッジ用）。単日は 8/15・複数は 8/29〜8/30。"""
    ds = sorted({p['date'] for p in perfs} | {p['end'] for p in perfs if p.get('end')})
    if not ds:
        return ''
    return r9(ds[0]) if len(ds) == 1 else '%s〜%s' % (r9(ds[0]), r9(ds[-1]))


# 🚨 楽天の timming は「2026/06/20(土) 10:00 〜 2026/06/23 (火) 23:59」＝**終了側だけ
# 日付と曜日カッコの間にスペースが入る**。旧regexは `(\d{2})\(` でスペースを許さず、
# 終了日を1つも拾えないまま len(ds)<2 で None を返していた。その結果、呼び出し側の
# 「締切が無ければ card_end(=data-dateのmax_end_on＝一番遅い締切)で埋める」フォールバックが
# 全枠に効き、**もう終わった先行が「まだ買える」として載る／生きた枠の締切が実際より遅く出る**
# という嘘の情報になっていた（2026-07-30発見・ウルトラヒーローズ岐阜=6/23締切の最速先行が
# 「〜9/11」と出ていた）。selftestが旧形式(スペース無し)で書かれていたので通り抜けていた。
_WIN_DT = r'(20\d{2})/(\d{2})/(\d{2})\s*\([^)]*\)\s*(\d{1,2}:\d{2})'


def win_end_iso(timming):
    ds = re.findall(_WIN_DT, timming or '')
    if len(ds) < 2:
        return None, None
    return '%s-%s-%s' % ds[1][:3], ds[1][3]


def win_start_iso(timming):
    ds = re.findall(_WIN_DT, timming or '')
    if not ds:
        return None, None
    return '%s-%s-%s' % ds[0][:3], ds[0][3]


def deeplink(u):
    if 'click.linksynergy.com' in u:
        return u
    return ('https://click.linksynergy.com/deeplink?id=z9x6HLNpWco&mid=53531&murl='
            + urllib.parse.quote(u, safe=''))


def amazon(name):
    q = urllib.parse.quote('%s CD' % name)
    return ('https://www.amazon.co.jp/s?k=%s&i=specialty-aps&srs=26200021051&tag=oshinavi0a-22' % q)


def build(recs, new_id):
    """同じ興行（正規化名が同じ）の楽天ページをまとめて1エントリにする。

    楽天は「乃木坂46 真夏の全国ツアー2026［東京］」「同［福岡］」のように**会場ごとに別ページ**。
    OSHINAVIはツアーを1エントリにまとめる（[[feedback_tour_consolidate]]）ので、
    ここで束ねて各バッジに会場別URLを付ける（[[feedback_tour_per_ticket_url]]）。
    """
    if isinstance(recs, dict):
        recs = [recs]
    rec = recs[0]
    today = TODAY.isoformat()
    perfs = []
    for r in recs:
        for p in r['perfs']:
            if (p.get('end') or p['date']) >= today:
                q = dict(p)
                q['_url'] = r['url']
                perfs.append(q)
    if not perfs:
        return None, '公演が全部過去'

    last = max((p.get('end') or p['date']) for p in perfs)
    prefs = []
    for p in perfs:
        s = pref_short(p['pref'])
        if s and s not in prefs:
            prefs.append(s)
    # 会場の重複除去は**表記ゆれを吸収したキー**で行う。素の文字列比較だと同じ会場が
    # 半角カナ／住所カッコ付き／空白違いで別会場に見え、1会場なのに
    # 「全国ツアー（モエレ沼公園／ﾓｴﾚ沼公園／モエレ沼公園）」になる（2026-07-30 id3229で発覚）。
    # 表示は同じ会場のうち**最短表記**を採る（住所付きの冗長な方を残さない）。
    venues, _vpick = [], {}
    for p in perfs:
        v = fix_half_kana((p.get('venue') or '').strip())
        if not v:
            continue
        k = venue_key(v)
        if k not in _vpick:
            _vpick[k] = v
            venues.append(v)
        elif len(v) < len(_vpick[k]):
            venues[venues.index(_vpick[k])] = v
            _vpick[k] = v

    tickets = []
    for r in recs:
        rp = [p for p in perfs if p['_url'] == r['url']]
        if not rp:
            continue
        # 🚨 販売期間に「終わり」が書かれていない窓は、公演カード(data-date)の販売終了日時で埋める。
        #    ただし **max() を全公演に流用してはいけない**＝早い公演に千秋楽の締切が付いて嘘になる
        #    （2026-09-09 ユーザーが画面で発見。id7502 ラフ×ラフ＝11/14の米子が「〜R9年4/3」、
        #      id7494 ジャパンオープンテニス＝9/28〜10/6の大会に9/30の締切）。
        #    カードは1枚ずつ自分の締切を持っている（実測＝11/14 13:00公演の max_end_on は
        #    2026-11-14T13:30）ので、**締切ごとに公演を束ねて枠を割る**。
        #    窓に締切が書いてある時は従来どおりツアー全体で1枠のまま（割ると同じ枠が増えるだけ）。
        #    🚨割る単位は「カードの締切ごと」ではなく **公演ごと**（同じ公演の券種違いは1枠にまとめる）。
        #      券種ごとに割ると、窓×券種の総当たりになって存在しない枠が生える。
        #      **1公演しかないページは割らない＝元から正しいので触らない**。
        #    [[feedback_sale_end_unknown_display]]／[[feedback_no_fake_info]]
        #    🚨同じ公演日・同じ会場で締切が同じなら昼夜も1枠にまとめる（画面に同じ表記が2つ並ぶだけ）。
        #      締切が違う時だけ割り、その時はバッジに開演時刻を入れて見分けられるようにする
        #      （[[feedback_same_day_show_time_badge]]）。
        # ①公演＝（公演日・会場・開演時刻）。同じ公演の券種違いは1公演にまとめて max を採る
        by_perf = {}
        for p in rp:
            by_perf.setdefault((p['date'], p.get('end') or '',
                                venue_key(p.get('venue') or ''), p.get('time') or ''), []).append(p)
        # ②締切が同じ公演は1枠にまとめる＝**枠の単位は締切**（同じ締切の公演を分けても
        #   画面に同じ日付の枠が並ぶだけ。さだまさし11/19と11/20は同じ11/11締切＝1枠が正しい）
        perf_end = {k: max((p.get('sale_end') or '') for p in g) for k, g in by_perf.items()}
        by_slot = {}
        for k, g in by_perf.items():
            by_slot.setdefault(perf_end[k], []).extend(g)
        # 同じ（公演日・会場）に締切違いが2つ以上＝バッジが同じ文字になって見分けられない
        seen_dv = {}
        for k in by_perf:
            seen_dv.setdefault(k[:3], set()).add(perf_end[k])
        amb_perf = {k for k in by_perf if len(seen_dv[k[:3]]) > 1}
        ambiguous = {ce: all(k in amb_perf for k in by_perf if perf_end[k] == ce)
                     for ce in by_slot}
        for w in r['windows']:
            sd, st = win_start_iso(w['timming'])
            ed0, et0 = win_end_iso(w['timming'])
            if not sd:
                continue
            if ed0 or len(by_perf) < 2:
                ce = max((p.get('sale_end') or '') for p in rp)
                chunks = [(rp, ed0, et0, False)] if ed0 else [(rp, (ce[:10] or None), ce[11:16], False)]
            else:
                chunks = []
                for ce in sorted(by_slot, key=lambda s: s or '9999'):
                    chunks.append((by_slot[ce], (ce[:10] or None), ce[11:16], ambiguous[ce]))
            for gp, ed, et, need_time in chunks:
                if ed and ed < today:
                    continue                           # 締切済み＝載せない
                span = perf_span(gp)
                pref_txt = '・'.join(dict.fromkeys(pref_short(p['pref']) for p in gp if p['pref']))
                last_r = max((p.get('end') or p['date']) for p in gp)
                # 開演時刻を入れるのは2つの時だけ（[[feedback_same_day_show_time_badge]]・増やさない）
                #   ①同じ公演日・会場に締切違いが並ぶ（バッジが同じ文字になって見分けられない）
                #   ②受付の締切が公演当日にある（何時の回に間に合う締切か分からない）
                same_day = bool(ed) and {ed} == {p['date'] for p in gp}
                if (need_time or same_day) and all(p.get('time') for p in gp):
                    tms = '・'.join(dict.fromkeys(p['time'] for p in gp))
                    if tms and '〜' not in span:
                        span = '%s %s' % (span, tms)
                label = re.sub(r'\s+', ' ', w['type'] or '一般発売').strip()
                t = {}
                if ed:
                    # 受付終了が公演日より後なら公演日で締める（[[feedback_sale_end_cap_show_date]]）
                    if ed > last_r:
                        ed, et = last_r, ''
                    t['type'] = ('%s（%s %s公演）〜%s %s' % (label, pref_txt, span, r9(ed), et)).strip()
                    t['date'] = ed
                else:
                    t['type'] = '%s（%s %s公演）〜%s公演日' % (label, pref_txt, span, r9(last_r))
                    t['date'] = last_r
                    t['saleEndUnknown'] = True
                if sd > today:
                    t['startDate'] = sd
                    t['type'] = t['type'].replace('公演）', '公演）%s %s発売 ' % (r9(sd), st), 1).strip()
                if t.get('startDate') == t['date'] or sd == t['date']:
                    # 発売日=締切日の単日形＝当日券。そのままだと「隠れ枠」になり、
                    # ヒール(heal_stale_deadlines)はぴあ専用なので誰も直せず画面から消える。
                    # 当日券は事実として「売り切れ次第終了」なのでフラグを立てて除外対象にする。
                    t['saleUntilSoldOut'] = True
                t['url'] = deeplink(r['url'])
                tickets.append(t)

    # 同じ表記・同じ締切・同じ飛び先の枠は1つにする。楽天は「一般発売」を販売枠に2つ
    # 並べることがあり（片方に終わりが書いてあり片方は空）、そのまま出すと画面に
    # 見分けのつかない枠が2つ並ぶ（2026-09-10 id7505 THE ORCHESTRA TOKYO で発生）。
    _seen, _uniq = set(), []
    for t in tickets:
        k = (t['type'], t['date'], t.get('url'))
        if k in _seen:
            continue
        _seen.add(k)
        _uniq.append(t)
    tickets = _uniq

    if not tickets:
        return None, '買える枠なし'
    if not any(p['venue'] for p in perfs):
        # 会場が取れないページ形式が残っている＝空カッコのまま載せない（[[feedback_check_existing_logic]]）
        return None, '会場が取れない(要目視)'

    if len(venues) == 1:
        venue = venues[0]
        datelabel = '%s %s %s' % (jp_date(perfs[0]['date']), prefs[0], venue)
        if last != perfs[0]['date']:
            datelabel = '%s〜%s %s %s' % (jp_date(perfs[0]['date']), jp_date(last), prefs[0], venue)
    else:
        # 全会場を列挙する。[:4]で打ち切ると大規模ツアーの大半の会場が消える
        # （ぴあ側で2026-07-01に同じ事故＝ディズニー・オン・クラシック18県中4会場しか出ず。
        #   楽天ビルダーに同じバグが残っていたのを2026-07-26に発見＝MATSURI 10会場→4会場）
        venue = '全国ツアー（%s）' % '／'.join(venues)
        first = min(p['date'] for p in perfs)
        # 実質単日（最早の公演日==最遅の終了日）なら「9/5〜9/5」の冗長形にしない
        # （ぴあ側は2026-07-15に直したが楽天側に同じ穴が残っていた・2026-07-30 id3229）
        if first == last:
            datelabel = '%s %s' % (jp_date(first), venue)
        else:
            datelabel = '%s〜%s %s' % (jp_date(first), jp_date(last), venue)

    g = rec.get('_genre') or ''
    # 表示テキストは出口で半角カナを全角化する（会場名に混ざる＝id3516で発覚）
    for t in tickets:
        t['type'] = fix_half_kana(t.get('type'))
    e = {
        'id': new_id,
        'artist': fix_half_kana(rec['name']),
        'name': fix_half_kana(rec['name']),
        'date': last,
        'dateLabel': fix_half_kana(datelabel),
        'venue': fix_half_kana(venue),
        'prefecture': prefs[0] if len(prefs) == 1 else '全国',
        'genre': 'new',
        '_genre': g,
        '_srcgenre': 'rakuten',
        'price': None,
        'links': {
            'rakuten': deeplink(rec['url']),
            'lawson': None, 'pia': None, 'eplus': None,
            # 検索語も表示と同じ正規化を通す（ぴあ側で amazon_cd(norm_fw(..)) を忘れて
            # 全角クエリのまま0件になった事故と同型・2026-07-30）
            'amazon': amazon(fix_half_kana(rec['name'])) if g in CD_GENRES else None,
        },
        'tickets': tickets,
        'verified': True,
        'verifiedAt': today,
    }
    return e, ''


def _selftest():
    # 🚨「今日」を固定してから回す。固定しないと**日付が過ぎた時点でテストが落ちて、
    #   ゲートが動かないまま放置される**（2026-09-09 に実際「公演が全部過去」で落ちていた）。
    #   固定日は下の雛形（公演8/29・一般発売7/25開始・二次先行8/1開始）が
    #   「一般発売は開始済み／二次先行はこれから」になる位置に置く。
    global TODAY
    _real_today = TODAY
    TODAY = datetime.date(2026, 7, 28)
    try:
        _selftest_body()
    finally:
        TODAY = _real_today


def _selftest_body():
    rec = {
        'url': 'https://ticket.rakuten.co.jp/music/fes/rtxxxxx/',
        'name': 'テストフェス2026',
        '_genre': 'fes',
        'perfs': [{'date': '2026-08-29', 'end': '', 'time': '12:00', 'pref': '長野県', 'venue': '白馬会場', 'status': '受付中'}],
        'windows': [
            {'type': '一般発売', 'timming': '2026/07/25(土) 10:00 〜 ', 'status': '1', 'start': ''},
            # 🚨終了側にスペースが入る楽天の実形式（2026-07-30の嘘締切バグの回帰ケース）
            {'type': '二次先行', 'timming': '2026/08/01(土) 10:00 〜 2026/08/10 (月) 23:59', 'status': '0', 'start': ''},
            {'type': '終わった枠', 'timming': '2026/05/01(金) 10:00 〜 2026/05/10 (日) 23:59', 'status': '0', 'start': ''},
        ],
    }
    # 終了側スペース有り／無しの両方で締切が取れること（取れないと card_end で埋まって嘘になる）
    assert win_end_iso('2026/06/20(土) 10:00 〜 2026/06/23 (火) 23:59') == ('2026-06-23', '23:59')
    assert win_end_iso('2026/06/20(土) 10:00 〜 2026/06/23(火) 23:59') == ('2026-06-23', '23:59')
    assert win_end_iso('2026/07/25(土) 10:00 〜 ') == (None, None)
    assert win_start_iso('2026/06/20(土) 10:00 〜 2026/06/23 (火) 23:59') == ('2026-06-20', '10:00')
    e, why = build(rec, 9999)
    assert e, why
    assert e['date'] == '2026-08-29' and e['prefecture'] == '長野', e
    assert len(e['tickets']) == 2, e['tickets']          # 終わった枠は落ちる
    t0, t1 = e['tickets']
    # 締切なし＝公演日で締める＋saleEndUnknown・startDateは付けない(開始が過去/今日)
    assert t0['date'] == '2026-08-29' and t0.get('saleEndUnknown') is True, t0
    assert 'startDate' not in t0, t0
    assert '（長野 8/29公演）' in t0['type'], t0['type']
    # 発売前枠は startDate 付き・date は締切
    assert t1['date'] == '2026-08-10' and t1['startDate'] == '2026-08-01', t1
    assert '8/1 10:00発売' in t1['type'], t1['type']
    assert t1['date'] != t1['startDate'], '単日形(隠れ枠)を作ってはいけない'
    assert e['links']['rakuten'].startswith('https://click.linksynergy.com/deeplink?id=z9x6HLNpWco'), e['links']
    assert e['genre'] == 'new' and e['_genre'] == 'fes'
    # R9年表記
    assert r9('2027-01-14') == 'R9年 1/14'

    # 🚨2026-07-30追加＝id3229 北海道芸術花火の型。同じ1会場が「半角カナ」「住所〔〕付き」で
    #   3通り書かれており、素の文字列比較では3会場に見えて「全国ツアー（同じ会場×3）」＋
    #   「9/5〜9/5」の冗長形になっていた。表記ゆれを吸収して1会場・単日形に落ちること。
    rec2 = {
        'url': 'https://ticket.rakuten.co.jp/event/rtmlhk6/',
        'name': 'テスト花火2026', '_genre': 'hanabi',
        'perfs': [
            {'date': '2026-09-05', 'end': '', 'time': '18:00', 'pref': '北海道',
             'venue': 'モエレ沼公園 〔札幌市東区モエレ沼公園1-1〕', 'status': '受付中'},
            {'date': '2026-09-05', 'end': '', 'time': '18:00', 'pref': '北海道',
             'venue': 'ﾓｴﾚ沼公園 〔札幌市東区ﾓｴﾚ沼公園1-1〕', 'status': '受付中'},
            {'date': '2026-09-05', 'end': '', 'time': '18:00', 'pref': '北海道',
             'venue': 'モエレ沼公園', 'status': '受付中'},
        ],
        'windows': [{'type': '一般発売', 'timming': '2026/08/26(水) 12:00 〜 2026/09/05 (土) 15:00',
                     'status': '0', 'start': ''}],
    }
    e2, why2 = build(rec2, 9998)
    assert e2, why2
    assert e2['venue'] == 'モエレ沼公園', e2['venue']          # 1会場・最短表記
    assert '全国ツアー' not in e2['dateLabel'], e2['dateLabel']
    assert '〜' not in e2['dateLabel'], e2['dateLabel']        # 単日は範囲形にしない
    # 半角カナは表示テキストに残らない
    assert not re.search(r'[｡-ﾟ]', e2['venue'] + e2['dateLabel'] + e2['tickets'][0]['type'])
    # 陽性テスト：本当に別会場なら統合しない
    rec3 = dict(rec2)
    rec3['perfs'] = [dict(rec2['perfs'][0]),
                     {'date': '2026-09-06', 'end': '', 'time': '18:00', 'pref': '北海道',
                      'venue': '別の公園', 'status': '受付中'}]
    e3, _ = build(rec3, 9997)
    # （rec3は住所付き表記しか無いので、その表記のまま残る＝勝手に情報を削らない）
    assert e3['venue'] == '全国ツアー（モエレ沼公園 〔札幌市東区モエレ沼公園1-1〕／別の公園）', e3['venue']
    assert '〜' in e3['dateLabel'], e3['dateLabel']            # 日付が違えば範囲形

    # 🚨2026-09-10追加＝id7502 ラフ×ラフの型。販売期間に終わりが書かれていない窓なのに
    #   公演が複数あると、旧コードは max(card_end)＝千秋楽の締切を全公演に付けていた
    #   （11/14の米子公演が「〜R9年 4/3」と出ていた＝嘘）。カードごとに枠を割ること。
    rec4 = {
        'url': 'https://ticket.rakuten.co.jp/music/rtal267/',
        'name': 'テスト巡業2026', '_genre': 'jpop',
        'perfs': [
            {'date': '2026-11-14', 'end': '', 'time': '13:00', 'pref': '鳥取県',
             'venue': '米子AZTiC laughs', 'status': '受付中',
             'sale_start': '2026-08-17 12:00', 'sale_end': '2026-11-14 13:30'},
            {'date': '2026-11-22', 'end': '', 'time': '13:00', 'pref': '静岡県',
             'venue': 'LIVE ROXY SHIZUOKA', 'status': '受付中',
             'sale_start': '2026-08-17 12:00', 'sale_end': '2026-11-22 13:30'},
            {'date': '2027-04-03', 'end': '', 'time': '16:30', 'pref': '大阪府',
             'venue': 'Banana Hall', 'status': '受付中',
             'sale_start': '2026-08-17 12:00', 'sale_end': '2027-04-03 17:00'},
        ],
        'windows': [{'type': '一般発売', 'timming': '2026/08/17(月) 12:00 〜 ',
                     'status': '0', 'start': ''}],
    }
    e4, why4 = build(rec4, 9996)
    assert e4, why4
    ts4 = e4['tickets']
    assert len(ts4) == 3, ts4                                  # 公演ごとに枠が割れる
    assert [t['date'] for t in ts4] == ['2026-11-14', '2026-11-22', '2027-04-03'], ts4
    # 早い公演に千秋楽の締切が付かない＝これが 2026-09-09 の嘘の正体
    assert '4/3' not in ts4[0]['type'], ts4[0]['type']
    # 締切が公演当日にある枠なので開演時刻が入る（[[feedback_same_day_show_time_badge]]の条件②）
    assert '（鳥取 11/14 13:00公演）' in ts4[0]['type'], ts4[0]['type']
    assert '（大阪 R9年 4/3 16:30公演）' in ts4[2]['type'], ts4[2]['type']
    assert all(not t.get('saleEndUnknown') for t in ts4), ts4   # カードに締切がある＝不明ではない
    # 陰性テスト：窓に締切が書いてあるツアーは割らない（同じ枠が増えるだけ）
    rec5 = dict(rec4)
    rec5['windows'] = [{'type': '一般発売',
                        'timming': '2026/08/17(月) 12:00 〜 2026/10/31 (土) 23:59',
                        'status': '0', 'start': ''}]
    e5, _ = build(rec5, 9995)
    assert len(e5['tickets']) == 1, e5['tickets']
    assert e5['tickets'][0]['date'] == '2026-10-31', e5['tickets']
    # 陰性テスト2：1公演しかないページは券種のカードが何枚あっても割らない
    #   （割ると「窓×券種」の総当たりになって存在しない枠が生える。1公演なら元から正しい）
    rec6 = {
        'url': 'https://ticket.rakuten.co.jp/event/rthanabi/',
        'name': 'テスト花火単日2026', '_genre': 'hanabi',
        'perfs': [
            {'date': '2026-10-31', 'end': '', 'time': '18:00', 'pref': '大阪府',
             'venue': '大阪城', 'status': '受付中',
             'sale_start': '2026-07-01 00:00', 'sale_end': '2026-10-17 23:59'},
            {'date': '2026-10-31', 'end': '', 'time': '18:00', 'pref': '大阪府',
             'venue': '大阪城', 'status': '受付中', 'ticket_name': '一般席',
             'sale_start': '2026-10-18 00:00', 'sale_end': '2026-10-31 16:00'},
        ],
        'windows': [{'type': '早割', 'timming': '2026/07/01(水) 00:00 〜 ',
                     'status': '0', 'start': ''}],
    }
    e6, _ = build(rec6, 9994)
    assert len(e6['tickets']) == 1, e6['tickets']
    assert e6['tickets'][0]['date'] == '2026-10-31', e6['tickets']
    # 陰性テスト3：同日同会場の昼夜でも**締切が同じなら1枠**（分けても同じ表記が2つ並ぶだけ）
    #   実例＝id3224 MATSURI の 13:30/17:30 は2回とも前日23:59締切
    rec7 = {
        'url': 'https://ticket.rakuten.co.jp/music/rtax088/',
        'name': 'テスト昼夜2026', '_genre': 'jpop',
        'perfs': [
            {'date': '2026-09-19', 'end': '', 'time': '13:30', 'pref': '山梨県',
             'venue': 'YCC県民文化ホール 小ホール', 'status': '受付中',
             'sale_start': '2026-07-02 18:00', 'sale_end': '2026-09-18 23:59'},
            {'date': '2026-09-19', 'end': '', 'time': '17:30', 'pref': '山梨県',
             'venue': 'YCC県民文化ホール 小ホール', 'status': '受付中',
             'sale_start': '2026-07-02 18:00', 'sale_end': '2026-09-18 23:59'},
            {'date': '2026-12-06', 'end': '', 'time': '13:30', 'pref': '東京都',
             'venue': 'Zepp DiverCity (TOKYO)', 'status': '受付中',
             'sale_start': '2026-07-02 18:00', 'sale_end': '2026-12-05 23:59'},
        ],
        'windows': [{'type': '楽天チケット先着先行', 'timming': '2026/07/02(木) 18:00 〜 ',
                     'status': '0', 'start': ''}],
    }
    e7, _ = build(rec7, 9993)
    ts7 = e7['tickets']
    assert len(ts7) == 2, ts7                                  # 山梨の昼夜は1枠
    assert '（山梨 9/19公演）' in ts7[0]['type'], ts7[0]['type']   # 締切が同じ＝時刻は入れない
    assert ts7[0]['date'] == '2026-09-18' and ts7[1]['date'] == '2026-12-05', ts7
    # 陰性テスト4：公演日が違っても**締切が同じなら1枠**（枠の単位は締切）
    #   実例＝id1 さだまさし 11/19と11/20はどちらも11/11締切
    rec8 = {
        'url': 'https://ticket.rakuten.co.jp/music/rtkb710/',
        'name': 'テスト同一締切2026', '_genre': 'jpop',
        'perfs': [
            {'date': '2026-11-19', 'end': '', 'time': '18:30', 'pref': '東京都',
             'venue': 'テストホール', 'status': '受付中',
             'sale_start': '2026-08-01 10:00', 'sale_end': '2026-11-11 23:59'},
            {'date': '2026-11-20', 'end': '', 'time': '18:30', 'pref': '東京都',
             'venue': 'テストホール', 'status': '受付中',
             'sale_start': '2026-08-01 10:00', 'sale_end': '2026-11-11 23:59'},
        ],
        'windows': [{'type': '一般発売', 'timming': '2026/08/01(土) 10:00 〜 ',
                     'status': '0', 'start': ''}],
    }
    e8, _ = build(rec8, 9992)
    assert len(e8['tickets']) == 1, e8['tickets']
    assert '（東京 11/19〜11/20公演）' in e8['tickets'][0]['type'], e8['tickets'][0]['type']
    assert e8['tickets'][0]['date'] == '2026-11-11', e8['tickets']

    print('selftest OK: 締切不明→公演日+saleEndUnknown / 発売前startDate / 終了枠除去 / deeplink / R9年'
          ' / 会場の表記ゆれ統合 / 単日形 / 半角カナ全角化 / 締切なし窓は公演ごとに枠を割る')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src', nargs='?', default='tmp/rakuten_fresh.json')
    ap.add_argument('--start-id', type=int, default=0)
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args()
    if args.selftest:
        _selftest()
        return 0

    import rakuten_harvest as RH
    rows = json.load(open(args.src, encoding='utf-8'))
    groups = {}
    for r in rows:
        groups.setdefault(RH.norm_name(r['name']), []).append(r)
    recs = list(groups.values())
    if len(recs) < len(rows):
        sys.stderr.write('ツアー統合: %d ページ → %d エントリ\n' % (len(rows), len(recs)))
    nid = args.start_id
    if not nid:
        h = open('index.html', encoding='utf-8').read()
        m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
        nid = max(e['id'] for e in json.loads(m.group(2))) + 1

    out, skip = [], []
    for g in recs:
        e, why = build(g, nid)
        nm = g[0]['name']
        if e:
            out.append(e)
            nid += 1
            sys.stderr.write('  OK   %s%s\n' % (nm[:40], ' (%dページ統合)' % len(g) if len(g) > 1 else ''))
        else:
            skip.append((nm, why))
            sys.stderr.write('  skip %s (%s)\n' % (nm[:40], why))
    print(json.dumps(out, ensure_ascii=False, indent=1))
    sys.stderr.write('\n構築 %d件 / skip %d件\n' % (len(out), len(skip)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
