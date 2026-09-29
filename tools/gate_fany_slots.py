# -*- coding: utf-8 -*-
"""FANYの登録枠を、売り場のデータから**ゼロから作り直して**全件突合する番人。

  python tools/gate_fany_slots.py                      … 今の一覧を引き直して突合
  python tools/gate_fany_slots.py --src tmp/fany_MMDD.json   … 既に引いた一覧で突合（速い）
  python tools/gate_fany_slots.py --ids 17600,17601    … その id だけ
  python tools/gate_fany_slots.py --selftest

終了コード＝**0:一致／1:食い違いあり／2:引けなかった**（1以上なら投入・pushの前に直す）。

## なぜ要るか
TIGETと同じで、FANYも**毎日ずれる**（当日券が足される・先行が終わって印が変わる・締切が延びる）。
ぴあのヒールはFANYを見ないし、`check_zero_badge` は「枠0」しか見ない。
＝**この番人が無いと、登録した表示値がページとズレても誰も気づかない**
（[[project_rakuten_make_it_ironclad]] と同じ理屈）。

## 見方
- `只ページ側にある`＝売り場に増えた枠（当日券・追加販売）→ 取り直して足す
- `只登録側にある`＝売り場から消えた枠。**売り切れ・先行終了の印つきなら残す**
  （[[feedback_soldout_keep_visible]]）。印なしで消えているなら取り直す
- 一覧から落ちたイベントは**「消えた」とも「終わった＝正常」とも決めつけない**
  🆕2026-09-30 ZAIKOのスタリオン（配信中なのに「公演日が過ぎた＝正常」と読んで見逃した）を受けて、
  一覧の生データ→無ければ**詳細ページの「受付」欄**を読み、受付中・受付前で締切が今日以降の受付があれば
  🚨生データ突合の食い違いとして鳴らす（exit 1）。詳細も読めない分は「判定不能」に分ける。
  ⚠️一覧（search）は公演日が今日以降しか返さない＝過ぎた公演の配信は一覧には出てこない（2026-09-30 実測）
"""
import argparse
import collections
import datetime
import io
import json
import re
import sys
import time

sys.path.insert(0, 'tools')
import build_fany_entries as BF          # noqa: E402
import fany_harvest as FH                # noqa: E402

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

REPORT = 'tmp/gate_fany_report.txt'


def key(t):
    """比べる骨格＝券種名つきバッジ・締切・印の3点（url は比べない＝申込idは変わりうる）。"""
    return (t.get('type'), t.get('date'), bool(t.get('soldout')),
            bool(t.get('saleEnded')), bool(t.get('presaleEnded')))


def load_registered(ids=None):
    h = open('index.html', encoding='utf-8', newline='').read()
    ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))
    out = {}
    for e in ev:
        fid = re.search(r'/event/detail/(\d+)', (e.get('links') or {}).get('fany') or '')
        if not fid:
            continue
        if ids and e['id'] not in ids:
            continue
        out.setdefault(fid.group(1), []).append(e)
    return out


def raw_stream_check(fany_slots, perfs):
    """🆕2026-09-28 **ビルダーを通さない**突合（ZAIKOのスタリオンで、番人がビルダーと同じ間違いをして一致した）。
    売り場の元の券種名に「配信・視聴・アーカイブ」があり、受付中／発売前で締切があるなら、
    登録に「配信/視聴/アーカイブ」を含み date＝その締切の枠があるか。返り値＝食い違いの説明のリスト。"""
    out = []
    for p in perfs:
        for s in p.get('performance_sales') or []:
            nm = s.get('sales_name') or ''
            st = (s.get('display_sales_status') or '').strip()
            if not re.search(BF.STREAM_RE, nm) or st not in BF.PRE_ST + BF.LIVE_ST:
                continue
            ed = BF.raw_dt(s.get('sales_end_datetime_raw'))[0]
            if not ed:
                continue
            if not any(t.get('date') == ed and re.search(BF.STREAM_RE, t.get('type') or '')
                       for t in fany_slots):
                out.append('配信の券種「%s」（〜%s）が、登録に「配信」付き・締切%sで無い' % (nm[:20], ed, ed))
    return out


def raw_live_sales(perfs, today):
    """🆕2026-09-30 一覧の生データ（ビルダーを通さない）で「いま買える／これから買える」販売枠。
    先着発売中・抽選受付中は締切が今日以降（締切が無ければ公演日が今日以降）、
    発売前は締切か発売日が今日以降。"""
    out = []
    for p in perfs:
        d = BF.perf_end_iso(p) or BF.perf_date_iso(p) or ''
        for s in p.get('performance_sales') or []:
            st = (s.get('display_sales_status') or '').strip()
            nm = s.get('sales_name') or ''
            if st not in BF.LIVE_ST + BF.PRE_ST or BF.SELLER_SIDE.search(nm):
                continue
            ed = BF.raw_dt(s.get('sales_end_datetime_raw'))[0]
            sd = BF.raw_dt(s.get('sales_start_datetime_raw'))[0]
            if (ed and ed >= today) or (not ed and ((st in BF.PRE_ST and sd and sd >= today) or d >= today)):
                out.append('%s（%s・〜%s）' % ((nm or 'チケット')[:20], st, ed or '締切なし'))
    return out


LIVE_BTN = ('受付中', '受付前')
_DT = re.compile(r'(\d{4})/(\d{2})/(\d{2})')


def detail_receptions(html):
    """🆕2026-09-30 詳細ページ /event/detail/<id> の「受付」欄を読む（ビルダーも一覧も通さない生データ）。
    返り値＝[{'name', 'period', 'end'(iso or None＝「開演2時間前」のような相対の締切), 'btn'}]。
    2026-09-30 実測＝ボタンの文言は 受付中／受付前／受付終了 の3つ（受付前も disabled の札が付くので文言で見る）。"""
    m = re.search(r'<!--受付-->(.*?)<!--/受付-->', html or '', re.S)
    out = []
    if not m:
        return out
    for li in re.findall(r'<li>(.*?)</li>', m.group(1), re.S):
        nm = re.search(r'<p>\s*(?:<span class="g-tag">[^<]*</span>)?(.*?)</p>', li, re.S)
        per = re.search(r'受付期間：</span>(.*?)</div>', li, re.S)
        btn = re.search(r'<p class="g-ticketInfo_btn[^"]*"[^>]*>(.*?)<', li, re.S)
        ptxt = re.sub(r'\s+', ' ', per.group(1)).strip() if per else ''
        right = re.split(r'[～〜]', ptxt, maxsplit=1)[1] if re.search(r'[～〜]', ptxt) else ''
        dm = _DT.search(right)
        out.append({'name': BF.strip_tags(nm.group(1)) if nm else '', 'period': ptxt,
                    'end': '%s-%s-%s' % dm.groups() if dm else None,
                    'btn': BF.strip_tags(btn.group(1)) if btn else ''})
    return out


def live_detail(recs, today):
    """詳細ページの受付で「いま買える／これから買える」もの。
    受付中・受付前で、締切が今日以降か、締切が相対（開演2時間前など）で日付が書いていないもの。"""
    return ['%s（%s・%s）' % (r['name'][:20], r['btn'], r['period'][:40]) for r in recs
            if r['btn'] in LIVE_BTN and not BF.SELLER_SIDE.search(r['name'])
            and (r['end'] is None or r['end'] >= today)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', default=None, help='引いてある一覧JSON（無ければ引き直す）')
    ap.add_argument('--ids', default='')
    ap.add_argument('--days', type=int, default=200, help='引き直すときの先の日数')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        return _selftest()

    today = datetime.date.today().isoformat()
    ids = {int(x) for x in re.findall(r'\d+', a.ids)} or None
    reg = load_registered(ids)
    if not reg:
        print('FANYの登録が無い（links.fany を持つエントリ0件）')
        return 0

    if a.src:
        data = json.load(open(a.src, encoding='utf-8'))
    else:
        tmp = 'tmp/fany_gate_%s.json' % datetime.date.today().strftime('%m%d')
        to = (datetime.date.today() + datetime.timedelta(days=a.days)).isoformat()
        if FH.harvest(today, to, tmp, with_genre=False) != 0:
            print('🚨一覧が引けなかった＝突合できない（「一致」と言ってはいけない）')
            return 2
        data = json.load(open(tmp, encoding='utf-8'))

    # 売り場のデータからゼロから組み直す（登録値は見ない）
    gmap = dict(data.get('genre_map') or {})
    same = collections.Counter()
    for p in data['performances']:
        iso = BF.perf_date_iso(p)
        if iso:
            same[(p.get('event_id'), iso, p.get('venue_id'))] += 1
    gmap['_same_day'] = same
    page = collections.defaultdict(list)
    perfs = collections.defaultdict(list)
    for p in data['performances']:
        perfs[str(p.get('event_id'))].append(p)
        e, _ = BF.build_one(p, today, gmap, collections.Counter())
        if e:
            page[str(p.get('event_id'))] += e['tickets']

    ng, ok, gone, linkonly, rawng, nodetail, outrange = [], 0, [], [], [], [], []
    rng_to = (data.get('range') or {}).get('to')
    for fid, entries in sorted(reg.items()):
        # 🚨「links.fany を足しただけ」のエントリ（枠はぴあ等で持っている）は突合対象外。
        #    ここを外さないと、売り場が違って当然の締切の差を全部「食い違い」として鳴らす
        #    （2026-09-21＝51件にリンクを足したら58件が鳴った）。
        #    ただし数は出す＝**FANYの枠を足し込めば買える枠が増える候補**なので見失わない。
        fany_slots = [t for e in entries for t in (e.get('tickets') or [])
                      if 'ticket.fany.lol' in (t.get('url') or '')]
        if not fany_slots:
            linkonly.append((fid, entries, len(page.get(fid, []))))
            continue
        rc = raw_stream_check(fany_slots, perfs.get(fid, []))
        if rc:
            rawng.append((fid, entries, rc))
        rk = {key(t) for t in fany_slots}
        gk = {key(t) for t in page.get(fid, [])}
        if fid not in page and rng_to and not perfs.get(fid) and all(
                (e.get('date') or '') > rng_to for e in entries):
            # 🆕2026-09-30 一覧を取った期間（--to）より先の公演は、一覧に無くて当たり前＝「落ちた」ではない
            #   （20925 佐久間一行 岡山 R9年4/4＝--to 3/31 の外で鳴った）。照合していないことは数で出す。
            outrange.append((fid, entries))
            continue
        if fid not in page:
            # 🚨2026-09-30 「組めない＝一覧から落ちた＝公演日が過ぎて正常」と決めつけない
            #   （ZAIKOのスタリオン＝配信中なのに正常扱いで見逃した）。一覧は公演日が今日以降しか返さない
            #   （2026-09-30 実測＝from に過去日を入れると0件）＝過ぎた公演の配信は一覧に出てこない。
            #   ①一覧の生データ ②詳細ページの「受付」欄 に、まだ買える受付があれば食い違いとして鳴らす。
            alive = raw_live_sales(perfs.get(fid, []), today)
            if not alive:
                html = FH.fetch(FH.BASE + '/event/detail/%s' % fid, tries=2)
                time.sleep(0.5)
                if html is None or '<!--受付-->' not in html:
                    nodetail.append((fid, entries))   # 読めない＝判定不能（「終わった」ではない）
                    continue
                alive = live_detail(detail_receptions(html), today)
            if alive:
                rawng.append((fid, entries, ['組み立てで捨てられた（一覧から落ちた）が、売り場ではまだ買える受付がある：%s'
                                             % ' / '.join(alive)]))
                continue
            gone.append((fid, entries))
            continue
        if rk == gk:
            ok += 1
            continue
        ng.append((fid, entries, sorted(rk - gk), sorted(gk - rk)))

    rep = io.open(REPORT, 'w', encoding='utf-8')
    rep.write('=== gate_fany_slots (today=%s) 対象%dイベント ===\n' % (today, len(reg)))
    rep.write('一致 %d / 食い違い %d / 一覧から落ちた %d / 詳細が読めず判定不能 %d / リンクだけ足した分 %d\n\n'
              % (ok, len(ng), len(gone), len(nodetail), len(linkonly)))
    for fid, entries, only_reg, only_page in ng:
        e = entries[0]
        rep.write('--- event/detail/%s  id%s %s @ %s\n'
                  % (fid, ','.join(str(x['id']) for x in entries),
                     (e.get('name') or '')[:40], (e.get('venue') or '')[:20]))
        for k in only_reg:
            rep.write('    只登録側: %s | %s | soldout=%s saleEnded=%s presaleEnded=%s\n' % k)
        for k in only_page:
            rep.write('    只ページ側: %s | %s | soldout=%s saleEnded=%s presaleEnded=%s\n' % k)
    rep.write('\n=== 🚨生データ突合（ビルダーを通さない・配信の券種）の食い違い %d件 ===\n' % len(rawng))
    for fid, entries, rc in rawng:
        rep.write('--- event/detail/%s  id%s %s\n' % (fid, ','.join(str(x['id']) for x in entries),
                                                     (entries[0].get('name') or '')[:40]))
        for m in rc:
            rep.write('    %s\n' % m)
    rep.write('\n=== 一覧から落ちたイベント（詳細ページの受付も全部 受付終了＝公演終了）===\n')
    for fid, entries in gone:
        for e in entries:
            rep.write('  id%-6s 公演%s %s\n' % (e['id'], e.get('date'), (e.get('name') or '')[:40]))
    rep.write('\n=== 一覧から落ちて詳細ページも読めず判定できなかった（「終わった」とは言えない）===\n')
    for fid, entries in nodetail:
        rep.write('  event/detail/%s  id%s\n' % (fid, ','.join(str(x['id']) for x in entries)))
    rep.write('\n=== 一覧を取った期間（〜%s）より先の公演＝今回は照合していない %d件 ===\n' % (rng_to, len(outrange)))
    for fid, entries in outrange:
        rep.write('  event/detail/%s  id%s 公演%s\n' % (fid, ','.join(str(x['id']) for x in entries),
                                                     entries[0].get('date')))
    rep.write('\n=== リンクだけ足した分（FANYの枠を足し込めば買える枠が増える候補）===\n')
    for fid, entries, n in linkonly:
        e = entries[0]
        rep.write('  id%-6s FANYに%2d枠 / 公演%s %s @ %s\n'
                  % (e['id'], n, e.get('date'), (e.get('name') or '')[:34],
                     (e.get('venue') or '')[:18]))
    rep.close()
    print('gate_fany_slots: 一致%d / 食い違い%d / 🚨生データ突合%d / 一覧落ち%d / 判定不能%d / リンクだけ%d / 期間外(未照合)%d → %s'
          % (ok, len(ng), len(rawng), len(gone), len(nodetail), len(linkonly), len(outrange), REPORT))
    return 1 if (ng or rawng) else 0


def _selftest():
    t1 = {'type': '一般発売（大阪 10/1公演）〜9/30 8:00', 'date': '2026-09-30',
          'url': 'https://x/reception/1/2'}
    t2 = dict(t1, url='https://x/reception/9/9')
    assert key(t1) == key(t2), 'url が違っても同じ枠と見る'
    t3 = dict(t1, soldout=True, presaleEnded=True)
    assert key(t1) != key(t3), '印が付いたら別の枠と見る'
    # 🆕2026-09-30 スタリオン型＝公演日は過去・配信券の締切は未来
    today = '2026-09-30'

    def sale(st, nm, s1, s0='20260920100000'):
        return {'display_sales_status': st, 'sales_name': nm, 'prefecture_code': '13',
                'sales_start_datetime_raw': s0, 'sales_end_datetime_raw': s1,
                'destination_url': 'https://x/reception/5/2'}
    perf = {'id': 1, 'event_id': 99, 'venue_id': 7, 'class': '01', 'name': 'スタリオン型',
            'venue_name': 'ルミネtheよしもと（東京都）', 'performance_date': '2026/09/28(<span>月</span>)',
            'start_time': '220000', 'performance_sales': [sale('先着発売中', '配信視聴チケット', '20261005235900')]}
    assert raw_live_sales([perf], today), '配信中の販売枠を買えると読む'
    e, why = BF.build_one(perf, today, {'_same_day': {}}, collections.Counter())
    assert e and e['tickets'][0]['date'] == '2026-10-05', (e, why)    # 直ったビルダーは組める
    assert not raw_stream_check(e['tickets'], [perf])
    assert raw_stream_check([{'type': '一般（東京 9/28公演）〜9/28', 'date': '2026-09-28'}], [perf])
    for s in (sale('先着発売終了', '配信視聴チケット', '20261005235900'),
              sale('先着発売中', '配信視聴チケット', '20260929235900'),
              sale('先着発売中', '一般', '20260928200000')):
        assert not raw_live_sales([dict(perf, performance_sales=[s])], today), s
    # 詳細ページの「受付」欄（一覧から落ちた時に読む）＝2026-09-30 の実ページと同じ形
    html = ('<!--受付--><section><ul class="g-ticketInfo">'
            '<li> <a href="/limited/reception/1" > <div class="fany-ticketInfo_text"> <p> <span class="g-tag">抽選販売</span>'
            ' ●FANY ID抽選先行 </p> <span class="period_txt">受付期間：</span> 2026/06/25(木) 11:00～2026/06/28(日) 11:00 </div>'
            ' <p class="g-ticketInfo_btn g-ticketInfo_btn-disabled no-margin">受付終了<i></i></p></a></li>'
            '<li> <a href="/reception/2" > <div class="fany-ticketInfo_text"> <p> <span class="g-tag">先着販売</span>'
            ' 配信視聴チケット </p> <span class="period_txt">受付期間：</span> 2026/09/20(日) 10:00～2026/10/05(月) 23:59 </div>'
            ' <p class="g-ticketInfo_btn no-margin">受付中<i></i></p></a></li>'
            '</ul></section><!--/受付-->')
    recs = detail_receptions(html)
    assert [(r['btn'], r['end']) for r in recs] == [('受付終了', '2026-06-28'), ('受付中', '2026-10-05')], recs
    assert len(live_detail(recs, today)) == 1, '受付中の配信を鳴らす'
    assert not live_detail(recs, '2026-10-06'), '締切が過ぎたら鳴らさない'
    assert not live_detail(recs[:1], today), '受付終了だけなら鳴らさない（本当に終わった）'
    rel = detail_receptions(html.replace('2026/09/20(日) 10:00～2026/10/05(月) 23:59', '2026/09/20(日) 10:00～開演2時間前'))
    assert rel[1]['end'] is None and live_detail(rel, today), '相対の締切で受付中＝終わったと言えない＝鳴らす'
    reg = load_registered()
    print('selftest OK（登録されているFANYのイベント %d本）' % len(reg))
    return 0


if __name__ == '__main__':
    sys.exit(main())
