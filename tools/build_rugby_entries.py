# -*- coding: utf-8 -*-
"""TicketRugby のハーベスト結果から OSHINAVI のエントリを組む（T-SQUARE形テンプレート・2026-11-20 新設）。

  python tools/build_rugby_entries.py tmp/x1120/newv/rugby/harvest.json --out tmp/x1120/newv/rugby/built.json
  python tools/build_rugby_entries.py --selftest

## 1試合＝1カード（ホームとアウェイは畳まない＝[[feedback_sports_home_away_never_merge]]）
- TicketRugby は1試合（大学の2試合開催は1枠）＝1つの番号＝1ページ。
- カード名＝売り場の試合名＋「（会場）」、出演者の欄＝チーム名を「／」でつなぐ。
- 飛び先＝ログイン不要の「チケット発売情報」`/ticket_release_info/<番号>`（購入ページ /sales/perform はログインが要る）。

## 枠＝受付ごと（受付名×販売期間）
ページは席種ごとに受付（「一般発売」「【トヨタV】ファンクラブゴールド会員／一次先行発売」…）と販売期間を並べる。
同じ受付名・同じ販売期間を席種をまたいで1枠にまとめる（席種ごとに割ると同じ枠が並ぶだけ）。
| 販売期間と印 | OSHINAVI |
|---|---|
| 終わりが過ぎた | 載せない（終わった受付） |
| 始まる前 | 「受付名（県 M/D H:MM公演）M/D H:MM発売〜M/D H:MM」・startDate＝開始・date＝終わり |
| 期間の中・どれかの席種が 空席あり／残りわずか | 「受付名（…）〜M/D H:MM」・date＝終わり |
| 期間の中・全席種が 空席なし | soldout |
| 期間の中・全席種が 発売期間外 など読めない印 | 🚨推測しない＝枠を作らず報告 |
🚨販売期間の終わりが書いていない＝締切を作らず「〜試合日」（ticketpay・TIGET と同じ）。
🚨終わりが試合日より後なら試合日で締める。🚨2027年以降の試合日は「R9年 」（締切・発売日の側は年なし）。
🚨始まりの読めない受付は日付を作らない＝載せない（報告）。

## ジャンル＝スポーツの試合は "sports"（_srcgenre に売り場のカテゴリ札）
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


BT = _load('build_ticketpay_entries')     # ticket_name / md / mdp / jp（書き方の決まりだけ）
JST = datetime.timezone(datetime.timedelta(hours=9))
LIVE = ('空席あり', '残りわずか')
CANCEL = re.compile(r'中止|延期')


SEASON = re.compile(r'シーズンシート|シーズンパス|シーズンチケット|観戦パック|年間シート')
_HW = {**{c: chr(c - 0xFEE0) for c in list(range(0xFF10, 0xFF1A)) + list(range(0xFF21, 0xFF3B)) + list(range(0xFF41, 0xFF5B))},
       ord('－'): '-', ord('＆'): '&', ord('．'): '.', 0x3000: ' '}


def hw(s):
    """全角の英数字だけ半角に（「浦安Ｄ－Ｒｏｃｋｓ」「ＭＵＦＧスタジアム」）。全角カッコ・【】は残す。"""
    return re.sub(r'\s+', ' ', (s or '').translate(_HW)).strip()


def parse_dt(s):
    """'2026-11-21 14:00' → naive datetime（日本時間）"""
    if not s:
        return None
    m = re.match(r'(\d{4})-(\d\d)-(\d\d) (\d{1,2}):(\d\d)$', s)
    return datetime.datetime(*map(int, m.groups())) if m else None


def hm(dt):
    return '%d:%02d' % (dt.hour, dt.minute)


def build(ev, today, now, notes=None):
    """1試合＝1エントリ。載せられないときは (None, 理由)。now＝日本時間の naive datetime。"""
    notes = notes if notes is not None else collections.Counter()
    date = ev.get('date') or ''
    if not re.match(r'\d{4}-\d\d-\d\d$', date):
        return None, '試合日が読めない'
    if date < today:
        return None, '試合が終わっている'
    if CANCEL.search(ev.get('status') or ''):
        return None, '中止・延期（%s）' % ev.get('status')
    name0 = hw(ev.get('name'))
    if not name0:
        return None, '試合名が読めない'
    if SEASON.search(name0):
        # 何試合分かの券（シーズンシート・観戦パック）＝一覧の日時は1試合の日ではない（0:00・23:00）＝日付を作らない
        return None, 'シーズンシート・観戦パック（1試合の日時ではない）'
    ty = int(today[:4])
    pref = ev.get('prefecture') or ''
    stime = re.sub(r'^0(\d):', r'\1:', ev.get('start') or '')
    show = BT.md(date, ty) + (' ' + stime if stime else '')
    url = ev['url']
    groups = collections.OrderedDict()
    for s in (ev.get('release') or {}).get('seats') or []:
        for w in s.get('windows') or []:
            groups.setdefault((w['name'], w.get('start'), w.get('end')), []).append(w.get('icon') or '')
    if not groups:
        return None, '受付が読めない（チケット発売情報に席種・販売期間が無い）'
    tickets, skipped = [], []

    def endpart(e):
        if e is None or e.date().isoformat() > date:
            return date, BT.mdp(date)
        return e.date().isoformat(), '%s %s' % (BT.mdp(e.date().isoformat()), hm(e))
    for (wname, ws, we), icons in groups.items():
        st, en = parse_dt(ws), parse_dt(we)
        nm = BT.ticket_name(wname)
        head = '%s（%s公演）' % (nm, '%s %s' % (pref, show) if pref else show)
        if en is not None and en < now:
            continue                                   # 終わった受付
        if st is None:
            skipped.append((wname, '始まりが読めない＝日付を作らない'))
            continue
        ed, et = endpart(en)
        if st > now:
            tickets.append({'type': '%s%s %s発売〜%s' % (head, BT.mdp(st.date().isoformat()), hm(st), et),
                            'date': ed, 'startDate': st.date().isoformat(), 'url': url})
        elif any(i in LIVE for i in icons):
            tickets.append({'type': '%s〜%s' % (head, et), 'date': ed, 'url': url})
        elif icons and all(i == '空席なし' for i in icons):
            tickets.append({'type': '%s〜%s' % (head, et), 'date': ed, 'url': url, 'soldout': True, 'soldoutSince': today})
        else:
            notes[('期間の中なのに読めない印', '・'.join(sorted(set(icons))))] += 1
            skipped.append((wname, '期間の中なのに印が %s（発売中にしない）' % '・'.join(sorted(set(icons)))))
    seen, uniq = set(), []
    for t in tickets:
        k = (t['type'], t['date'], t.get('startDate'), bool(t.get('soldout')))
        if k not in seen:
            seen.add(k)
            uniq.append(t)
    names = [t['type'] for t in uniq]
    if len(names) != len(set(names)):
        notes['同じ文字のバッジ（受付名・期間の表記が同じ・売り切れだけ違う）'] += 1
    if not uniq:
        return None, '載せられる枠が無い（受付が全部終わった）' + ('：' + skipped[0][1] if skipped else '')
    teams = [hw(t) for t in ev.get('teams') or [] if t]
    venue = hw(ev.get('venue'))
    e = {
        'artist': '／'.join(dict.fromkeys(teams)) or name0,
        'name': '%s（%s）' % (name0, venue) if venue else name0,
        'date': date,
        'dateLabel': BT.jp(date) + (' %s試合開始' % stime if stime else ''),
        'venue': venue or '（会場未定）',
        'prefecture': pref,
        'genre': 'new',
        '_genre': 'sports',
        '_extraGenres': [],
        '_srcgenre': 'ticketrugby:' + (ev.get('cat') or ''),
        'price': None,
        'links': {'rakuten': None, 'lawson': None, 'pia': None, 'eplus': None, 'ticketrugby': url},
        'tickets': uniq,
        'verified': True,
        'verifiedAt': today,
    }
    if skipped:
        e['_skipped_slots'] = skipped
    if not pref:
        notes['県が分からない'] += 1
    return e, None


def _selftest():
    today = '2026-11-20'
    now = datetime.datetime(2026, 11, 20, 12, 0)

    def ev(windows=None, date='2026-11-21', status='発売中', pref='愛知', start='13:00', seats=None):
        w = windows if windows is not None else [
            {'name': '【トヨタV】ファンクラブゴールド会員／一次先行発売', 'icon': '発売期間外', 'start': '2026-10-10 10:00', 'end': '2026-10-17 9:59'},
            {'name': '一般発売', 'icon': '空席なし', 'start': '2026-10-17 10:00', 'end': '2026-11-21 14:00'}]
        return {'id': 1, 'url': 'https://ticketrugby.jp/ticket_release_info/1', 'status': status, 'date': date,
                'start': start, 'venue': 'トヨタスポーツセンター 陸上競技場', 'prefecture': pref, 'cat': 'その他',
                'name': 'トヨタヴェルブリッツ対静岡ブルーレヴズ プレシーズンマッチ', 'teams': ['トヨタヴェルブリッツ', '静岡ブルーレヴズ'],
                'release': {'seats': seats if seats is not None else [
                    {'seat': '指定席', 'windows': w},
                    {'seat': '自由席', 'windows': [dict(w[0]), dict(w[1], icon='空席あり')]}]}}
    # ① 終わった先行は落とす・一般は席種をまたいで1枠（どれかが空席あり＝販売中）
    e, why = build(ev(), today, now)
    assert e['tickets'] == [{'type': '一般発売（愛知 11/21 13:00公演）〜11/21 14:00', 'date': '2026-11-21',
                             'url': 'https://ticketrugby.jp/ticket_release_info/1'}], e['tickets']
    assert e['name'] == 'トヨタヴェルブリッツ対静岡ブルーレヴズ プレシーズンマッチ（トヨタスポーツセンター 陸上競技場）', e['name']
    assert e['artist'] == 'トヨタヴェルブリッツ／静岡ブルーレヴズ' and e['_genre'] == 'sports' and e['genre'] == 'new'
    assert e['dateLabel'] == '2026年11月21日(土) 13:00試合開始'
    # ② 全席種が空席なし＝soldout
    w = [{'name': '一般発売', 'icon': '空席なし', 'start': '2026-10-17 10:00', 'end': '2026-11-21 14:00'}]
    e, _ = build(ev(seats=[{'windows': w}, {'windows': [dict(w[0])]}]), today, now)
    assert e['tickets'][0]['soldout'], e['tickets']
    # ③ 始まる前＝発売日つき・2027年は R9年・終わりが試合日より後は試合日で締める
    w = [{'name': 'ファンクラブ先行（抽選）', 'icon': '発売期間外', 'start': '2026-12-01 10:00', 'end': '2027-01-20 23:59'}]
    e, _ = build(ev(date='2027-01-16', seats=[{'windows': w}]), today, now)
    t = e['tickets'][0]
    assert t['type'] == 'ファンクラブ先行（抽選）（愛知 R9年 1/16 13:00公演）12/1 10:00発売〜1/16', t
    assert t['date'] == '2027-01-16' and t['startDate'] == '2026-12-01', t
    # ④ 期間の中なのに全部 発売期間外＝載せない・終わりが無い＝〜試合日
    w = [{'name': '一般発売', 'icon': '発売期間外', 'start': '2026-10-17 10:00', 'end': '2026-11-21 14:00'}]
    assert build(ev(seats=[{'windows': w}]), today, now)[0] is None
    w = [{'name': '一般発売', 'icon': '空席あり', 'start': '2026-10-17 10:00', 'end': None}]
    e, _ = build(ev(seats=[{'windows': w}]), today, now)
    assert e['tickets'][0]['type'] == '一般発売（愛知 11/21 13:00公演）〜11/21' and e['tickets'][0]['date'] == '2026-11-21'
    # ⑤ 始まりが読めない・中止・終わった試合・全部終わった受付
    assert build(ev(seats=[{'windows': [dict(w[0], start=None)]}]), today, now)[0] is None
    assert build(ev(status='中止'), today, now)[0] is None
    assert build(ev(date='2026-11-19'), today, now)[0] is None
    w = [{'name': '一般発売', 'icon': '空席あり', 'start': '2026-10-17 10:00', 'end': '2026-11-19 14:00'}]
    assert build(ev(seats=[{'windows': w}]), today, now)[0] is None
    # ⑥ 県が無ければバッジから県を落とす
    e, _ = build(ev(pref=''), today, now)
    assert e['tickets'][0]['type'].startswith('一般発売（11/21 13:00公演）'), e['tickets']
    # ⑦ 全角英数字は半角（カッコ・【】は残す）・シーズンシートは載せない
    e, _ = build(dict(ev(), name='浦安Ｄ－Ｒｏｃｋｓ対東京サンゴリアス', teams=['浦安Ｄ－Ｒｏｃｋｓ'], venue='ＭＵＦＧスタジアム'), today, now)
    assert e['artist'] == '浦安D-Rocks' and e['venue'] == 'MUFGスタジアム' and e['name'] == '浦安D-Rocks対東京サンゴリアス（MUFGスタジアム）', e
    assert build(dict(ev(), name='【秩父宮ラグビー場】ブラックラムズ東京　シーズンシート'), today, now)[0] is None
    print('selftest OK（全角英数字・シーズンシート・終わった受付を落とす・席種をまたいで1枠・売り切れ・発売前・R9年・試合日で締める・読めない印・終わりなし・始まりなし・中止・県なし）')
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('--out', default='tmp/built_rugby.json')
    ap.add_argument('--today', default='')
    a = ap.parse_args()
    d = json.load(io.open(a.src, encoding='utf-8'))
    try:
        now = datetime.datetime.strptime(d['harvested_at'], '%Y-%m-%d %H:%M')
    except Exception:
        now = datetime.datetime.now(JST).replace(tzinfo=None)
    today = a.today or now.date().isoformat()
    out, skipped, notes = [], [], collections.Counter()
    for ev in d['events']:
        e, why = build(ev, today, now, notes)
        if e:
            out.append(e)
        else:
            skipped.append({'id': ev['id'], 'name': ev.get('name'), 'why': why, 'url': ev.get('url')})
    out.sort(key=lambda e: (e['date'], e['name']))
    json.dump({'entries': out, 'skipped': skipped, 'notes': [[str(k), v] for k, v in notes.items()],
               'harvested_at': d.get('harvested_at')},
              io.open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('=== 組み上がり %d件 / 載せない %d件 → %s ===' % (len(out), len(skipped), a.out))
    for k, v in collections.Counter(re.sub(r'：.*', '', s['why']) for s in skipped).most_common():
        print('  %s: %d件' % (k, v))
    for k, v in notes.most_common():
        print('  ℹ️ %s: %d' % (k, v))
    st = collections.Counter('売り切れ' if t.get('soldout') else '発売前' if t.get('startDate') else '販売中'
                             for e in out for t in e['tickets'])
    print('  枠 %d: %s' % (sum(st.values()), ' / '.join('%s %d' % kv for kv in st.most_common())))


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        _selftest()
        sys.exit(0)
    main()
