# -*- coding: utf-8 -*-
"""B.LEAGUE チケット由来の枠の番人＝**試合ページ（HTML）を読み直して、組み立てとは別の書き方で枠を作り、登録と全件突合**する。

  python tools/gate_bleague_slots.py                          … index.html の B.LEAGUE 枠を全部照合
  python tools/gate_bleague_slots.py --ids 1,2                … id 指定
  python tools/gate_bleague_slots.py --built tmp/x1120/newv/bleague/built.json   … 投入前の組み上がりを照合
  python tools/gate_bleague_slots.py --selftest

終了コード 0＝全一致 / 2＝食い違い・読めない あり（投入・push の前に 0 を確かめる）
報告の形は「🚨 id=<番号> 名前」（ほかの売り場の番人と同じ）。

## 組み立て（build_bleague_entries）と**別に**作る
- 読む所が違う＝組み立ては JSON の API（/tenants/…/events/…）、番人は**試合ページの HTML**
  （`self.__next_f.push` の中の react-query の下ごしらえ `getEventSummary`・`getEvent`）。
- UTC→日本時間・状態の判定・締切を試合日で締める・バッジの文字を**ここで書き直している**（組み立ての関数は使わない）。
- 残り枚数は HTML に無い＝ここだけ API（general-sales-package-stocks）を読む（売り場にこれしか無い）。
- チーム名の正式名は HTML に無い＝クラブの API（/clubs/<コード>）の 略称→正式名 で読み戻す。
- バッジの文字を**読み戻して**（受付名・県・試合日・開始・発売日時・締切・売り切れ・販売終了）比べる。
- カードの日付＝試合日、会場名、県、名前の対戦カード・会場も見る。
"""
import argparse
import datetime
import io
import json
import re
import sys
import time
import urllib.error
import urllib.request

if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
REPORT = 'tmp/gate_bleague_report.txt'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
URL_RE = re.compile(r'ticket\.bleague\.jp/clubs/([a-z0-9]+)/events/([A-Za-z0-9]+)')
PREFS = ('北海道 青森 岩手 宮城 秋田 山形 福島 茨城 栃木 群馬 埼玉 千葉 東京 神奈川 新潟 富山 石川 福井 山梨 長野 '
         '岐阜 静岡 愛知 三重 滋賀 京都 大阪 兵庫 奈良 和歌山 鳥取 島根 岡山 広島 山口 徳島 香川 愛媛 高知 福岡 佐賀 '
         '長崎 熊本 大分 宮崎 鹿児島 沖縄').split()
_LAST = [0.0]


def get(url, sleep, as_json=False):
    w = sleep - (time.time() - _LAST[0])
    if w > 0:
        time.sleep(w)
    _LAST[0] = time.time()
    r = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Language': 'ja'}), timeout=90)
    b = r.read().decode('utf-8', 'replace')
    return json.loads(b) if as_json else b


def page_queries(html):
    """HTML → {queryKey の JSON 文字列: data}（RSC の行を1行ずつ JSON にして queries を拾う）"""
    chunks = []
    for m in re.finditer(r'self\.__next_f\.push\((\[.*?\])\)</script>', html, re.S):
        try:
            a = json.loads(m.group(1))
        except ValueError:
            continue
        if len(a) > 1 and isinstance(a[1], str):
            chunks.append(a[1])
    if not chunks:
        raise ValueError('ページに RSC が無い（確認画面・形が変わった疑い）')
    rsc = ''.join(chunks)
    out = {}
    stack = []
    for line in rsc.split('\n'):
        m = re.match(r'^[0-9a-f]+:([\[{].*)$', line)
        if not m:
            continue
        try:
            stack.append(json.loads(m.group(1)))
        except ValueError:
            continue
    while stack:
        o = stack.pop()
        if isinstance(o, dict):
            if 'queryKey' in o and isinstance(o.get('state'), dict):
                out[json.dumps(o['queryKey'], ensure_ascii=False)] = o['state'].get('data')
            stack.extend(o.values())
        elif isinstance(o, list):
            stack.extend(o)
    return out


def jst(v):
    """'$D2026-12-19T08:05:00.000Z' / '2026-12-19T08:05:00Z' → 日本時間の naive datetime（組み立てとは別の書き方）"""
    if not isinstance(v, str):
        return None
    m = re.search(r'(\d{4})-(\d\d)-(\d\d)T(\d\d):(\d\d)', v)
    if not m:
        return None
    return datetime.datetime(*map(int, m.groups())) + datetime.timedelta(hours=9)


def nocond(x):
    c = x.get('condition')
    return c is None or c == '$undefined'


def mdd(dt_or_iso):
    if isinstance(dt_or_iso, str):
        return '%d/%d' % (int(dt_or_iso[5:7]), int(dt_or_iso[8:10]))
    return '%d/%d' % (dt_or_iso.month, dt_or_iso.day)


def expected(summ, evd, stock, now):
    """ページの下ごしらえ → 期待する枠 dict（無ければ None と理由）。"""
    if not summ.get('canNavigateToDetail'):
        return None, '準備中（試合ページが開かない）'
    st = summ.get('salesStatus')
    if st in ('SUSPENDED', 'EVENT_CANCELED'):
        return None, '準備中・中止（%s）' % st
    if st not in ('BEFORE_SALE', 'ON_SALE', 'SALE_ENDED'):
        return None, '読めない状態 %s' % st
    day = summ.get('eventStartDate') or ''
    tm = summ.get('eventStartTime')
    tm = '' if tm in (None, '$undefined') else '%d:%s' % (int(tm.split(':')[0]), tm.split(':')[1])
    end = jst(summ.get('saleEndAt'))
    if end is None or end.date().isoformat() > day:
        end_date, end_txt = day, mdd(day)
    else:
        end_date, end_txt = end.date().isoformat(), '%s %d:%02d' % (mdd(end), end.hour, end.minute)
    w = {'show': mdd(day), 'year': int(day[:4]), 'time': tm or None, 'sale': None, 'start_date': None,
         'end': end_txt, 'end_date': end_date, 'soldout': False, 'ended': False}
    if st == 'SALE_ENDED' or (end is not None and end <= now):
        w['soldout'] = w['ended'] = True
        return w, ''
    starts = [jst(x.get('saleStartAt')) for x in (evd.get('salesSchedules') or []) if nocond(x)]
    if not starts or None in starts:
        return None, '一般の受付が無い・読めない'
    if any(s <= now for s in starts):
        if not stock or stock.get('remaining') is None:
            return None, '残り枚数が読めない'
        if stock['remaining'] == 0:
            if not stock.get('total'):
                return None, '入荷待ち'
            w['soldout'] = True
        return w, ''
    s0 = min(starts)
    w['sale'] = '%s %d:%02d' % (mdd(s0), s0.hour, s0.minute)
    w['start_date'] = s0.date().isoformat()
    return w, ''


BADGE_RE = re.compile(r'^一般販売（(?:(?P<pref>(?!R\d+年)[^\s（）]+) )?(?:R(?P<r>\d+)年 )?(?P<show>\d{1,2}/\d{1,2})'
                      r'(?: (?P<time>\d{1,2}:\d{2}))?公演）(?:(?P<sale>\d{1,2}/\d{1,2} \d{1,2}:\d{2})発売)?'
                      r'〜(?P<end>\d{1,2}/\d{1,2}(?: \d{1,2}:\d{2})?)$')


def badge_key(t):
    m = BADGE_RE.match(t.get('type') or '')
    if not m:
        return None
    return (m.group('show'), int(m.group('r')) + 2018 if m.group('r') else None, m.group('time'), m.group('sale'),
            m.group('end'), bool(t.get('soldout')), bool(t.get('saleEnded')), t.get('date'),
            t.get('startDate') if m.group('sale') else None)


def window_key(w, this_year):
    return (w['show'], w['year'] if w['year'] > this_year else None, w['time'], w['sale'], w['end'],
            w['soldout'], w['ended'], w['end_date'], w['start_date'])


def check_entry(e, html, stock, clubnames, today, now):
    ng = []
    q = page_queries(html)
    summ = next((v for k, v in q.items() if k.startswith('["getEventSummary"')), None)
    evd = next((v for k, v in q.items() if k.startswith('["getEvent",')), None)
    if not isinstance(summ, dict) or not isinstance(evd, dict):
        raise ValueError('getEventSummary／getEvent が無い（公開が終わった疑い）')
    reg = [t for t in e.get('tickets') or [] if 'ticket.bleague.jp' in (t.get('url') or '')]
    rk = []
    for t in reg:
        k = badge_key(t)
        if k is None:
            ng.append('バッジの文字が読めない: %s' % t.get('type'))
            continue
        rk.append(k)
        m = BADGE_RE.match(t['type'])
        if m.group('pref') and m.group('pref') not in PREFS:
            ng.append('バッジの県が県名でない: %s' % t['type'])
        if (m.group('pref') or '') != (e.get('prefecture') or ''):
            ng.append('バッジの県「%s」≠ カードの県「%s」' % (m.group('pref'), e.get('prefecture')))
    w, why = expected(summ, evd, stock, now)
    pk = [window_key(w, int(today[:4]))] if w else []
    for k in sorted(set(rk) - set(pk), key=str):
        ng.append('登録にだけある: %s' % (k,) + ('（ページは %s）' % why if why else ''))
    for k in sorted(set(pk) - set(rk), key=str):
        ng.append('試合ページにだけある: %s' % (k,))
    day = summ.get('eventStartDate')
    if day and e.get('date') != day:
        ng.append('カードの日付 %s ≠ 試合日 %s' % (e.get('date'), day))
    ven = evd.get('venue') or {}
    vn = (ven.get('displayName') or '').strip()
    if vn and vn != (e.get('venue') or ''):
        ng.append('会場が違う: 登録「%s」／ページ「%s」' % (e.get('venue'), vn))
    pf = ven.get('prefecture') or (summ.get('venueSummary') or {}).get('prefecture') or ''
    pf2 = pf if pf == '北海道' else pf[:-1] if pf[-1:] in '都府県' else pf
    if pf2 != (e.get('prefecture') or ''):
        ng.append('県が違う: 登録「%s」／ページ「%s」' % (e.get('prefecture'), pf))
    addr = ven.get('address') or ''
    if pf and addr and not addr.startswith(pf):
        ng.append('ℹ️住所の頭が県と違う（売り場の表記）: %s / %s' % (pf, addr[:12]))
    gsd = evd.get('genreSpecificData') or {}
    if evd.get('displayFormat') == 'MATCH_EVENT':
        ha = [((gsd.get(s) or {}).get('abbreviatedName') or '') for s in ('homeTeam', 'awayTeam')]
        full = [clubnames.get(a, a) for a in ha]
        want = '%s／%s' % tuple(full)
        if all(a in clubnames for a in ha) and e.get('artist') != want:
            ng.append('対戦カードが違う: 登録「%s」／ページ「%s」' % (e.get('artist'), want))
        if not (e.get('name') or '').startswith('%s対%s（%s）' % (full[0], full[1], vn)) and all(a in clubnames for a in ha):
            ng.append('カード名の頭が「ホーム対アウェイ（会場）」でない: %s' % e.get('name'))
        grp = (evd.get('eventGroupSummary') or {}).get('name') or ''
        if grp and not (e.get('name') or '').endswith(grp):
            ng.append('大会名がカード名に無い: %s' % grp)
    ng = [x for x in ng if not x.startswith('ℹ️')]
    return ng


def load_clubnames(sleep, codes):
    names = {}
    for c in codes:
        try:
            d = get('https://api.ticket.bleague.jp/clubs/%s' % c, sleep, as_json=True)
            if d.get('abbreviatedName') and d.get('name'):
                names[d['abbreviatedName']] = d['name']
        except Exception:
            pass
    return names


def _selftest():
    now = datetime.datetime(2026, 11, 20, 12, 0)
    summ = {'canNavigateToDetail': True, 'salesStatus': 'ON_SALE', 'eventStartDate': '2026-12-19',
            'eventStartTime': '15:05', 'saleEndAt': '$D2026-12-19T08:05:00.000Z'}
    evd = {'displayFormat': 'MATCH_EVENT', 'salesSchedules': [{'condition': {'x': 1}, 'saleStartAt': '$D2026-10-26T09:00:00.000Z'},
                                                              {'saleStartAt': '$D2026-10-30T11:00:00.000Z'}],
           'venue': {'displayName': '北海きたえーる', 'prefecture': '北海道'},
           'eventGroupSummary': {'name': 'B.LEAGUE リーグ戦'},
           'genreSpecificData': {'homeTeam': {'abbreviatedName': '北海道'}, 'awayTeam': {'abbreviatedName': '川崎'}}}
    clubs = {'北海道': 'レバンガ北海道', '川崎': '川崎ブレイブサンダース'}

    def page(s, d):
        rsc = '1:' + json.dumps({'state': {'queries': [
            {'queryKey': ['getEventSummary', 'E'], 'state': {'data': s}},
            {'queryKey': ['getEvent', 'lh', 'E'], 'state': {'data': d}}]}}, ensure_ascii=False) + '\n'
        return '<script>self.__next_f.push(%s)</script>' % json.dumps([1, rsc], ensure_ascii=False)
    good = {'name': 'レバンガ北海道対川崎ブレイブサンダース（北海きたえーる） B.LEAGUE リーグ戦', 'artist': 'レバンガ北海道／川崎ブレイブサンダース',
            'date': '2026-12-19', 'venue': '北海きたえーる', 'prefecture': '北海道',
            'tickets': [{'type': '一般販売（北海道 12/19 15:05公演）〜12/19 17:05', 'date': '2026-12-19',
                         'url': 'https://ticket.bleague.jp/clubs/lh/events/E'}]}
    st = {'remaining': 3, 'total': 10}
    assert check_entry(good, page(summ, evd), st, clubs, '2026-11-20', now) == []
    # 鳴る：売り切れの印・締切・カードの日付・会場・県・対戦カード・準備中
    assert check_entry(good, page(summ, evd), {'remaining': 0, 'total': 10}, clubs, '2026-11-20', now)
    bad = json.loads(json.dumps(good))
    bad['tickets'][0]['type'] = '一般販売（北海道 12/19 15:05公演）〜12/19 15:05'
    assert check_entry(bad, page(summ, evd), st, clubs, '2026-11-20', now)
    assert check_entry(dict(good, date='2026-12-20'), page(summ, evd), st, clubs, '2026-11-20', now)
    assert check_entry(dict(good, venue='X'), page(summ, evd), st, clubs, '2026-11-20', now)
    assert check_entry(dict(good, prefecture='東京'), page(summ, evd), st, clubs, '2026-11-20', now)
    assert check_entry(dict(good, artist='A／B'), page(summ, evd), st, clubs, '2026-11-20', now)
    assert check_entry(good, page(dict(summ, salesStatus='SUSPENDED'), evd), st, clubs, '2026-11-20', now)
    # 発売前（2027年＝R9年）
    s2 = dict(summ, salesStatus='BEFORE_SALE', eventStartDate='2027-01-23', eventStartTime='13:35',
              saleEndAt='$D2027-01-23T06:35:00.000Z')
    e2 = dict(good, date='2027-01-23', tickets=[{'type': '一般販売（北海道 R9年 1/23 13:35公演）12/4 20:00発売〜1/23 15:35',
                                                 'date': '2027-01-23', 'startDate': '2026-12-04',
                                                 'url': 'https://ticket.bleague.jp/clubs/lh/events/E'}])
    evd2 = dict(evd, salesSchedules=[{'saleStartAt': '$D2026-12-04T11:00:00.000Z'}])
    assert check_entry(e2, page(s2, evd2), st, clubs, '2026-11-20', now) == []
    e3 = json.loads(json.dumps(e2))
    e3['tickets'][0]['startDate'] = '2026-12-05'
    assert check_entry(e3, page(s2, evd2), st, clubs, '2026-11-20', now)
    try:
        page_queries('<html>確認</html>')
        raise AssertionError('RSC の無いページを読まない')
    except ValueError:
        pass
    print('selftest OK: HTML の RSC から別の書き方で枠を作る/売り切れ・締切・発売日・カードの日付・会場・県・対戦カード・準備中で鳴る')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ids', default='')
    ap.add_argument('--built', default='')
    ap.add_argument('--today', default=(datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) + datetime.timedelta(hours=9)).date().isoformat())
    ap.add_argument('--sleep', type=float, default=3.0)
    ap.add_argument('--report', default=REPORT)
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        _selftest()
        sys.exit(0)
    if a.built:
        ents = json.load(io.open(a.built, encoding='utf-8'))['entries']
        targets = [(e, i) for i, e in enumerate(ents)]
    else:
        h = io.open('index.html', encoding='utf-8', newline='').read()
        ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))
        want = {int(x) for x in re.findall(r'\d+', a.ids)} if a.ids else None
        targets = [(e, e['id']) for e in ev if 'ticket.bleague.jp/clubs/' in json.dumps(e.get('links') or {}) + json.dumps(e.get('tickets') or [])
                   and (not want or e['id'] in want)]
    top = get('https://ticket.bleague.jp/', a.sleep)
    codes = list(dict.fromkeys(re.findall(r'href="/clubs/([a-z0-9]+)/events"', top)))
    clubnames = load_clubnames(a.sleep, codes)
    ok, ng, err = 0, [], []
    for e, key in targets:
        urls = sorted({m for t in (e.get('tickets') or []) + [{'url': (e.get('links') or {}).get('bleague')}]
                       for m in URL_RE.findall(t.get('url') or '')})
        if len(urls) != 1:
            ng.append((e, key, ['試合ページが %d 個（1試合1カードのはず）: %s' % (len(urls), urls)]))
            continue
        host, eid = urls[0]
        try:
            html = get('https://ticket.bleague.jp/clubs/%s/events/%s' % (host, eid), a.sleep)
            stock = None
            try:
                stock = get('https://api.ticket.bleague.jp/tenants/%s/events/%s/general-sales-package-stocks' % (host, eid),
                            a.sleep, as_json=True)
            except urllib.error.HTTPError:
                pass
            now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) + datetime.timedelta(hours=9)
            msgs = check_entry(e, html, stock, clubnames, a.today, now)
        except Exception as ex:
            err.append((e, key, eid, str(ex)[:80]))
            continue
        if msgs:
            ng.append((e, key, msgs))
        else:
            ok += 1
    rep = io.open(a.report, 'w', encoding='utf-8')
    rep.write('=== gate_bleague_slots (today=%s) %s 対象%d件・クラブ名 %d ===\n'
              % (a.today, a.built or 'index.html', len(targets), len(clubnames)))
    for e, key, msgs in ng:
        rep.write('\n🚨 id=%s %s\n    %s\n' % (key, (e.get('name') or '')[:50], (e.get('links') or {}).get('bleague')))
        for m in msgs:
            rep.write('    %s\n' % m)
    for e, key, u, why in err:
        rep.write('❌ id=%s events/%s 読めなかった: %s\n' % (key, u, why))
    rep.write('\n=== 集計: 一致 %d / 🚨食い違い %d / ❌読めなかった %d ===\n' % (ok, len(ng), len(err)))
    rep.close()
    sys.stderr.write('gate_bleague_slots: match=%d ng=%d fetcherr=%d -> %s\n' % (ok, len(ng), len(err), a.report))
    sys.exit(2 if (ng or err) else 0)


if __name__ == '__main__':
    main()
