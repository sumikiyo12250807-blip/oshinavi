# -*- coding: utf-8 -*-
"""チケットボード由来の枠の番人＝**受付ページの JSON を読み直して、組み立てとは別の向き・別の判定で枠を作り、登録と全件突合**する。

  python tools/gate_tickebo_slots.py                          … index.html のチケットボード枠を全部照合
  python tools/gate_tickebo_slots.py --ids 1,2                … id 指定
  python tools/gate_tickebo_slots.py --built tmp/x1120/newv/tickebo/built.json   … 投入前の組み上がりを照合
  python tools/gate_tickebo_slots.py --selftest

終了コード 0＝全一致 / 2＝食い違い・読めない あり。報告の形は「🚨 id=<番号> 名前」。

## 組み立て（build_tickebo_entries）と**別に**作る
⚠️チケットボードは公演の中身を出す所が `/web/api/evt/sales-list` の JSON **1つだけ**（公演ページの HTML は Vue の型だけで中身が無い）。
＝読む所は同じ。代わりに**読み方と判定を変える**：
- 組み立ては「公演ごとに受付を回す」。番人は「**受付ごとに公演を回す**」（画面の「販売種別から探す」タブの向き）。
- 組み立ては売り場の状態札（acceptanceStatus before/during/after）を使う。番人は**受付期間の時刻と今の時刻から自分で状態を決め**、
  売り場の札と合わない時は「分からない」として鳴らす（札がずれていれば組み立ても間違える）。
- 県は JIS 番号を**自分の表**で引き直す。日時・締切を公演日で締める・バッジの文字を**ここで書き直す**（組み立ての関数は使わない）。
- バッジの文字を読み戻して（受付名・県・公演日・開演・発売日時・締切・売り切れ）比べる。カードの日付・会場・県・公演名も見る。
"""
import argparse
import datetime
import io
import json
import re
import sys
import time
import unicodedata
import urllib.request

if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
REPORT = 'tmp/gate_tickebo_report.txt'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
URL_RE = re.compile(r'ticket\.tickebo\.jp/show/event\.html\?info=(\d+)')
JIS = {1: '北海道', 2: '青森', 3: '岩手', 4: '宮城', 5: '秋田', 6: '山形', 7: '福島', 8: '茨城', 9: '栃木', 10: '群馬',
       11: '埼玉', 12: '千葉', 13: '東京', 14: '神奈川', 15: '新潟', 16: '富山', 17: '石川', 18: '福井', 19: '山梨',
       20: '長野', 21: '岐阜', 22: '静岡', 23: '愛知', 24: '三重', 25: '滋賀', 26: '京都', 27: '大阪', 28: '兵庫',
       29: '奈良', 30: '和歌山', 31: '鳥取', 32: '島根', 33: '岡山', 34: '広島', 35: '山口', 36: '徳島', 37: '香川',
       38: '愛媛', 39: '高知', 40: '福岡', 41: '佐賀', 42: '長崎', 43: '熊本', 44: '大分', 45: '宮崎', 46: '鹿児島', 47: '沖縄'}
_LAST = [0.0]


def get_json(no, sleep):
    w = sleep - (time.time() - _LAST[0])
    if w > 0:
        time.sleep(w)
    _LAST[0] = time.time()
    r = urllib.request.urlopen(urllib.request.Request(
        'https://ticket.tickebo.jp/web/api/evt/sales-list?acceptanceNo=%s' % no,
        headers={'User-Agent': UA, 'Accept-Language': 'ja', 'Accept': 'application/json'}), timeout=60)
    b = r.read().decode('utf-8', 'replace')
    if b.lstrip().startswith('<'):
        raise RuntimeError('JSON でなく HTML（確認画面・閉じた疑い）')
    return json.loads(b)


def dt(s):
    if not s:
        return None
    try:
        return datetime.datetime.strptime(s[:16], '%Y-%m-%dT%H:%M')
    except ValueError:
        return None


def slash(d):
    return '%d/%d' % (d.month, d.day) if isinstance(d, datetime.date) else '%d/%d' % (int(d[5:7]), int(d[8:10]))


def expected(data, today, now):
    """受付ごとに公演を回す → 期待する枠の集合と、分からない受付の説明"""
    evs = [e for e in data.get('events') or [] if e.get('openType') not in ('02', '04', '05')]   # 中止・延期・公演終了
    def days(e):
        return [x for x in ([e.get('eventOn')] if e.get('eventOn') else [e.get('holdStartOn'), e.get('holdEndOn')]) if x]
    evs = [e for e in evs if days(e) and max(days(e)) >= today]
    same_day = {}
    for e in evs:
        if len(days(e)) == 1:
            same_day[days(e)[0]] = same_day.get(days(e)[0], 0) + 1
    out, unknown = [], []
    for s in data.get('sales') or []:
        if s.get('tradeFlg'):
            continue
        no = s.get('salesNo')
        for e in evs:
            if no not in (e.get('salesNos') or []):
                continue
            a = next((x for x in e.get('acceptanceStatuses') or [] if x.get('salesNo') == no), {})
            st, en = dt(a.get('salesStartAt') or s.get('salesStartAt')), dt(a.get('salesEndAt') or s.get('salesEndAt'))
            # 自分で決める状態
            if en is not None and en < now:
                mine = 'after'
            elif st is not None and st > now:
                mine = 'before'
            elif st is not None:
                mine = 'during'
            else:
                mine = None
            theirs = a.get('acceptanceStatus')
            if mine != theirs:
                unknown.append('%s（%s）売り場の札 %s ≠ 時刻から %s' % (s.get('salesNmWeb'), days(e)[0], theirs, mine))
                continue
            if mine == 'after':
                continue
            ds = days(e)
            last = ds[-1]
            if en is None or en.date().isoformat() > last:
                end_date, end_txt = last, slash(last)
            else:
                end_date, end_txt = en.date().isoformat(), '%s %d:%02d' % (slash(en), en.hour, en.minute)
            tm = re.match(r'(\d{1,2}):(\d\d)', e.get('openEventTm') or '')
            show = (ds[0], ds[-1] if len(ds) > 1 else None,
                    '%d:%s' % (int(tm.group(1)), tm.group(2)) if tm and len(ds) == 1 and same_day.get(ds[0], 0) > 1 else None)
            try:
                pref = JIS.get(int(e.get('prefectureCd')), '')
            except (TypeError, ValueError):
                pref = ''
            sale = start_date = None
            sold = False
            if mine == 'before':
                sale, start_date = '%s %d:%02d' % (slash(st), st.hour, st.minute), st.date().isoformat()
            else:
                rem = next((x.get('remainNum') for x in e.get('salesRemainNums') or [] if x.get('salesNo') == no), None)
                if s.get('salesType') != '01':
                    if rem == 0:
                        sold = True
                    elif not (isinstance(rem, int) and rem > 0):
                        unknown.append('%s（%s）残り枚数が読めない %r' % (s.get('salesNmWeb'), ds[0], rem))
                        continue
            out.append({'name': s.get('salesNmWeb') or '', 'pref': pref, 'show': show, 'sale': sale, 'end': end_txt,
                        'end_date': end_date, 'start_date': start_date, 'soldout': sold,
                        'venue': re.sub(r'\s+', ' ', e.get('venueNm') or '').strip()})
    return out, unknown, evs, days


BADGE_RE = re.compile(r'^(?P<name>.*)（(?:(?P<pref>(?!R\d+年)[^\s（）]+) )?(?:R(?P<r>\d+)年 )?(?P<d1>\d{1,2}/\d{1,2})'
                      r'(?:〜(?:R(?P<r2>\d+)年 )?(?P<d2>\d{1,2}/\d{1,2}))?(?: (?P<time>\d{1,2}:\d{2}))?公演）'
                      r'(?:(?P<sale>\d{1,2}/\d{1,2} \d{1,2}:\d{2})発売)?〜(?P<end>\d{1,2}/\d{1,2}(?: \d{1,2}:\d{2})?)$')


def wname(s):
    """受付名をバッジの書き方に（別に書く：NFKC・半角カッコ等を全角・後ろの値段を落とす）"""
    s = re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', s or '')).strip()
    s = re.sub(r'\s*[\d,]+\s*円\s*$', '', s)
    for a, b in (('(', '（'), (')', '）'), ('[', '［'), (']', '］'), ('<', '＜'), ('>', '＞')):
        s = s.replace(a, b)
    return s


def key_of_window(w, ty):
    d1, d2, tmv = w['show']
    def md(iso, with_era):
        y = int(iso[:4])
        return ('R%d年 ' % (y - 2018) if with_era and y > ty else '') + slash(iso)
    show = md(d1, True) + ('〜' + md(d2, d2[:4] != d1[:4]) if d2 else '')
    return (wname(w['name']), w['pref'], show, tmv, w['sale'], w['end'], w['soldout'], w['end_date'], w['start_date'])


def key_of_badge(t):
    m = BADGE_RE.match(t.get('type') or '')
    if not m:
        return None
    show = ('R%s年 ' % m.group('r') if m.group('r') else '') + m.group('d1')
    if m.group('d2'):
        show += '〜' + ('R%s年 ' % m.group('r2') if m.group('r2') else '') + m.group('d2')
    return (m.group('name'), m.group('pref') or '', show, m.group('time'), m.group('sale'), m.group('end'),
            bool(t.get('soldout')), t.get('date'), t.get('startDate') if m.group('sale') else None)


def check_entry(e, data, today, now):
    ng = []
    ty = int(today[:4])
    wins, unknown, evs, days = expected(data, today, now)
    pk = [key_of_window(w, ty) for w in wins]
    rk = []
    for t in e.get('tickets') or []:
        if 'tickebo.jp' not in (t.get('url') or ''):
            continue
        k = key_of_badge(t)
        if k is None:
            ng.append('バッジの文字が読めない: %s' % t.get('type'))
        else:
            rk.append(k)
    left = list(pk)
    for r in rk:
        hit = next((x for x in left if (x[0] == r[0] or (len(r[0]) >= 20 and x[0].startswith(r[0]))) and x[1:] == r[1:]), None)
        if hit:
            left.remove(hit)
            if len(r[0]) >= 20:
                left = [x for x in left if not (x[0].startswith(r[0]) and x[1:] == r[1:])]
        else:
            ng.append('登録にだけある: %s' % (r,))
    # 同じ文字の枠（同じ受付・同じ日の別会場が同じ県など）は画面で1つ＝重なりを消す
    seen = set()
    for x in left:
        if x in seen or x in rk:
            continue
        seen.add(x)
        ng.append('ページにだけある: %s' % (x,))
    fut = sorted({x for ev in evs for x in days(ev)})
    if fut and e.get('date') != fut[-1]:
        ng.append('カードの日付 %s ≠ 最後の公演日 %s' % (e.get('date'), fut[-1]))
    for w in wins:
        if w['venue'] and w['venue'] not in (e.get('venue') or ''):
            ng.append('会場「%s」がカードに無い' % w['venue'])
        if w['pref'] and w['pref'] not in (e.get('prefecture') or ''):
            ng.append('県「%s」がカードの県「%s」に無い' % (w['pref'], e.get('prefecture')))
    t0 = re.sub(r'\s+', ' ', ((data.get('eventGroup') or {}).get('eventGroupTitleWeb') or '')).strip()
    if t0 and t0 != e.get('name'):
        ng.append('公演名が違う: 登録「%s」／ページ「%s」' % (e.get('name'), t0))
    return list(dict.fromkeys(ng)), unknown


def _selftest():
    now = datetime.datetime(2026, 11, 20, 12, 0)
    data = {'eventGroup': {'eventGroupTitleWeb': 'NMIXX SHOW'},
            'sales': [{'salesNo': 1, 'salesNmWeb': '一般発売(先着)', 'salesType': '03'},
                      {'salesNo': 2, 'salesNmWeb': 'FC先行(抽選)', 'salesType': '01'}],
            'events': [{'eventOn': '2026-12-12', 'openEventTm': '18:00', 'venueNm': 'クロコくんホール', 'prefectureCd': '23',
                        'openType': '01', 'salesNos': [1, 2], 'salesRemainNums': [{'salesNo': 1, 'remainNum': 0}],
                        'acceptanceStatuses': [
                            {'salesNo': 1, 'acceptanceStatus': 'during', 'salesStartAt': '2026-10-10T10:00:00', 'salesEndAt': '2026-12-11T23:59:00'},
                            {'salesNo': 2, 'acceptanceStatus': 'before', 'salesStartAt': '2026-11-25T12:00:00', 'salesEndAt': '2026-11-30T23:59:00'}]},
                       {'eventOn': '2027-01-10', 'openEventTm': '17:00', 'venueNm': 'Kアリーナ横浜', 'prefectureCd': '14',
                        'openType': '01', 'salesNos': [1], 'salesRemainNums': [{'salesNo': 1, 'remainNum': 5}],
                        'acceptanceStatuses': [{'salesNo': 1, 'acceptanceStatus': 'during', 'salesStartAt': '2026-10-10T10:00:00',
                                                'salesEndAt': '2027-01-09T23:59:00'}]}]}
    u = 'https://ticket.tickebo.jp/show/event.html?info=1'
    good = {'name': 'NMIXX SHOW', 'date': '2027-01-10', 'venue': 'クロコくんホール／Kアリーナ横浜', 'prefecture': '愛知・神奈川',
            'tickets': [{'type': '一般発売（先着）（愛知 12/12公演）〜12/11 23:59', 'date': '2026-12-11', 'url': u, 'soldout': True},
                        {'type': 'FC先行（抽選）（愛知 12/12公演）11/25 12:00発売〜11/30 23:59', 'date': '2026-11-30', 'startDate': '2026-11-25', 'url': u},
                        {'type': '一般発売（先着）（神奈川 R9年 1/10公演）〜1/9 23:59', 'date': '2027-01-09', 'url': u}]}
    ng, unk = check_entry(good, data, '2026-11-20', now)
    assert ng == [] and unk == [], (ng, unk)
    bad = json.loads(json.dumps(good))
    bad['tickets'][0].pop('soldout')
    assert check_entry(bad, data, '2026-11-20', now)[0]
    bad = json.loads(json.dumps(good))
    bad['tickets'][1]['startDate'] = '2026-11-26'
    assert check_entry(bad, data, '2026-11-20', now)[0]
    assert check_entry(dict(good, date='2026-12-12'), data, '2026-11-20', now)[0]
    assert check_entry(dict(good, prefecture='愛知'), data, '2026-11-20', now)[0]
    assert check_entry(dict(good, tickets=good['tickets'][:2]), data, '2026-11-20', now)[0]
    # 売り場の札と時刻が合わない＝分からない
    d2 = json.loads(json.dumps(data))
    d2['events'][0]['acceptanceStatuses'][1]['acceptanceStatus'] = 'during'
    assert check_entry(good, d2, '2026-11-20', now)[1]
    print('selftest OK: 受付ごとに公演を回す別の向き・時刻から状態を決める/売り切れ・発売日・日付・県・枠の不足で鳴る/札と時刻のずれを出す')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ids', default='')
    ap.add_argument('--built', default='')
    ap.add_argument('--today', default=(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)).date().isoformat())
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
        targets = [(e, e['id']) for e in ev if 'ticket.tickebo.jp/show/event.html' in json.dumps(e.get('links') or {}) + json.dumps(e.get('tickets') or [])
                   and (not want or e['id'] in want)]
    ok, ng, err, unk_all = 0, [], [], []
    for e, key in targets:
        nos = sorted({u for t in (e.get('tickets') or []) + [{'url': (e.get('links') or {}).get('tickebo')}]
                      for u in URL_RE.findall(t.get('url') or '')})
        if len(nos) != 1:
            ng.append((e, key, ['受付ページが %d 個（1興行1カードのはず）: %s' % (len(nos), nos)]))
            continue
        try:
            data = get_json(nos[0], a.sleep)
            now = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)).replace(tzinfo=None)
            msgs, unk = check_entry(e, data, a.today, now)
        except Exception as ex:
            err.append((e, key, nos[0], str(ex)[:80]))
            continue
        if unk:
            unk_all.append((e, key, unk))
        if msgs:
            ng.append((e, key, msgs))
        else:
            ok += 1
    rep = io.open(a.report, 'w', encoding='utf-8')
    rep.write('=== gate_tickebo_slots (today=%s) %s 対象%d件 ===\n' % (a.today, a.built or 'index.html', len(targets)))
    for e, key, msgs in ng:
        rep.write('\n🚨 id=%s %s\n    %s\n' % (key, (e.get('name') or '')[:50], (e.get('links') or {}).get('tickebo')))
        for m in msgs:
            rep.write('    %s\n' % m)
    for e, key, unk in unk_all:
        rep.write('\nℹ️ 分からない受付（札と時刻が合わない・残りが読めない） id=%s %s\n' % (key, (e.get('name') or '')[:40]))
        for m in unk:
            rep.write('    %s\n' % m)
    for e, key, u, why in err:
        rep.write('❌ id=%s info=%s 読めなかった: %s\n' % (key, u, why))
    rep.write('\n=== 集計: 一致 %d / 🚨食い違い %d / ❌読めなかった %d / ℹ️分からない受付があるカード %d ===\n'
              % (ok, len(ng), len(err), len(unk_all)))
    rep.close()
    sys.stderr.write('gate_tickebo_slots: match=%d ng=%d fetcherr=%d unknown=%d -> %s\n' % (ok, len(ng), len(err), len(unk_all), a.report))
    sys.exit(2 if (ng or err) else 0)


if __name__ == '__main__':
    main()
