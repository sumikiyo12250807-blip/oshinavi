# -*- coding: utf-8 -*-
"""B.LEAGUE チケットのハーベスト結果から OSHINAVI のエントリを組む（T-SQUARE形テンプレート・2026-11-20 新設）。

  python tools/build_bleague_entries.py tmp/x1120/newv/bleague/harvest.json --out tmp/x1120/newv/bleague/built.json
  python tools/build_bleague_entries.py --selftest

## 1試合＝1カード（ホームとアウェイは畳まない＝[[feedback_sports_home_away_never_merge]]）
- B.LEAGUE チケットは1試合＝1つの eventId＝1ページ（売るのは主催＝ホームのクラブ）。
- 同じ対戦・同じ日でも、別の eventId（例「仙台横丁会ver(当日引換券)」の別の販売グループ）は別カード（URL が違う）。
- カード名＝「ホーム対アウェイ（会場） 大会名」、出演者の欄＝「ホーム／アウェイ」（正式なチーム名）。

## 枠＝「一般販売」1つ（ログインしていない人に見える受付）
B.LEAGUE の販売スケジュールは「条件つき」（ファンクラブの会員ランク・ステージ）と「条件なし」に分かれる。
画面（ログインしていない人）は条件なしのスケジュールだけで状態を出す＝ここもそれだけを枠にする。
条件つきのスケジュールには**名前が無い**（API にも画面にも受付名が出ない）＝名前を作らない＝枠にしない（数だけ報告）。
| 売り場の状態 | OSHINAVI |
|---|---|
| 条件なしのどれかが始まっている・残りあり | 「一般販売（県 M/D H:MM公演）〜M/D H:MM」・date＝販売終了（saleEndAt） |
| 同・残り0（total>0） | soldout（売り切れ） |
| 条件なしが全部これから | 「…M/D H:MM発売〜M/D H:MM」・startDate＝いちばん早い開始・date＝販売終了 |
| SALE_ENDED／販売終了の時刻を過ぎた | soldout＋saleEnded（販売終了） |
| 準備中（canNavigateToDetail=false・SUSPENDED）・中止・条件なしが無い・残りが読めない | 🚨載せない（報告） |
🚨販売終了（saleEndAt）が無い時は締切を作らず「〜公演日」（ticketpay・TIGET と同じ）。
🚨販売終了が試合日より後なら試合日で締める。
🚨2027年以降の試合日は「R9年 」を付ける（締切・発売日の側は年なし）。

## ジャンル＝スポーツの試合は "sports"（_srcgenre に売り場の札 SPORTS_BASKETBALL）
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
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + '.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


BH = _load('bleague_harvest')        # utc_to_jst / page_url
JST = BH.JST
WD = '月火水木金土日'
GENRE_MAP = {'SPORTS_BASKETBALL': 'sports'}


def era(y, ty):
    return 'R%d年 ' % (y - 2018) if y > ty else ''


def md(iso, ty):
    return '%s%d/%d' % (era(int(iso[:4]), ty), int(iso[5:7]), int(iso[8:10]))


def mdp(iso):
    return '%d/%d' % (int(iso[5:7]), int(iso[8:10]))


def jp(iso):
    y, m, d = int(iso[:4]), int(iso[5:7]), int(iso[8:10])
    return '%d年%d月%d日(%s)' % (y, m, d, WD[datetime.date(y, m, d).weekday()])


def short_pref(p):
    p = (p or '').strip()
    if p and p != '北海道' and p[-1] in '都府県':
        return p[:-1]
    return p


def undef(v):
    return v in (None, '', '$undefined')


def team(gsd, side):
    t = (gsd or {}).get(side) or {}
    return (t.get('name') or t.get('abbreviatedName') or '').strip()


def hm(dt):
    return '%d:%02d' % (dt.hour, dt.minute)


def build(ev, today, now, notes=None):
    """1試合＝1エントリ。載せられないときは (None, 理由)。now＝日本時間の datetime（tz付き）。"""
    notes = notes if notes is not None else collections.Counter()
    s = ev.get('summary') or {}
    d = ev.get('detail') or {}
    date = s.get('eventStartDateJst') or ''
    if not re.match(r'\d{4}-\d\d-\d\d$', date):
        return None, '試合日が読めない'
    if date < today:
        return None, '試合が終わっている'
    stime = s.get('eventStartTimeJst')
    stime = '' if undef(stime) else re.sub(r'^0(\d):', r'\1:', stime)
    status = s.get('salesStatus')
    if not s.get('canNavigateToDetail'):
        return None, '準備中（試合ページがまだ開かない）'
    if status == 'SUSPENDED':
        return None, '準備中（SUSPENDED）'
    if status == 'EVENT_CANCELED':
        return None, '中止'
    if status not in ('BEFORE_SALE', 'ON_SALE', 'SALE_ENDED'):
        notes[('読めない状態', status)] += 1
        return None, '読めない状態：%s（発売中にしない）' % status
    if not d:
        return None, '試合の詳細が読めない'
    gsd = d.get('genreSpecificData') or {}
    home, away = team(gsd, 'homeTeam'), team(gsd, 'awayTeam')
    group = ((d.get('eventGroupSummary') or {}).get('name') or '').strip()
    venue_d = d.get('venue') or {}
    venue = (venue_d.get('displayName') or '').strip()
    pref = short_pref(venue_d.get('prefecture') or (s.get('venueSummary') or {}).get('prefecture'))
    custom = d.get('customEventName') or s.get('customEventName')
    if d.get('displayFormat') == 'MATCH_EVENT' and home and away:
        name = '%s対%s（%s） %s' % (home, away, venue or '会場未定', group)
        artist = '%s／%s' % (home, away)
    else:
        name = (custom if not undef(custom) else '') or group
        if not name:
            return None, '試合名が読めない'
        artist = name
    name = re.sub(r'\s+', ' ', name).strip()
    # 2026-11-24 抜き打ち 57757：シーズンシート・席パック＝販売用の器（器の日付に試合は無い）＝試合として出さない
    SEASON = bool(re.search(r'シーズンシート|シーズンチケット|シーズンパス|年間シート|パック|プラン', name)) or (home and away and home == away)
    if SEASON:
        artist = home or artist.split('／')[0]
        name = name.replace('%s対%s（%s） ' % (home, away, venue or '会場未定'), '').strip() or name
        if artist not in name:
            name = artist + ' ' + name
    if '駐車' in name:
        # 2026-11-20 クラブが駐車券を同じ売り場で売っている（29件）＝試合の券ではないので載せない
        return None, '駐車券（試合の券ではない）'

    end = BH.utc_to_jst(d.get('saleEndAt'))
    scheds = d.get('salesSchedules') or []
    guest = [BH.utc_to_jst(x.get('saleStartAt')) for x in scheds if undef(x.get('condition'))]
    if any(g is None for g in guest):
        return None, '一般の販売開始が読めない'
    fc_future = [x for x in scheds if not undef(x.get('condition'))
                 and (BH.utc_to_jst(x.get('saleStartAt')) or now) > now]
    if fc_future:
        notes['条件つき（先行）のこれからの受付がある試合'] += 1

    def endpart(e):
        """締切＝販売終了。試合日より後なら試合日で締める。無ければ〜試合日（時刻なし）。"""
        if e is None:
            return date, mdp(date)
        if e.date().isoformat() > date:
            return date, mdp(date)
        return e.date().isoformat(), '%s %s' % (mdp(e.date().isoformat()), hm(e))
    show = md(date, int(today[:4])) + (' ' + stime if stime else '')
    head = '一般販売（%s公演）' % ('%s %s' % (pref, show) if pref else show)
    if SEASON:
        head = '一般販売（シーズンシート・席のセット）'
    url = ev.get('url') or BH.page_url(ev.get('host'), ev.get('id'))
    if status == 'SALE_ENDED' or (end is not None and end <= now):
        ed, et = endpart(end)
        tk = {'type': '%s〜%s' % (head, et), 'date': ed, 'url': url,
              'soldout': True, 'soldoutSince': today, 'saleEnded': True, 'saleEndedSince': today}
    else:
        if not guest:
            return None, '一般の受付が無い（条件つきの先行だけ）'
        started = [g for g in guest if g <= now]
        ed, et = endpart(end)
        if started:
            st = ev.get('stock')
            if not st or st.get('remaining') is None:
                return None, '残り枚数が読めない（画面は準備中）'
            if st.get('remaining') == 0:
                if not st.get('total'):
                    return None, '在庫の入荷待ち（total 0）'
                tk = {'type': '%s〜%s' % (head, et), 'date': ed, 'url': url, 'soldout': True, 'soldoutSince': today}
            else:
                tk = {'type': '%s〜%s' % (head, et), 'date': ed, 'url': url}
        else:
            g0 = min(guest)
            tk = {'type': '%s%s %s発売〜%s' % (head, mdp(g0.date().isoformat()), hm(g0), et),
                  'date': ed, 'startDate': g0.date().isoformat(), 'url': url}
    srcg = gsd.get('genre') or ''
    if SEASON:
        date = tk['date']
    e = {
        'artist': artist,
        'name': name,
        'date': date,
        'dateLabel': ('ホームゲームの席のセット販売（%s）' % (pref or venue or '')) if SEASON else (jp(date) + (' %s試合開始' % stime if stime else '')),
        'venue': venue or '（会場未定）',
        'prefecture': pref,
        'genre': 'new',
        '_genre': GENRE_MAP.get(srcg, ''),
        '_extraGenres': [],
        '_srcgenre': 'bleague:' + srcg,
        'price': None,
        'links': {'rakuten': None, 'lawson': None, 'pia': None, 'eplus': None, 'bleague': url},
        'tickets': [tk],
        'verified': True,
        'verifiedAt': today,
    }
    if not e['_genre']:
        e['_review'] = ['ジャンル未決（売り場の札：%s）' % (srcg or 'なし')]
    if not pref:
        notes['県が分からない'] += 1
    return e, None


def _selftest():
    today = '2026-11-20'
    now = datetime.datetime(2026, 11, 20, 12, 0, tzinfo=JST)

    def ev(status='ON_SALE', nav=True, scheds=None, end='2026-12-19T08:05:00Z', stock=None, date='2026-12-19',
           time_='15:05', detail=True):
        s = {'eventId': 'E1', 'hostTenantCode': 'lh', 'eventStartDateJst': date, 'eventStartTimeJst': time_,
             'salesStatus': status, 'canNavigateToDetail': nav, 'venueSummary': {'prefecture': '北海道'}}
        dd = {'displayFormat': 'MATCH_EVENT', 'saleEndAt': end,
              'eventGroupSummary': {'name': 'りそなグループ B.LEAGUE 2026-27 B.LEAGUE PREMIER リーグ戦'},
              'venue': {'displayName': '北海きたえーる', 'prefecture': '北海道'},
              'genreSpecificData': {'genre': 'SPORTS_BASKETBALL', 'homeTeam': {'name': 'レバンガ北海道'},
                                    'awayTeam': {'name': '川崎ブレイブサンダース'}},
              'salesSchedules': scheds if scheds is not None else [
                  {'condition': {'items': []}, 'saleStartAt': '2026-10-26T09:00:00Z'},
                  {'saleStartAt': '2026-10-30T11:00:00Z'}]}
        return {'id': 'E1', 'host': 'lh', 'url': 'https://ticket.bleague.jp/clubs/lh/events/E1', 'summary': s,
                'detail': dd if detail else None, 'stock': stock if stock is not None else {'remaining': 5, 'total': 9}}
    # ① 販売中＝〜販売終了（日本時間）・カード名＝対戦カード（会場）大会名
    e, why = build(ev(), today, now)
    assert e['tickets'] == [{'type': '一般販売（北海道 12/19 15:05公演）〜12/19 17:05', 'date': '2026-12-19',
                             'url': 'https://ticket.bleague.jp/clubs/lh/events/E1'}], e['tickets']
    assert e['name'] == 'レバンガ北海道対川崎ブレイブサンダース（北海きたえーる） りそなグループ B.LEAGUE 2026-27 B.LEAGUE PREMIER リーグ戦', e['name']
    assert e['artist'] == 'レバンガ北海道／川崎ブレイブサンダース' and e['_genre'] == 'sports' and e['genre'] == 'new'
    assert e['dateLabel'] == '2026年12月19日(土) 15:05試合開始' and e['prefecture'] == '北海道'
    # ② 残り0＝売り切れ・total 0＝入荷待ちは載せない
    e, _ = build(ev(stock={'remaining': 0, 'total': 100}), today, now)
    assert e['tickets'][0]['soldout'] and 'saleEnded' not in e['tickets'][0]
    assert build(ev(stock={'remaining': 0, 'total': 0}), today, now)[0] is None
    assert build(ev(stock={}), today, now)[0] is None                       # 残りが読めない
    # ③ 発売前＝いちばん早い条件なしの開始・date＝販売終了・2027年は R9年
    e, _ = build(ev(status='BEFORE_SALE', date='2027-01-23', time_='13:35', end='2027-01-23T06:35:00Z',
                    scheds=[{'condition': {'items': [1]}, 'saleStartAt': '2026-11-30T11:00:00Z'},
                            {'saleStartAt': '2026-12-04T11:00:00Z'}, {'saleStartAt': '2026-12-05T11:00:00Z'}]),
                 today, now)
    t = e['tickets'][0]
    assert t['type'] == '一般販売（北海道 R9年 1/23 13:35公演）12/4 20:00発売〜1/23 15:35', t
    assert t['date'] == '2027-01-23' and t['startDate'] == '2026-12-04', t
    # ④ 準備中・中止・一般なし・詳細なしは載せない
    assert build(ev(nav=False), today, now)[0] is None
    assert build(ev(status='SUSPENDED'), today, now)[0] is None
    assert build(ev(status='EVENT_CANCELED'), today, now)[0] is None
    assert '先行だけ' in build(ev(scheds=[{'condition': {'items': [1]}, 'saleStartAt': '2026-10-26T09:00:00Z'}]), today, now)[1]
    assert build(ev(detail=False), today, now)[0] is None
    assert '読めない状態' in build(ev(status='WHATEVER'), today, now)[1]
    # ⑤ 販売終了＝soldout＋saleEnded／時刻なし・終了なし＝〜試合日
    e, _ = build(ev(status='SALE_ENDED'), today, now)
    assert e['tickets'][0]['saleEnded'] and e['tickets'][0]['soldout']
    e, _ = build(ev(time_='$undefined', end='$undefined'), today, now)
    assert e['tickets'][0]['type'] == '一般販売（北海道 12/19公演）〜12/19' and e['tickets'][0]['date'] == '2026-12-19', e['tickets']
    assert e['dateLabel'] == '2026年12月19日(土)'
    # ⑥ 販売終了が試合日より後なら試合日で締める
    e, _ = build(ev(end='2026-12-21T00:00:00Z'), today, now)
    assert e['tickets'][0]['type'].endswith('〜12/19') and e['tickets'][0]['date'] == '2026-12-19'
    # ⑦ 終わった試合は載せない
    assert build(ev(date='2026-11-19'), today, now)[0] is None
    print('selftest OK（販売中・売り切れ・入荷待ち・発売前・R9年・準備中/中止/先行だけ/詳細なし・販売終了・時刻なし・締切を試合日で締める・終わった試合）')
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('--out', default='tmp/built_bleague.json')
    ap.add_argument('--today', default='')
    a = ap.parse_args()
    d = json.load(io.open(a.src, encoding='utf-8'))
    today = a.today or d.get('today') or datetime.datetime.now(JST).date().isoformat()
    # 「今」＝ハーベストした時刻（残り枚数を読んだ時の状態に合わせる）
    try:
        now = datetime.datetime.strptime(d['harvested_at'], '%Y-%m-%d %H:%M').replace(tzinfo=JST)
    except Exception:
        now = datetime.datetime.now(JST)
    out, skipped, notes = [], [], collections.Counter()
    for ev in d['events']:
        e, why = build(ev, today, now, notes)
        if e:
            out.append(e)
        else:
            skipped.append({'id': ev['id'], 'why': why, 'url': ev.get('url'),
                            'date': (ev.get('summary') or {}).get('eventStartDateJst')})
    out.sort(key=lambda e: (e['date'], e['name']))
    json.dump({'entries': out, 'skipped': skipped, 'notes': [[str(k), v] for k, v in notes.items()],
               'harvested_at': d.get('harvested_at')},
              io.open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('=== 組み上がり %d件 / 載せない %d件 → %s ===' % (len(out), len(skipped), a.out))
    for k, v in collections.Counter(re.sub(r'：.*', '', s['why']) for s in skipped).most_common():
        print('  %s: %d件' % (k, v))
    for k, v in notes.most_common():
        print('  ℹ️ %s: %d' % (k, v))
    st = collections.Counter('売り切れ' if e['tickets'][0].get('soldout') and not e['tickets'][0].get('saleEnded')
                             else '販売終了' if e['tickets'][0].get('saleEnded')
                             else '発売前' if e['tickets'][0].get('startDate') else '販売中' for e in out)
    print('  枠: ' + ' / '.join('%s %d' % kv for kv in st.most_common()))


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        _selftest()
        sys.exit(0)
    main()
