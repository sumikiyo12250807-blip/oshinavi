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
- 登録に無いイベント（一覧から落ちた）は**「消えた」と決めつけない**＝公演日が過ぎた分は正常
"""
import argparse
import collections
import datetime
import io
import json
import re
import sys

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
    for p in data['performances']:
        e, _ = BF.build_one(p, today, gmap, collections.Counter())
        if e:
            page[str(p.get('event_id'))] += e['tickets']

    ng, ok, gone, linkonly = [], 0, [], []
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
        rk = {key(t) for t in fany_slots}
        gk = {key(t) for t in page.get(fid, [])}
        if fid not in page:
            gone.append((fid, entries))
            continue
        if rk == gk:
            ok += 1
            continue
        ng.append((fid, entries, sorted(rk - gk), sorted(gk - rk)))

    rep = io.open(REPORT, 'w', encoding='utf-8')
    rep.write('=== gate_fany_slots (today=%s) 対象%dイベント ===\n' % (today, len(reg)))
    rep.write('一致 %d / 食い違い %d / 一覧から落ちた %d / リンクだけ足した分 %d\n\n'
              % (ok, len(ng), len(gone), len(linkonly)))
    for fid, entries, only_reg, only_page in ng:
        e = entries[0]
        rep.write('--- event/detail/%s  id%s %s @ %s\n'
                  % (fid, ','.join(str(x['id']) for x in entries),
                     (e.get('name') or '')[:40], (e.get('venue') or '')[:20]))
        for k in only_reg:
            rep.write('    只登録側: %s | %s | soldout=%s saleEnded=%s presaleEnded=%s\n' % k)
        for k in only_page:
            rep.write('    只ページ側: %s | %s | soldout=%s saleEnded=%s presaleEnded=%s\n' % k)
    rep.write('\n=== 一覧から落ちたイベント（公演日が過ぎた分は正常）===\n')
    for fid, entries in gone:
        for e in entries:
            rep.write('  id%-6s 公演%s %s\n' % (e['id'], e.get('date'), (e.get('name') or '')[:40]))
    rep.write('\n=== リンクだけ足した分（FANYの枠を足し込めば買える枠が増える候補）===\n')
    for fid, entries, n in linkonly:
        e = entries[0]
        rep.write('  id%-6s FANYに%2d枠 / 公演%s %s @ %s\n'
                  % (e['id'], n, e.get('date'), (e.get('name') or '')[:34],
                     (e.get('venue') or '')[:18]))
    rep.close()
    print('gate_fany_slots: 一致%d / 食い違い%d / 一覧落ち%d / リンクだけ%d → %s'
          % (ok, len(ng), len(gone), len(linkonly), REPORT))
    return 1 if ng else 0


def _selftest():
    t1 = {'type': '一般発売（大阪 10/1公演）〜9/30 8:00', 'date': '2026-09-30',
          'url': 'https://x/reception/1/2'}
    t2 = dict(t1, url='https://x/reception/9/9')
    assert key(t1) == key(t2), 'url が違っても同じ枠と見る'
    t3 = dict(t1, soldout=True, presaleEnded=True)
    assert key(t1) != key(t3), '印が付いたら別の枠と見る'
    reg = load_registered()
    print('selftest OK（登録されているFANYのイベント %d本）' % len(reg))
    return 0


if __name__ == '__main__':
    sys.exit(main())
