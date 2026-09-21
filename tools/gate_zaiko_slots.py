# -*- coding: utf-8 -*-
"""ZAIKOの登録枠を、売り場から**ゼロから作り直して**全件突合する番人（毎朝用）。

  python tools/gate_zaiko_slots.py                       … 引き直して突合（重い）
  python tools/gate_zaiko_slots.py --src tmp/zaiko_MMDD.json   … 引いてある結果で突合（速い）
  python tools/gate_zaiko_slots.py --ids 20459,20460     … その id だけ
  python tools/gate_zaiko_slots.py --selftest

終了コード＝**0:一致／1:食い違いあり／2:引けなかった**（1以上なら投入・pushの前に直す）。

## なぜ要るか
TIGET・FANYと同じで、売り場の枠は**毎日ずれる**（当日券が足される・売り切れの印が付く・
締切が延びる）。ぴあのヒールはZAIKOを見ないし、`check_zero_badge` は「枠0」しか見ない。
＝**この番人が無いと、登録した表示値がページとズレても誰も気づかない**。

## 見方
- `只ページ側にある`＝売り場に増えた枠 → 取り直して足す
- `只登録側にある`＝売り場から消えた枠。**売り切れ・販売終了の印つきなら残す**
  （[[feedback_soldout_keep_visible]]）。印なしで消えているなら取り直す
- 一覧から落ちたイベントは**「消えた」と決めつけない**＝公演日が過ぎた分は正常
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
import build_zaiko_entries as BZ          # noqa: E402
import zaiko_harvest as ZH                # noqa: E402

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

REPORT = 'tmp/gate_zaiko_report.txt'


def key(t):
    """比べる骨格＝バッジの文字・締切・印。url は比べない（同じイベントURLなので意味がない）。"""
    return (t.get('type'), t.get('date'), bool(t.get('soldout')),
            bool(t.get('saleEnded')), bool(t.get('saleEndUnknown')))


def listrow_from_entry(e, url):
    """一覧の行を**登録エントリから復元**する（番人は一覧を引かずに個別だけ見れば足りる）。
    使うのは公演日・開演時刻・会場・県だけ。cat（カテゴリ）はジャンルの受け皿にしか使わず、
    枠の突合には関わらないので空でよい。"""
    m = re.search(r'(\d{1,2}:\d{2})開演', e.get('dateLabel') or '')
    return {'url': url, 'title': e.get('name') or '', 'date': e.get('date'),
            'time': m.group(1) if m else '', 'venue': e.get('venue') or '',
            'pref': e.get('prefecture') or '', 'cat': None}


def load_registered(ids=None):
    h = io.open('index.html', encoding='utf-8', newline='').read()
    ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))
    out = {}
    for e in ev:
        u = (e.get('links') or {}).get('zaiko')
        if not u:
            continue
        if ids and e['id'] not in ids:
            continue
        out.setdefault(u, []).append(e)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', default=None, help='引いてある結果（list＋details）')
    ap.add_argument('--ids', default='')
    ap.add_argument('--sleep', type=float, default=0.7)
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        return _selftest()

    today = datetime.date.today().isoformat()
    ids = {int(x) for x in re.findall(r'\d+', a.ids)} or None
    reg = load_registered(ids)
    if not reg:
        print('ZAIKOの登録が無い（links.zaiko を持つエントリ0件）')
        return 0

    # 🚨**登録されているイベントの個別ページを自分で引く**のが番人の仕事。
    #   zaiko_harvest の --detail は「一覧にあって未登録のもの」だけ引く作り（収集用の効率化）なので、
    #   それを流用すると**登録済みの分が details に無くて突合できない**（2026-09-21に踏んだ）。
    det, ferr = {}, []
    if a.src:
        data = json.load(io.open(a.src, encoding='utf-8'))
        det = data.get('details') or {}
        rows = {r['url']: r for r in (data.get('list') or [])}
    else:
        rows = {}
        for i, u in enumerate(sorted(reg), 1):
            d = ZH.parse_event(ZH.fetch(u), u)
            if d is None:
                ferr.append(u)
            else:
                det[u] = d
            if i % 50 == 0:
                print('  引いた %d/%d件' % (i, len(reg)))
            time.sleep(a.sleep)
        if ferr and len(ferr) == len(reg):
            print('🚨1件も引けなかった＝突合できない（「一致」と言ってはいけない）')
            return 2

    # 売り場のデータからゼロから組み直す（登録値は見ない）
    page, unknown = {}, collections.Counter()
    for u, entries in reg.items():
        r = rows.get(u) or listrow_from_entry(entries[0], u)
        e, _ = BZ.build_one(r, det.get(u), today, unknown)
        if e:
            page[u] = e['tickets']

    ng, ok, gone, nodetail = [], 0, [], []
    for u, entries in sorted(reg.items()):
        rk = {key(t) for e in entries for t in (e.get('tickets') or [])}
        if u not in det:
            nodetail.append((u, entries))       # 個別が引けていない＝判定不能（「消えた」ではない）
            continue
        if u not in page:
            gone.append((u, entries))           # 引けたが組めない＝公演が終わった等
            continue
        gk = {key(t) for t in page[u]}
        if rk == gk:
            ok += 1
            continue
        ng.append((u, entries, sorted(rk - gk), sorted(gk - rk)))

    rep = io.open(REPORT, 'w', encoding='utf-8')
    rep.write('=== gate_zaiko_slots (today=%s) 対象%dイベント ===\n' % (today, len(reg)))
    rep.write('一致 %d / 食い違い %d / 一覧から落ちた %d / 個別が引けず判定不能 %d\n\n'
              % (ok, len(ng), len(gone), len(nodetail)))
    for u, entries, only_reg, only_page in ng:
        e = entries[0]
        rep.write('--- id%s %s @ %s\n    %s\n'
                  % (','.join(str(x['id']) for x in entries), (e.get('name') or '')[:40],
                     (e.get('venue') or '')[:20], u))
        for k in only_reg:
            rep.write('    只登録側: %s | %s | soldout=%s saleEnded=%s unknown=%s\n' % k)
        for k in only_page:
            rep.write('    只ページ側: %s | %s | soldout=%s saleEnded=%s unknown=%s\n' % k)
    rep.write('\n=== 一覧から落ちたイベント（公演日が過ぎた分は正常）===\n')
    for u, entries in gone:
        for e in entries:
            rep.write('  id%-6s 公演%s %s\n' % (e['id'], e.get('date'), (e.get('name') or '')[:40]))
    rep.write('\n=== 個別が引けず判定できなかった ===\n')
    for u, entries in nodetail:
        rep.write('  id%s %s\n' % (','.join(str(x['id']) for x in entries), u))
    if unknown:
        rep.write('\n🚨表に無いジャンル: %s\n' % dict(unknown))
    rep.close()
    print('gate_zaiko_slots: 一致%d / 食い違い%d / 一覧落ち%d / 判定不能%d → %s'
          % (ok, len(ng), len(gone), len(nodetail), REPORT))
    return 1 if ng else 0


def _selftest():
    t1 = {'type': 'チケット（東京 10/1公演）〜9/30 23:59', 'date': '2026-09-30',
          'url': 'https://akb48.zaiko.io/ja/e/x'}
    assert key(t1) == key(dict(t1, url='https://other.zaiko.io/ja/e/y')), \
        'url が違っても同じ枠と見る'
    assert key(t1) != key(dict(t1, soldout=True)), '印が付いたら別の枠と見る'
    assert key(t1) != key(dict(t1, saleEndUnknown=True)), '締切不明の印も見分ける'
    # 一覧の行を登録エントリから復元できるか
    r = listrow_from_entry({'name': 'テスト', 'date': '2026-10-01',
                            'dateLabel': '2026年10月1日(木) 19:00開演',
                            'venue': 'AKB48劇場', 'prefecture': '東京'}, 'https://x.zaiko.io/ja/e/y')
    assert r['time'] == '19:00' and r['date'] == '2026-10-01', r
    reg = load_registered()
    print('selftest OK（登録されているZAIKOのイベント %d本）' % len(reg))
    return 0


if __name__ == '__main__':
    sys.exit(main())
