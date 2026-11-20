# -*- coding: utf-8 -*-
"""チケットボードのハーベスト結果から OSHINAVI のエントリを組む（T-SQUARE形テンプレート・2026-11-20 新設）。

  python tools/build_tickebo_entries.py tmp/x1120/newv/tickebo/harvest.json --out tmp/x1120/newv/tickebo/built.json
  python tools/build_tickebo_entries.py --selftest

## 1受付ページ＝1カード（ツアーは1エントリ＝[[feedback_tour_consolidate]]）
受付ページ（acceptanceNo）は1つの興行（ツアー）で、その下に公演（events）が並び、公演ごとに受付（sales）が付く。
＝カード1枚・**枠は（受付×公演）ごと**（会場・県・締切が公演ごとに違う）。飛び先は全部同じ受付ページ。

## 枠の状態（画面の JS EVT-01-01_performancesList.js の listDisplaySalesEventStatusForType と同じ決まり）
| その公演の受付の状態 | OSHINAVI |
|---|---|
| openType 05（公演終了）・02 中止・04 延期（cls_type.js の開催状況種別） | 載せない |
| 先着（salesType 02）で残り枚数の欄が空 | 🚨載せない（画面の JS は残り0として「買えない」側に倒す＝発売中と言い切れない・数を報告） |
| after（受付終了） | 載せない |
| before（受付前） | 「受付名（県 M/D公演）M/D H:MM発売〜M/D H:MM」・startDate＝その公演の受付開始・date＝受付終了 |
| during・抽選（salesType 01） | 「受付名（…）〜M/D H:MM」（抽選は残り枚数を見ない＝画面も「受付中」） |
| during・先着・残り>0 | 同上 |
| during・先着・残り0 | soldout（画面は「予定枚数終了」） |
| 定価トレード（tradeFlg） | 載せない（公式の譲り合い＝新しい発売ではない・数だけ報告） |
| それ以外・読めない | 🚨推測しない＝枠を作らず報告 |
🚨受付終了が無い＝締切を作らず「〜公演日」。終了が公演日より後なら公演日で締める。
🚨2027年以降の公演日は「R9年 」（締切・発売日の側は年なし）。
🚨同じ日に2公演ある時だけバッジに開演時刻を入れる。

## ジャンル＝トップのジャンル札を機械で写す（ライブ＆ミュージック→musicetc／イベント＆レジャー→event）。札が無ければ空。
"""
import argparse
import collections
import datetime
import importlib.util
import io
import json
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name):
    prev = sys.stdout
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + '.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    sys.stdout = prev
    return mod


BT = _load('build_ticketpay_entries')     # ticket_name / md / mdp / jp / SELLER_SIDE（決まりだけ）
JST = datetime.timezone(datetime.timedelta(hours=9))
PREF_CD = ['北海道', '青森', '岩手', '宮城', '秋田', '山形', '福島', '茨城', '栃木', '群馬', '埼玉', '千葉', '東京', '神奈川',
           '新潟', '富山', '石川', '福井', '山梨', '長野', '岐阜', '静岡', '愛知', '三重', '滋賀', '京都', '大阪', '兵庫', '奈良',
           '和歌山', '鳥取', '島根', '岡山', '広島', '山口', '徳島', '香川', '愛媛', '高知', '福岡', '佐賀', '長崎', '熊本', '大分',
           '宮崎', '鹿児島', '沖縄']
CAT_GENRE = {'ライブ＆ミュージック': 'musicetc', 'イベント＆レジャー': 'event'}


def pref_of(cd):
    try:
        n = int(cd)
    except (TypeError, ValueError):
        return ''
    return PREF_CD[n - 1] if 1 <= n <= 47 else ''


def parse_dt(s):
    """'2026-12-11T23:59:00' → naive datetime（日本時間）"""
    m = re.match(r'(\d{4})-(\d\d)-(\d\d)T(\d\d):(\d\d)', s or '')
    return datetime.datetime(*map(int, m.groups())) if m else None


def hm(dt):
    return '%d:%02d' % (dt.hour, dt.minute)


def tm(s):
    m = re.match(r'(\d{1,2}):(\d\d)', s or '')
    return '%d:%s' % (int(m.group(1)), m.group(2)) if m else ''


def event_days(ev):
    if ev.get('eventOn'):
        return [ev['eventOn']]
    return [d for d in (ev.get('holdStartOn'), ev.get('holdEndOn')) if d]


def build(src, today, now, notes=None):
    """1受付ページ＝1エントリ。載せられないときは (None, 理由)。now＝日本時間の naive datetime。"""
    notes = notes if notes is not None else collections.Counter()
    d = src.get('data') or {}
    eg = d.get('eventGroup') or {}
    title = re.sub(r'\s+', ' ', eg.get('eventGroupTitleWeb') or '').strip()
    if not title:
        return None, '公演名が読めない'
    if BT.SELLER_SIDE.search(title):
        return None, '出す側の申込'
    sales = {s.get('salesNo'): s for s in d.get('sales') or []}
    ty = int(today[:4])
    url = src['url']
    evs = []
    for ev in d.get('events') or []:
        days = event_days(ev)
        if not days:
            notes['公演日が読めない公演'] += 1
            continue
        if ev.get('openType') == '05' or max(days) < today:
            continue
        if ev.get('openType') in ('02', '04'):          # 区分の表（cls_type.js）：02 中止・04 延期
            notes['中止・延期の公演（載せない）'] += 1
            continue
        evs.append((ev, days))
    if not evs:
        return None, 'これからの公演が無い'
    per_day = collections.Counter(days[0] for ev, days in evs if len(days) == 1)
    tickets, skipped, venues, prefs = [], [], [], []
    for ev, days in sorted(evs, key=lambda x: (x[1][0], x[0].get('openEventTm') or '')):
        pref = pref_of(ev.get('prefectureCd'))
        venue = re.sub(r'\s+', ' ', ev.get('venueNm') or '').strip()
        if venue and venue not in venues:
            venues.append(venue)
        if pref and pref not in prefs:
            prefs.append(pref)
        if len(days) == 1:
            show = BT.md(days[0], ty) + (' ' + tm(ev.get('openEventTm')) if per_day[days[0]] > 1 and tm(ev.get('openEventTm')) else '')
        else:
            show = '%s〜%s' % (BT.md(days[0], ty), BT.md(days[-1], ty) if days[-1][:4] != days[0][:4] else BT.mdp(days[-1]))
        last = days[-1]
        acc = {a.get('salesNo'): a for a in ev.get('acceptanceStatuses') or []}
        rem = {r.get('salesNo'): r.get('remainNum') for r in ev.get('salesRemainNums') or []}
        for no in ev.get('salesNos') or []:
            s = sales.get(no)
            if not s:
                notes['受付の中身が無い'] += 1
                continue
            raw = s.get('salesNmWeb') or ''
            if s.get('tradeFlg'):
                notes['定価トレードの受付（載せない）'] += 1
                continue
            if BT.SELLER_SIDE.search(raw):
                skipped.append((raw, '出す側の受付'))
                continue
            a = acc.get(no) or {}
            st_ = a.get('acceptanceStatus')
            sa, ea = parse_dt(a.get('salesStartAt') or s.get('salesStartAt')), parse_dt(a.get('salesEndAt') or s.get('salesEndAt'))
            if st_ == 'after' or (ea is not None and ea < now):
                continue
            nm = BT.ticket_name(raw)
            head = '%s（%s公演）' % (nm, '%s %s' % (pref, show) if pref else show)
            if ea is None or ea.date().isoformat() > last:
                ed, et = last, BT.mdp(last)
            else:
                ed, et = ea.date().isoformat(), '%s %s' % (BT.mdp(ea.date().isoformat()), hm(ea))
            if st_ == 'before':
                if sa is None:
                    skipped.append((raw, '受付前なのに開始が読めない＝日付を作らない'))
                    continue
                tickets.append({'type': '%s%s %s発売〜%s' % (head, BT.mdp(sa.date().isoformat()), hm(sa), et),
                                'date': ed, 'startDate': sa.date().isoformat(), 'url': url})
            elif st_ == 'during':
                r = rem.get(no)
                if s.get('salesType') == '01' or (isinstance(r, int) and r > 0):
                    tickets.append({'type': '%s〜%s' % (head, et), 'date': ed, 'url': url})
                elif r == 0:
                    tickets.append({'type': '%s〜%s' % (head, et), 'date': ed, 'url': url, 'soldout': True, 'soldoutSince': today})
                else:
                    notes[('残り枚数が読めない', str(r))] += 1
                    skipped.append((raw, '受付中なのに残り枚数が読めない'))
            else:
                notes[('読めない受付の状態', str(st_))] += 1
                skipped.append((raw, '読めない受付の状態：%s' % st_))
    seen, uniq = set(), []
    for t in tickets:
        k = (t['type'], t['date'], t.get('startDate'), bool(t.get('soldout')))
        if k not in seen:
            seen.add(k)
            uniq.append(t)
    if not uniq:
        return None, '載せられる枠が無い' + ('：' + skipped[0][1] if skipped else '（受付が全部終わった・定価トレードだけ）')
    all_days = sorted({x for _, days in evs for x in days})
    first, lastd = all_days[0], all_days[-1]
    if first == lastd:
        ev0 = evs[0][0]
        label = BT.jp(first) + (' %s開演' % tm(ev0.get('openEventTm')) if len(evs) == 1 and tm(ev0.get('openEventTm')) else '')
    else:
        label = '%s〜%s' % (BT.jp(first), BT.jp(lastd))
    cats = (src.get('top') or {}).get('cats') or []
    genres = [CAT_GENRE[c] for c in cats if CAT_GENRE.get(c)]
    performers = [re.sub(r'\s+', ' ', p).strip() for p in eg.get('performerNmWebs') or [] if p and p.strip()]
    e = {
        'artist': '／'.join(dict.fromkeys(performers)) or title,
        'name': title,
        'date': lastd,
        'dateLabel': label,
        'venue': '／'.join(venues) or '（会場未定）',
        'prefecture': '・'.join(prefs),
        'genre': 'new',
        '_genre': genres[0] if genres else '',
        '_extraGenres': list(dict.fromkeys(genres[1:])),
        '_srcgenre': 'tickebo:' + ','.join(cats),
        'price': None,
        'links': {'rakuten': None, 'lawson': None, 'pia': None, 'eplus': None, 'tickebo': url},
        'tickets': uniq,
        'verified': True,
        'verifiedAt': today,
    }
    if skipped:
        e['_skipped_slots'] = skipped
    if not genres:
        e['_review'] = ['ジャンル未決（売り場の札：%s）' % ('・'.join(cats) or 'なし')]
    if not prefs:
        notes['県が分からないカード'] += 1
    return e, None


def _selftest():
    today = '2026-11-20'
    now = datetime.datetime(2026, 11, 20, 12, 0)

    def src(events=None, sales=None, cats=None):
        return {'id': 1, 'url': 'https://ticket.tickebo.jp/show/event.html?info=1', 'top': {'cats': cats if cats is not None else ['ライブ＆ミュージック']},
                'data': {'eventGroup': {'eventGroupTitleWeb': 'NMIXX JAPAN DEBUT SHOWCASE', 'performerNmWebs': ['NMIXX']},
                         'sales': sales or [{'salesNo': 1, 'salesNmWeb': '一般発売(先着)', 'salesType': '03', 'tradeFlg': False},
                                            {'salesNo': 2, 'salesNmWeb': 'FC先行(抽選)', 'salesType': '01', 'tradeFlg': False},
                                            {'salesNo': 3, 'salesNmWeb': '定価トレード', 'salesType': '03', 'tradeFlg': True}],
                         'events': events if events is not None else [
                             {'eventOn': '2026-12-12', 'openEventTm': '18:00', 'venueNm': 'クロコくんホール  (旧 日本ガイシホール)',
                              'prefectureCd': '23', 'openType': '01', 'salesNos': [1, 2, 3],
                              'salesRemainNums': [{'salesNo': 1, 'remainNum': 2}, {'salesNo': 2, 'remainNum': 0}],
                              'acceptanceStatuses': [
                                  {'salesNo': 1, 'acceptanceStatus': 'during', 'salesStartAt': '2026-10-10T10:00:00', 'salesEndAt': '2026-12-11T23:59:00'},
                                  {'salesNo': 2, 'acceptanceStatus': 'before', 'salesStartAt': '2026-11-25T12:00:00', 'salesEndAt': '2026-11-30T23:59:00'},
                                  {'salesNo': 3, 'acceptanceStatus': 'during', 'salesStartAt': '2026-10-10T10:00:00', 'salesEndAt': '2026-12-11T23:59:00'}]},
                             {'eventOn': '2027-01-10', 'openEventTm': '17:00', 'venueNm': 'Kアリーナ横浜', 'prefectureCd': '14', 'openType': '01',
                              'salesNos': [1], 'salesRemainNums': [{'salesNo': 1, 'remainNum': 0}],
                              'acceptanceStatuses': [{'salesNo': 1, 'acceptanceStatus': 'during', 'salesStartAt': '2026-10-10T10:00:00',
                                                      'salesEndAt': '2027-01-09T23:59:00'}]},
                             {'eventOn': '2026-11-01', 'openType': '05', 'salesNos': [1], 'acceptanceStatuses': []}]}}
    e, why = build(src(), today, now)
    assert why is None, why
    ty = [(t['type'], t['date'], t.get('startDate'), bool(t.get('soldout'))) for t in e['tickets']]
    assert ty == [('一般発売（先着）（愛知 12/12公演）〜12/11 23:59', '2026-12-11', None, False),
                  ('FC先行（抽選）（愛知 12/12公演）11/25 12:00発売〜11/30 23:59', '2026-11-30', '2026-11-25', False),
                  ('一般発売（先着）（神奈川 R9年 1/10公演）〜1/9 23:59', '2027-01-09', None, True)], ty
    assert e['venue'] == 'クロコくんホール (旧 日本ガイシホール)／Kアリーナ横浜' and e['prefecture'] == '愛知・神奈川', e
    assert e['date'] == '2027-01-10' and e['dateLabel'] == '2026年12月12日(土)〜2027年1月10日(日)', e
    assert e['_genre'] == 'musicetc' and e['artist'] == 'NMIXX' and e['genre'] == 'new'
    # 抽選の受付中は残り0でも受付中・同じ日2公演は開演時刻
    ev2 = [{'eventOn': '2026-12-12', 'openEventTm': t, 'venueNm': 'X', 'prefectureCd': '13', 'openType': '01', 'salesNos': [2],
            'salesRemainNums': [{'salesNo': 2, 'remainNum': 0}],
            'acceptanceStatuses': [{'salesNo': 2, 'acceptanceStatus': 'during', 'salesStartAt': '2026-11-01T10:00:00',
                                    'salesEndAt': '2026-11-30T23:59:00'}]} for t in ('13:00', '18:00')]
    e, _ = build(src(events=ev2), today, now)
    assert [t['type'] for t in e['tickets']] == ['FC先行（抽選）（東京 12/12 13:00公演）〜11/30 23:59',
                                                 'FC先行（抽選）（東京 12/12 18:00公演）〜11/30 23:59'], e['tickets']
    assert e['dateLabel'] == '2026年12月12日(土)'
    # 受付終了・定価トレードだけ・読めない状態・終わった公演だけ＝載せない
    ev3 = [dict(ev2[0], acceptanceStatuses=[dict(ev2[0]['acceptanceStatuses'][0], acceptanceStatus='after')])]
    assert build(src(events=ev3), today, now)[0] is None
    ev4 = [dict(ev2[0], salesNos=[3], acceptanceStatuses=[dict(ev2[0]['acceptanceStatuses'][0], salesNo=3)])]
    assert build(src(events=ev4), today, now)[0] is None
    ev5 = [dict(ev2[0], acceptanceStatuses=[dict(ev2[0]['acceptanceStatuses'][0], acceptanceStatus='pause')])]
    assert build(src(events=ev5), today, now)[0] is None
    assert build(src(events=[dict(ev2[0], eventOn='2026-11-19')]), today, now)[0] is None
    # 終わりが公演日より後＝公演日で締める・ジャンル札なし＝空
    ev6 = [dict(ev2[0], acceptanceStatuses=[dict(ev2[0]['acceptanceStatuses'][0], salesEndAt='2026-12-20T23:59:00')])]
    e, _ = build(src(events=ev6, cats=[]), today, now)
    assert e['tickets'][0]['type'].endswith('〜12/12') and e['tickets'][0]['date'] == '2026-12-12' and e['_genre'] == '', e
    print('selftest OK（受付×公演の枠・先着の残り0＝売り切れ・抽選は受付中・受付前・定価トレード・受付終了・同日2公演・R9年・締切を公演日で締める・ジャンル札）')
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('--out', default='tmp/built_tickebo.json')
    ap.add_argument('--today', default='')
    a = ap.parse_args()
    d = json.load(io.open(a.src, encoding='utf-8'))
    try:
        now = datetime.datetime.strptime(d['harvested_at'], '%Y-%m-%d %H:%M')
    except Exception:
        now = datetime.datetime.now(JST).replace(tzinfo=None)
    today = a.today or now.date().isoformat()
    out, skipped, notes = [], [], collections.Counter()
    for src in d['events']:
        e, why = build(src, today, now, notes)
        if e:
            out.append(e)
        else:
            skipped.append({'id': src['id'], 'name': (src.get('data') or {}).get('eventGroup', {}).get('eventGroupTitleWeb'),
                            'why': why, 'url': src['url']})
    out.sort(key=lambda e: (e['date'], e['name']))
    json.dump({'entries': out, 'skipped': skipped, 'notes': [[str(k), v] for k, v in notes.items()],
               'harvested_at': d.get('harvested_at')}, io.open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('=== 組み上がり %d件 / 載せない %d件 → %s ===' % (len(out), len(skipped), a.out))
    for k, v in collections.Counter(re.sub(r'：.*', '', s['why']) for s in skipped).most_common():
        print('  %s: %d件' % (k, v))
    for k, v in notes.most_common():
        print('  ℹ️ %s: %d' % (k, v))
    st = collections.Counter('売り切れ' if t.get('soldout') else '発売前' if t.get('startDate') else '販売中'
                             for e in out for t in e['tickets'])
    print('  枠 %d: %s' % (sum(st.values()), ' / '.join('%s %d' % kv for kv in st.most_common())))
    print('  ジャンル: ' + ' / '.join('%s %d' % kv for kv in collections.Counter(e['_genre'] or '(空)' for e in out).most_common()))


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        _selftest()
        sys.exit(0)
    main()
