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
import urllib.parse

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, 'tools')

TODAY = datetime.date.today()
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


def win_end_iso(timming):
    ds = re.findall(r'(20\d{2})/(\d{2})/(\d{2})\([^)]*\)\s*(\d{1,2}:\d{2})', timming or '')
    if len(ds) < 2:
        return None, None
    return '%s-%s-%s' % ds[1][:3], ds[1][3]


def win_start_iso(timming):
    ds = re.findall(r'(20\d{2})/(\d{2})/(\d{2})\([^)]*\)\s*(\d{1,2}:\d{2})', timming or '')
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
    venues = []
    for p in perfs:
        if p['venue'] and p['venue'] not in venues:
            venues.append(p['venue'])

    tickets = []
    for r in recs:
        rp = [p for p in perfs if p['_url'] == r['url']]
        if not rp:
            continue
        span = perf_span(rp)
        pref_txt = '・'.join(dict.fromkeys(pref_short(p['pref']) for p in rp if p['pref']))
        last_r = max((p.get('end') or p['date']) for p in rp)
        # カード(data-date)が持つ販売終了日時＝この公演の実際の締切。枠に締切が無い時の正になる。
        card_end = max((p.get('sale_end') or '') for p in rp)
        for w in r['windows']:
            sd, st = win_start_iso(w['timming'])
            ed, et = win_end_iso(w['timming'])
            if not sd:
                continue
            if not ed and card_end:
                ed, et = card_end[:10], card_end[11:16]
            if ed and ed < today:
                continue                               # 締切済み＝載せない
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
        datelabel = '%s〜%s %s' % (jp_date(min(p['date'] for p in perfs)), jp_date(last), venue)

    g = rec.get('_genre') or ''
    e = {
        'id': new_id,
        'artist': rec['name'],
        'name': rec['name'],
        'date': last,
        'dateLabel': datelabel,
        'venue': venue,
        'prefecture': prefs[0] if len(prefs) == 1 else '全国',
        'genre': 'new',
        '_genre': g,
        '_srcgenre': 'rakuten',
        'price': None,
        'links': {
            'rakuten': deeplink(rec['url']),
            'lawson': None, 'pia': None, 'eplus': None,
            'amazon': amazon(rec['name']) if g in CD_GENRES else None,
        },
        'tickets': tickets,
        'verified': True,
        'verifiedAt': today,
    }
    return e, ''


def _selftest():
    rec = {
        'url': 'https://ticket.rakuten.co.jp/music/fes/rtxxxxx/',
        'name': 'テストフェス2026',
        '_genre': 'fes',
        'perfs': [{'date': '2026-08-29', 'end': '', 'time': '12:00', 'pref': '長野県', 'venue': '白馬会場', 'status': '受付中'}],
        'windows': [
            {'type': '一般発売', 'timming': '2026/07/25(土) 10:00 〜 ', 'status': '1', 'start': ''},
            {'type': '二次先行', 'timming': '2026/08/01(土) 10:00 〜 2026/08/10(月) 23:59', 'status': '0', 'start': ''},
            {'type': '終わった枠', 'timming': '2026/05/01(金) 10:00 〜 2026/05/10(日) 23:59', 'status': '0', 'start': ''},
        ],
    }
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
    print('selftest OK: 締切不明→公演日+saleEndUnknown / 発売前startDate / 終了枠除去 / deeplink / R9年')


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
