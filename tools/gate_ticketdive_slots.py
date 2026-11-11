# -*- coding: utf-8 -*-
"""TicketDive 由来の枠の番人＝**公演ページ（HTML）を読み直して、組み立てとは別の書き方で枠を作り、登録と全件突合**する。

  python tools/gate_ticketdive_slots.py                          … index.html の TicketDive 枠を全部照合
  python tools/gate_ticketdive_slots.py --ids 1,2                … id 指定
  python tools/gate_ticketdive_slots.py --built tmp/built_ticketdive_MMDD.json   … 投入前の組み上がりを照合
  python tools/gate_ticketdive_slots.py --selftest

終了コード 0＝全一致 / 2＝食い違い・読めない あり（投入・push の前に 0 を確かめる）

## 組み立て（build_ticketdive_entries）と**別に**作る
- 読む所が違う＝組み立ては `/_next/data/…json`、番人は**公演ページの HTML**（`<script id="__NEXT_DATA__">`）。
- UTC→JST・状態の判定・締切を公演日で締める、を**ここで書き直している**（組み立ての関数は使わない）。
  共有するのは券種名の整え方（ticket_name）と「出す側」の線引き（is_seller_side）だけ＝決まりであって読み方ではない。
- バッジの文字を**読み戻して**（受付名・公演日・開演・発売日時・締切・売り切れ）比べる＝画面の文字の食い違いが分かる。
- カードの日付＝最後の公演日、会場名、県（決まった時は住所の県名と一致するか）も見る。
- 受付期間の内なのに残りあり＋closed 等の「分からない」受付は、組み立てが落としている＝食い違いにはせず数を出す。
"""
import argparse
import datetime
import importlib.util
import io
import json
import os
import re
import sys
import time

_KEEP = []
HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name):
    prev = sys.stdout
    _KEEP.append(prev)
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + '.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _KEEP.append(sys.stdout)
    sys.stdout = prev
    return mod


BT = _load('build_tiget_entries')     # ticket_name / is_seller_side / STREAM_RE（決まりだけ）
TD = _load('ticketdive_harvest')      # fetch / next_data（HTML を読むだけ）
if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
REPORT = 'tmp/gate_ticketdive_report.txt'
JST9 = datetime.timedelta(hours=9)
PREFS = ('北海道 青森 岩手 宮城 秋田 山形 福島 茨城 栃木 群馬 埼玉 千葉 東京 神奈川 新潟 富山 石川 福井 山梨 長野 '
         '岐阜 静岡 愛知 三重 滋賀 京都 大阪 兵庫 奈良 和歌山 鳥取 島根 岡山 広島 山口 徳島 香川 愛媛 高知 福岡 佐賀 '
         '長崎 熊本 大分 宮崎 鹿児島 沖縄').split()


def j(iso):
    """UTC の ISO 文字列 → JST の naive datetime（組み立てとは別の書き方）。"""
    if not iso:
        return None
    m = re.match(r'(\d{4})-(\d\d)-(\d\d)T(\d\d):(\d\d):(\d\d)', iso)
    if not m:
        return None
    return datetime.datetime(*[int(x) for x in m.groups()]) + JST9


def md(dt):
    return '%d/%d' % (dt.month, dt.day)


def page_windows(ed, today, now):
    """公演ページの eventDetail → 期待する枠のリスト（受付×公演）と、分からない受付の説明。
    枠＝{'name','show','time'(同日2公演の時の開演),'sale'(発売前の時 'M/D H:MM'),'end'('M/D H:MM' or 'M/D'),
         'end_date','start_date','soldout'}"""
    stages = []
    for s in (ed.get('stages') or []) + (ed.get('multiDaysStages') or []):
        st = j(s.get('startStage')) or j(s.get('openVenue'))
        if st:
            stages.append((s.get('id'), st, (s.get('venue') or {}).get('name') or s.get('stageName') or '',
                           (s.get('venue') or {}).get('address') or ''))
    days = {}
    for _, st, _, _ in stages:
        days[st.date()] = days.get(st.date(), 0) + 1
    out, unknown = [], []
    for info in ed.get('ticketInfoList') or []:
        rel = j(info.get('release'))
        if rel and rel > now:
            continue
        raw = info.get('name') or ''
        if BT.is_seller_side(raw):
            continue
        types = [t for t in info.get('ticketTypes') or []
                 if not (BT.is_seller_side(t.get('name')) and not re.search(r'取り置き|取置|チェキ', t.get('name') or ''))]
        if not types:
            continue
        stream = bool(re.search(BT.STREAM_RE, raw))
        sa, ea = j(info.get('startApply')), j(info.get('endApply'))
        use_sid = any(t.get('stageIds') for t in types)
        for sid, st, venue, addr in stages:
            if st.date().isoformat() < today and not stream:
                continue
            ts = [t for t in types if sid in (t.get('stageIds') or [])] if use_sid else types
            if not ts:
                continue
            if ea and (ea.date() <= st.date() or stream):
                end_date, end = ea.date().isoformat(), '%s %d:%02d' % (md(ea), ea.hour, ea.minute)
            else:
                end_date, end = st.date().isoformat(), md(st)
            if end_date < today:
                continue
            w = {'name': BT.ticket_name(raw), 'show': md(st), 'year': st.year,
                 'time': ('%d:%02d' % (st.hour, st.minute)) if days[st.date()] > 1 else None,
                 'end': end, 'end_date': end_date, 'sale': None, 'start_date': None, 'soldout': False,
                 'venue': venue, 'addr': addr}
            rates = [t.get('remainingRate') for t in ts]
            if sa and now < sa:
                w['sale'] = '%s %d:%02d' % (md(sa), sa.hour, sa.minute)
                w['start_date'] = sa.date().isoformat()
            elif rates and all(r == 0 for r in rates):
                w['soldout'] = True
            elif info.get('status') != 'closed' and any((r or 0) > 0 and t.get('status') != 'closed' for r, t in zip(rates, ts)):
                pass
            else:
                unknown.append('%s（%s公演）status=%s 残り=%s' % (raw[:20], md(st), info.get('status'), rates))
                continue
            out.append(w)
    return out, unknown, stages


BADGE_RE = re.compile(r'^(?P<name>.*)（(?:(?P<pref>(?!R\d+年)[^\s（）]+) )?(?:R(?P<r>\d+)年 )?(?P<show>\d{1,2}/\d{1,2})'
                      r'(?: (?P<time>\d{1,2}:\d{2}))?公演）'
                      r'(?:(?P<sale>\d{1,2}/\d{1,2} \d{1,2}:\d{2})発売|〜(?P<end>\d{1,2}/\d{1,2}(?: \d{1,2}:\d{2})?))$')


def badge_key(t):
    """登録の枠 → 比べる形（バッジの文字を読み戻す）。読めない形は None。"""
    m = BADGE_RE.match(t.get('type') or '')
    if not m:
        return None
    return (m.group('name'), m.group('show'), m.group('time'), m.group('sale'),
            None if m.group('sale') else m.group('end'), bool(t.get('soldout')),
            t.get('date'), t.get('startDate') if m.group('sale') else None)


def window_key(w):
    return (w['name'], w['show'], w['time'], w['sale'], None if w['sale'] else w['end'], w['soldout'],
            w['end_date'], w['start_date'])


def check_entry(e, ed, today, now):
    """1カード（登録か組み上がり）と公演ページを突き合わせる → (食い違いのリスト, 分からない受付のリスト)。"""
    ng = []
    reg = [t for t in e.get('tickets') or [] if 'ticketdive.com' in (t.get('url') or '')]
    rk = []
    for t in reg:
        k = badge_key(t)
        if k is None:
            ng.append('バッジの文字が読めない: %s' % t.get('type'))
        else:
            rk.append(k)
        m = BADGE_RE.match(t.get('type') or '')
        if m and m.group('pref') and m.group('pref') not in PREFS:
            ng.append('バッジの県が県名でない: %s' % t.get('type'))
    wins, unknown, stages = page_windows(ed, today, now)
    pk = [window_key(w) for w in wins]
    for k in sorted(set(rk) - set(pk), key=str):
        ng.append('登録にだけある: %s' % (k,))
    for k in sorted(set(pk) - set(rk), key=str):
        ng.append('公演ページにだけある: %s' % (k,))
    if len(rk) != len(set(rk)):
        ng.append('同じ枠が2つ以上ある')
    fut = sorted({st.date().isoformat() for _, st, _, _ in stages if st.date().isoformat() >= today})
    if fut and e.get('date') != fut[-1]:
        ng.append('カードの日付 %s ≠ 最後の公演日 %s' % (e.get('date'), fut[-1]))
    for _, st, venue, addr in stages:
        if st.date().isoformat() >= today and venue and venue not in (e.get('venue') or ''):
            ng.append('会場「%s」がカードに無い' % venue)
        ap = [p for p in PREFS if p + ('' if p == '北海道' else ('都' if p == '東京' else '府' if p in ('大阪', '京都') else '県')) in addr]
        if st.date().isoformat() >= today and len(ap) == 1 and ap[0] not in (e.get('prefecture') or ''):
            ng.append('住所の県 %s がカードの県「%s」に無い' % (ap[0], e.get('prefecture')))
    ev = ed.get('event') or {}
    if ev.get('name') and ev['name'] != e.get('name'):
        ng.append('公演名が違う: 登録「%s」／ページ「%s」' % (e.get('name'), ev['name']))
    return ng, unknown


def load_page(url_key, sleep):
    html = TD.fetch('https://ticketdive.com/event/' + url_key, sleep=sleep)
    nd = TD.next_data(html)
    if not nd:
        raise ValueError('__NEXT_DATA__ が無い')
    ed = TD.sj(nd['props']).get('eventDetail')
    if not ed:
        raise ValueError('eventDetail が無い（公開が終わった疑い）')
    return ed


def _selftest():
    now = datetime.datetime(2026, 11, 12, 9, 0)
    today = '2026-11-12'
    ed = {'event': {'name': 'テスト'},
          'stages': [{'id': 'S1', 'startStage': '2026-12-03T10:00:00.000Z', 'openVenue': '2026-12-03T09:30:00.000Z',
                      'venue': {'name': '恵比寿CreAto', 'address': '東京都渋谷区恵比寿'}}],
          'ticketInfoList': [
              {'name': '一般販売', 'release': '2026-11-01T00:00:00.000Z', 'startApply': '2026-11-10T11:00:00.000Z',
               'endApply': '2026-12-02T14:59:59.999Z', 'status': 'applied',
               'ticketTypes': [{'name': 'A', 'stageIds': ['S1'], 'remainingRate': 1, 'status': 'applied'}]},
              {'name': '一般販売2', 'release': '2026-11-01T00:00:00.000Z', 'startApply': '2026-11-20T03:00:00.000Z',
               'endApply': '2026-12-10T14:59:00.000Z', 'status': 'coming',
               'ticketTypes': [{'name': 'A', 'stageIds': ['S1'], 'remainingRate': 1, 'status': 'coming'}]},
              {'name': 'VIP', 'release': '2026-11-01T00:00:00.000Z', 'startApply': '2026-11-01T03:00:00.000Z',
               'endApply': '2026-12-01T14:59:00.000Z', 'status': 'closed',
               'ticketTypes': [{'name': 'V', 'stageIds': ['S1'], 'remainingRate': 0, 'status': 'closed'}]}]}
    good = {'name': 'テスト', 'date': '2026-12-03', 'venue': '恵比寿CreAto', 'prefecture': '東京', 'tickets': [
        {'type': '一般販売（東京 12/3公演）〜12/2 23:59', 'date': '2026-12-02', 'url': 'https://ticketdive.com/event/x'},
        {'type': '一般販売2（東京 12/3公演）11/20 12:00発売', 'date': '2026-12-03', 'startDate': '2026-11-20',
         'url': 'https://ticketdive.com/event/x'},
        {'type': 'VIP（東京 12/3公演）〜12/1 23:59', 'date': '2026-12-01', 'soldout': True,
         'url': 'https://ticketdive.com/event/x'}]}
    ng, unk = check_entry(good, ed, today, now)
    assert not ng and not unk, ng
    # 組み立てがずれたら鳴る：締切・売り切れの印・発売前の startDate・カードの日付・県
    for bad, why in (
            (dict(good, tickets=[dict(good['tickets'][0], type='一般販売（東京 12/3公演）〜12/3', date='2026-12-03')] + good['tickets'][1:]), '締切'),
            (dict(good, tickets=good['tickets'][:2] + [dict(good['tickets'][2], soldout=False)]), '売り切れ'),
            (dict(good, tickets=[good['tickets'][0], dict(good['tickets'][1], startDate='2026-11-21')] + good['tickets'][2:]), '発売日'),
            (dict(good, date='2026-12-04'), 'カードの日付'),
            (dict(good, prefecture='大阪'), '県'),
            (dict(good, tickets=good['tickets'][:2]), '枠が足りない')):
        assert check_entry(bad, ed, today, now)[0], why
    # 分からない状態（受付期間の内・残りあり・closed）は数えるだけ
    ed2 = json.loads(json.dumps(ed))
    ed2['ticketInfoList'][0]['status'] = 'closed'
    ed2['ticketInfoList'][0]['ticketTypes'][0]['status'] = 'closed'
    ng2, unk2 = check_entry(dict(good, tickets=good['tickets'][1:]), ed2, today, now)
    assert not ng2 and len(unk2) == 1, (ng2, unk2)
    assert badge_key({'type': '先行（R9年 1/5公演）〜12/20 23:59', 'date': '2026-12-20'})[1] == '1/5'
    assert BADGE_RE.match('先行（R9年 1/5公演）〜12/20 23:59').group('pref') is None
    assert BADGE_RE.match('先行（大阪 R9年 1/5公演）〜12/20 23:59').group('pref') == '大阪'
    print('selftest OK: HTML の __NEXT_DATA__ から別の書き方で枠を作る/締切・売り切れ・発売日・カードの日付・県のずれで鳴る')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ids', default='')
    ap.add_argument('--built', default='', help='投入前の組み上がり（build_ticketdive_entries の出力）を照合する')
    ap.add_argument('--today', default=(datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) + JST9).date().isoformat())
    ap.add_argument('--sleep', type=float, default=3.0)
    ap.add_argument('--report', default=REPORT)
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        _selftest()
        sys.exit(0)
    now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) + JST9
    if a.built:
        ents = json.load(io.open(a.built, encoding='utf-8'))['entries']
        targets = [(e, i) for i, e in enumerate(ents)]
    else:
        h = io.open('index.html', encoding='utf-8', newline='').read()
        ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))
        want = {int(x) for x in re.findall(r'\d+', a.ids)} if a.ids else None
        targets = [(e, e['id']) for e in ev
                   if 'ticketdive.com/event/' in json.dumps(e.get('links') or {}) + json.dumps(e.get('tickets') or [])
                   and (not want or e['id'] in want)]
    ok, ng, err, unk_all = 0, [], [], []
    for e, key in targets:
        urls = sorted({u for t in (e.get('tickets') or []) + [{'url': (e.get('links') or {}).get('ticketdive')}]
                       for u in re.findall(r'ticketdive\.com/event/([A-Za-z0-9_\-.%]+)', t.get('url') or '')})
        if len(urls) != 1:
            ng.append((e, key, ['TicketDive の公演ページが %d 個（1公演1カードのはず）: %s' % (len(urls), urls)]))
            continue
        try:
            ed = load_page(urls[0], a.sleep)
        except Exception as ex:
            err.append((e, key, urls[0], str(ex)[:80]))
            continue
        msgs, unk = check_entry(e, ed, a.today, now)
        if unk:
            unk_all.append((e, key, unk))
        if msgs:
            ng.append((e, key, msgs))
        else:
            ok += 1
    rep = io.open(a.report, 'w', encoding='utf-8')
    rep.write('=== gate_ticketdive_slots (today=%s) %s 対象%d件 ===\n' % (a.today, a.built or 'index.html', len(targets)))
    for e, key, msgs in ng:
        rep.write('\n🚨 id=%s %s\n    %s\n' % (key, (e.get('name') or '')[:40], (e.get('links') or {}).get('ticketdive')))
        for m in msgs:
            rep.write('    %s\n' % m)
    for e, key, unk in unk_all:
        rep.write('\nℹ️ 状態が分からない受付（組み立ては載せていない） id=%s %s\n' % (key, (e.get('name') or '')[:40]))
        for m in unk:
            rep.write('    %s\n' % m)
    for e, key, u, why in err:
        rep.write('❌ id=%s event/%s 読めなかった: %s\n' % (key, u, why))
    rep.write('\n=== 集計: 一致 %d / 🚨食い違い %d / ❌読めなかった %d / ℹ️分からない受付があるカード %d ===\n'
              % (ok, len(ng), len(err), len(unk_all)))
    rep.close()
    sys.stderr.write('gate_ticketdive_slots: match=%d ng=%d fetcherr=%d unknown=%d -> %s\n'
                     % (ok, len(ng), len(err), len(unk_all), a.report))
    sys.exit(2 if (ng or err) else 0)


if __name__ == '__main__':
    main()
