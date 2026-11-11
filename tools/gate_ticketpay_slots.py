# -*- coding: utf-8 -*-
"""チケットペイ由来の枠の機械ゲート＝**実ページから枠をゼロから作り直して突合**＋**組み立てを通さない生の突合**（2026-11-12 新設）。

  python tools/gate_ticketpay_slots.py                              … index.html のチケットペイ枠を全部照合
  python tools/gate_ticketpay_slots.py --ids 1,2                    … id 指定
  python tools/gate_ticketpay_slots.py --built tmp/built_ticketpay_MMDD.json   … 投入前の組み上がりを照合
  python tools/gate_ticketpay_slots.py --selftest

終了コード 0＝全一致 / 2＝食い違いあり（投入・push の前に必ず 0 を確認する）

## 見るもの（gate_tiget_slots.py と同じ考え方）
1. **作り直し突合**：実ページ → ticketpay_harvest.parse_event → build_ticketpay_entries.build で作った枠と、
   登録（または組み上がり）の枠が（券種名＋公演日＋締切・発売日・売切/販売終了の印）で全部一致するか
2. 🚨**生の突合（組み立てを通さない）**＝ビルダーと同じ間違いをして一致するのを防ぐ（ZAIKO スタリオンの学び）。
   ページの**画面の文字だけ**から別の書き方で読み直して比べる：
   - 札（受付期間中／受付前／完売／受付終了）と枠の印（買える／発売前／soldout／saleEnded）が合っているか
   - 「開催日 : YYYY/MM/DD」の最後の日 ＝ カードの date
   - 「販売期間 : … ～ YYYY/MM/DD HH:MM」の終わり ＝ 買える・発売前の枠の date（公演日で締めた時は公演日）
   - 受付前の枠の startDate ＝ 販売期間の始まり
   - 券種の見出し（`<h2>… 円</h2>`）の数 ＝ 枠の数（券種があるページ）
   - 「完売」の印が付いた券種の数 ＝ soldout の枠の数（ページが受付期間中のとき）
3. 組めなかった（公演が終わった等）のに、ページが受付期間中・受付前で締切が今日以降なら鳴らす（「組めない＝終わった」と決めつけない）
"""
import argparse
import datetime
import html as H
import importlib.util
import io
import json
import re
import sys
import time

_KEEP = []


def _load(path, name):
    prev = sys.stdout
    _KEEP.append(prev)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _KEEP.append(sys.stdout)
    sys.stdout = prev
    return mod


TH = _load('tools/ticketpay_harvest.py', 'tph')
BT = _load('tools/build_ticketpay_entries.py', 'tpb')
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
URL_ID = re.compile(r'ticketpay\.jp/booking/\?event_id=(\d+)')


def visible(t):
    t = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', t, flags=re.S)
    t = re.sub(r'<div id="event_txt_cont">.*?</div>', ' ', t, flags=re.S)   # 説明文は主催者の自由文＝見ない
    t = re.sub(r'<select.*?</select>', ' ', t, flags=re.S)
    return re.sub(r'\s+', ' ', H.unescape(re.sub(r'<[^>]+>', ' ', t)))


def _d(y, m, d):
    return '%04d-%02d-%02d' % (int(y), int(m), int(d))


def raw_facts(t):
    """画面の文字だけから読む（parse_event を使わない別の読み方）。"""
    v = visible(t)
    f = {}
    # 札＝公演名の右の箱（event_rightbox）の文字だけ（公演名に「完売しました」と書く主催者がいる＝65300）
    rb = re.search(r'id="event_rightbox">(.*?)</div>', t, re.S)
    rbt = visible(rb.group(1)) if rb else ''
    m = re.search(r'(受付期間中|受付前|完売|受付終了)', rbt)
    f['mark'] = m.group(1) if m else (None if not rbt.strip() else 'その他:' + rbt.strip()[:10])
    m = re.search(r'開催日 :\s*([\d/ ()月火水木金土日～〜]+)', v)
    f['show_last'] = max([_d(*x) for x in re.findall(r'(\d{4})/(\d{2})/(\d{2})', m.group(1))]) if m else None
    m = re.search(r'販売期間 :\s*(?:(\d{4})/(\d{2})/(\d{2}) \(.\) (\d{1,2}):(\d{2}))?\s*～\s*(?:(\d{4})/(\d{2})/(\d{2}) \(.\) (\d{1,2}):(\d{2}))?', v)
    f['sale_start'] = _d(*m.group(1, 2, 3)) if m and m.group(1) else None
    f['sale_end'] = _d(*m.group(6, 7, 8)) if m and m.group(6) else None
    tb = re.search(r'<div id="ticket_type_select_\d+">(.*?)(?:<div class="reservation">|<!-- \.reservation_line -->)', t, re.S)
    # 券種ごとの区切り＝<h2> から次の <h2> まで。完売の印は h2 の中ではなく直後の
    #   <… class="info_sold_out_mini">完売</…> に出る（2026-11-12 試運転で番人のほうが見落とした）
    segs = re.split(r'(?=<h2>)', tb.group(1))[1:] if tb else []
    f['n_types'] = len(segs)
    # 券種の説明（class="input_ex"）は主催者の自由文＝「完売次第終了」を拾わないよう外して読む
    f['n_types_sold'] = sum(1 for x in segs if re.search(r'完売(?!次第)|売切|売り切れ',
                                                     visible(re.sub(r'<p class="input_ex[^"]*">.*?</p>', ' ', x, flags=re.S))))
    return f


def raw_check(f, entry_date, slots, today):
    """生の突合。返り値＝食い違いの説明のリスト。"""
    out = []
    if not slots:
        return out
    sold = [s for s in slots if s.get('soldout')]
    ended = [s for s in slots if s.get('saleEnded')]
    pre = [s for s in slots if s.get('startDate') and not s.get('soldout')]
    if f['mark'] == '完売' and len(sold) != len(slots):
        out.append('ページは「完売」なのに soldout でない枠がある')
    if f['mark'] == '受付終了' and len(ended) != len(slots):
        out.append('ページは「受付終了」なのに saleEnded でない枠がある')
    if f['mark'] == '受付前' and len(pre) != len(slots):
        out.append('ページは「受付前」なのに発売日の無い枠・印の付いた枠がある')
    if f['mark'] == '受付期間中' and pre:
        out.append('ページは「受付期間中」なのに発売前の枠がある')
    if f['mark'] == '受付期間中' and f['sale_end'] and f['sale_end'] >= today and len(ended) > 0:
        out.append('ページは「受付期間中」で販売期間内なのに販売終了の枠がある')
    if f['mark'] == '受付期間中' and f['sale_end'] and f['sale_end'] < today and len(ended) != len(slots):
        out.append('販売期間の終わり %s が過ぎたのに販売終了でない枠がある' % f['sale_end'])
    if f['mark'] is None:
        out.append('ページの札が読めない')
    if f['show_last'] and entry_date != f['show_last']:
        out.append('カードの日付 %s ≠ ページの開催日 %s' % (entry_date, f['show_last']))
    for s in slots:
        if s.get('soldout') or s.get('saleEnded'):
            continue
        want = f['sale_end'] or f['show_last']
        if want and f['show_last'] and want > f['show_last'] and not BT.STREAM.search(s.get('type') or ''):
            want = f['show_last']
        if want and s.get('date') != want:
            out.append('枠の締切 %s ≠ ページの販売期間の終わり %s：%s' % (s.get('date'), want, s.get('type')))
        if s.get('startDate') and f['sale_start'] and s['startDate'] != f['sale_start']:
            out.append('枠の発売日 %s ≠ ページの販売期間の始まり %s' % (s['startDate'], f['sale_start']))
    if f['n_types'] and f['n_types'] != len(slots):
        out.append('券種 %d個 ≠ 枠 %d個' % (f['n_types'], len(slots)))
    if f['mark'] == '受付期間中' and f['n_types'] and f['n_types_sold'] != len(sold):
        out.append('完売の券種 %d個 ≠ soldout の枠 %d個' % (f['n_types_sold'], len(sold)))
    return out


def key(t):
    return (t.get('type'), t.get('date'), t.get('startDate'), bool(t.get('soldout')), bool(t.get('saleEnded')))


LIST_MARK = {'完売': '完売', '受付終了': '受付終了'}


def list_mark(li):
    """一覧の札（販売中(…まで)／受付前(…から)／完売／受付終了）を、ページの札の言葉に直す。"""
    s = (li or {}).get('list_status') or ''
    if s.startswith('販売中'):
        return '受付期間中'
    if s.startswith('受付前'):
        return '受付前'
    return LIST_MARK.get(s)


def check_one(eid, reg_slots, entry_date, today, cats=None, li=None):
    """1ページを読んで（作り直しの食い違い, 生の突合の食い違い, 作り直しの枠）を返す。
    li＝カテゴリ一覧のその番号の行（ページに札が無い型のため）。"""
    t, final = TH.fetch('%s/booking/?event_id=%s' % (TH.BASE, eid))
    if 'event_id=%s' % eid not in final:
        raise ValueError('トップへ飛んだ（非公開・削除）')
    d = TH.parse_event(t, eid)
    d['cats'] = cats or (li or {}).get('cats') or []
    d['list_status'] = (li or {}).get('list_status') or ''
    d['list_class'] = (li or {}).get('list_class') or ''
    built, why = BT.build(d, today)
    rebuilt = built['tickets'] if built else []
    rk, gk = {key(x) for x in reg_slots}, {key(x) for x in rebuilt}
    diff = (sorted(rk - gk, key=str), sorted(gk - rk, key=str)) if rk != gk else None
    f = raw_facts(t)
    if f['mark'] is None:
        f['mark'] = list_mark(li)          # ページに札が無い型＝一覧の札（ビルダーとは別に読み直した文字）
    rc = raw_check(f, entry_date, reg_slots, today)
    if not built and f['mark'] in ('受付期間中', '受付前') and (f['sale_end'] or f['show_last'] or '') >= today:
        rc.append('組み立てで捨てられた（%s）が、ページは%sで締切が今日以降' % (why, f['mark']))
    return diff, rc, rebuilt, built


def _selftest():
    page = ('<span class="event_name">【完売しました】X</span><div id="event_rightbox"><label class="event_mark_1">受付期間中</label></div> 会場 : X '
            '<p class="event_c"><label class="label_l en">開催日</label><span> : 2026/12/03 (木) </span></p>'
            '<div id="sales_period"><label class="label_m en">販売期間</label><span>: 2026/10/27 (火) 14:00 <br>～ 2026/11/30 (月) 23:59</span>'
            '</div><!-- #sales_period --><div id="ticket_type_select_1"><h2>A 8,000円</h2><select></select><h2>B 9,000円</h2><p class="info_sold_out_mini">完売</p>'
            '</div><div class="reservation">')
    f = raw_facts(page)
    assert f == {'mark': '受付期間中', 'show_last': '2026-12-03', 'sale_start': '2026-10-27', 'sale_end': '2026-11-30',
                 'n_types': 2, 'n_types_sold': 1}, f
    ok = [{'type': 'A（12/3公演）〜11/30 23:59', 'date': '2026-11-30'},
          {'type': 'B（12/3公演）〜11/30 23:59', 'date': '2026-11-30', 'soldout': True}]
    assert raw_check(f, '2026-12-03', ok, '2026-11-12') == []
    # 締切ずれ・カード日付ずれ・完売の取りこぼし・枠の数の取りこぼし は鳴る
    assert raw_check(f, '2026-12-03', [dict(ok[0], date='2026-12-03'), ok[1]], '2026-11-12')
    assert raw_check(f, '2026-11-30', ok, '2026-11-12')
    assert raw_check(f, '2026-12-03', [ok[0], dict(ok[1], soldout=False)], '2026-11-12')
    assert raw_check(f, '2026-12-03', [ok[0]], '2026-11-12')
    # 受付前なのに発売日なし・受付終了なのに saleEnded なし は鳴る
    f2 = dict(f, mark='受付前', n_types=0)
    assert raw_check(f2, '2026-12-03', [{'type': 'x', 'date': '2026-11-30'}], '2026-11-12')
    assert not raw_check(f2, '2026-12-03', [{'type': 'x', 'date': '2026-11-30', 'startDate': '2026-10-27'}], '2026-11-12')
    f3 = dict(f, mark='受付終了', n_types=0)
    assert raw_check(f3, '2026-12-03', [{'type': 'x', 'date': '2026-11-30', 'soldout': True}], '2026-11-12')
    # 販売期間が過ぎたのに受付中の枠＝鳴る／販売終了にした枠＝鳴らない
    f4 = dict(f, sale_end='2026-11-11', n_types=0)
    assert raw_check(f4, '2026-12-03', [{'type': 'x', 'date': '2026-11-11'}], '2026-11-12')
    assert not raw_check(f4, '2026-12-03', [{'type': 'x', 'date': '2026-11-11', 'soldout': True, 'saleEnded': True}], '2026-11-12')
    # 札がページに無い型は一覧の札で読む
    assert list_mark({'list_status': '販売中(2026/11/30 (月) 23:59まで)'}) == '受付期間中'
    assert list_mark({'list_status': '受付終了'}) == '受付終了' and list_mark({}) is None
    print('selftest OK（生の突合：札・カードの日付・締切・発売日・券種の数・完売の数・期間切れ・一覧の札）')
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ids', default='')
    ap.add_argument('--built', default='', help='投入前の組み上がり（build_ticketpay_entries の出力）を照合する')
    ap.add_argument('--today', default=datetime.date.today().isoformat())
    ap.add_argument('--sleep', type=float, default=3.0, help='1ページごとの間（秒）')
    ap.add_argument('--report', default='tmp/gate_ticketpay_report.txt')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        sys.exit(_selftest())

    targets = []    # (表示用id, event_id, 枠, カードの日付, cats, 名前)
    if a.built:
        src = json.load(open(a.built, encoding='utf-8'))
        for e in src['entries']:
            eid = URL_ID.search(e['links']['ticketpay']).group(1)
            cats = (e.get('_srcgenre') or '').split(':', 1)[-1].split(',')
            targets.append(('tp%s' % eid, eid, e['tickets'], e['date'], [c for c in cats if c], e['name']))
    else:
        h = open('index.html', encoding='utf-8', newline='').read()
        ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))
        want = {int(x) for x in re.findall(r'\d+', a.ids)} if a.ids else None
        for e in ev:
            if want and e['id'] not in want:
                continue
            urls = sorted({x for t in (e.get('tickets') or []) + [{'url': (e.get('links') or {}).get('ticketpay')}]
                           for x in URL_ID.findall(t.get('url') or '')})
            for eid in urls:
                reg = [t for t in e.get('tickets') or [] if ('event_id=%s' % eid) in (t.get('url') or '')]
                # 複数のチケットペイページを持つカードはカードの日付を照合しない（ページごとの公演日と比べられない）
                targets.append((e['id'], eid, reg, e['date'] if len(urls) == 1 else None, [], e.get('name')))

    lists, _ = TH.harvest_lists(a.sleep) if targets else ({}, {})     # ページに札が無い型のため（9回だけ読む）
    rep = io.open(a.report, 'w', encoding='utf-8')
    rep.write('=== gate_ticketpay_slots (today=%s) 対象%d件 %s ===\n' % (a.today, len(targets), a.built or 'index.html'))
    ok, ng, rawng, err = 0, [], [], []
    for tid, eid, reg, edate, cats, name in targets:
        try:
            diff, rc, rebuilt, built = check_one(eid, reg, edate, a.today, cats, lists.get(int(eid)))
        except Exception as ex:
            err.append((tid, eid, str(ex)[:80]))
            time.sleep(a.sleep)
            continue
        if edate is None:
            rc = [x for x in rc if not x.startswith('カードの日付')]
        if diff:
            ng.append((tid, eid, name, diff))
        if rc:
            rawng.append((tid, eid, name, rc))
        if not diff and not rc:
            ok += 1
        time.sleep(a.sleep)
    for tid, eid, name, (only_reg, only_page) in ng:
        rep.write('\n🚨 %s event_id=%s %s\n' % (tid, eid, (name or '')[:40]))
        for k in only_reg:
            rep.write('    登録にだけある: %s\n' % (k,))
        for k in only_page:
            rep.write('    実ページにだけある: %s\n' % (k,))
    for tid, eid, name, rc in rawng:
        rep.write('\n🚨生の突合（組み立てを通さない） %s event_id=%s %s\n' % (tid, eid, (name or '')[:40]))
        for m in rc:
            rep.write('    %s\n' % m)
    for tid, eid, why in err:
        rep.write('❌ %s event_id=%s 読めなかった: %s\n' % (tid, eid, why))
    rep.write('\n=== 集計: 一致 %d / 🚨作り直し食い違い %d / 🚨生の突合 %d / ❌読めなかった %d ===\n'
              % (ok, len(ng), len(rawng), len(err)))
    rep.close()
    sys.stderr.write('gate_ticketpay_slots: match=%d ng=%d rawng=%d fetcherr=%d -> %s\n'
                     % (ok, len(ng), len(rawng), len(err), a.report))
    sys.exit(2 if (ng or rawng or err) else 0)


if __name__ == '__main__':
    main()
