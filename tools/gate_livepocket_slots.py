# -*- coding: utf-8 -*-
"""livePocket 由来エントリの機械ゲート（番人）＝**実ページから枠をゼロから作り直して、登録と突合**する。

  python tools/gate_livepocket_slots.py              … 登録の livePocket 枠を全部照合
  python tools/gate_livepocket_slots.py --ids 1,2    … id指定
  python tools/gate_livepocket_slots.py --built tmp/built_livepocket_MMDD.json   … 投入前の組み上がりを照合（index.html を見ない）

終了コード 0＝全一致 / 1＝食い違い・読めないページあり（投入・pushの前に必ず 0 を確認する）

## 見るもの（gate_tiget_slots と同じ物差し）
券種名（＝受付名＋県＋公演日）・締切（date）・売り切れ／販売終了の印を、
`livepocket_harvest.parse_event → build_livepocket_entries.build` で作り直した枠と比べる。
🚨livePocket は販売中になると受付の開始日時が消える型がある＝「発売〜締切」の枠が「〜締切」に変わる。
   番人が鳴ったら `tools/heal_livepocket.py` で作り直す。
🆕2026-09-30 ビルダーが**組めなかった**ページを「公演が終わった＝正常」と決めつけない。
   実ページの生データに販売中・販売前で締切が今日以降の受付があれば、生データ突合の食い違いとして鳴らす
   （ZAIKOのスタリオン＝配信中なのに捨てて番人も見逃した）。`--selftest` で確かめられる。
"""
import argparse
import datetime
import importlib.util
import io
import json
import re
import sys
import time

_KEEP = []


def _load(path, name):
    # 🚨読み込む道具が sys.stdout を触っても、古いラッパーがGCされて buffer が閉じないよう握っておく（TIGETで踏んだ罠）
    prev = sys.stdout
    _KEEP.append(prev)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _KEEP.append(sys.stdout)
    sys.stdout = prev
    return mod


LH = _load('tools/livepocket_harvest.py', 'lh')
BL = _load('tools/build_livepocket_entries.py', 'bl')
REPORT = 'tmp/gate_livepocket_report.txt'
URL_RE = r'livepocket\.jp/e/([A-Za-z0-9_\-]+)'


def key(t):
    import fold_parts as FP   # 🆕9/30 畳んだ1部・2部の印を外して比べる
    return (FP.bare_type(t.get('type')), t.get('date'), bool(t.get('soldout')), bool(t.get('saleEnded')),
            bool(t.get('saleEndUnknown')))


STREAM_RE = r'配信(?!なし|無し)|視聴(?!覚)|アーカイブ'


def raw_check(reg, d, today):
    """🆕2026-09-28 **ビルダーを通さない**突合（ZAIKOのスタリオンで、番人がビルダーと同じ間違いをして一致した）。
    実ページの受付（receptions）を登録の文字に直接当てる。
      ①配信の語がある受付（受付名か券種名）が販売中／販売前で締切があるなら、登録に「配信/視聴/アーカイブ」を含み date＝締切の枠がある
      ②販売中／販売前の受付に締切があるなら、登録に date＝締切 か date＝公演日（公演日で締めた形）の枠がある
    返り値＝食い違いの説明のリスト。"""
    out = []
    shows = set((d or {}).get('dates') or [])
    for r in (d or {}).get('receptions') or []:
        if not re.search(r'販売中|販売前|受付中|受付前', r.get('status') or ''):
            continue
        end = ((r.get('period') or {}).get('end') or [None])[0]
        if not end or end < today:
            continue
        names = [r.get('title') or ''] + [c.get('name') or '' for c in r.get('cards') or []]
        nm = (r.get('title') or '')[:20]
        if any(re.search(STREAM_RE, x) for x in names) or re.match(r'\s*(オンライン|配信)', (d or {}).get('venue') or ''):
            if not any(t.get('date') == end and re.search(STREAM_RE, t.get('type') or '') for t in reg):
                out.append('配信の受付「%s」（〜%s）が、登録に「配信」付き・締切%sで無い' % (nm, end, end))
        elif not any(t.get('date') in ({end} | shows) for t in reg):
            out.append('受付「%s」の締切%sが登録のどの枠とも合わない' % (nm, end))
    return out


def live_raw_receptions(d, today):
    """🆕2026-09-30 実ページの生データで「いま買える／これから買える」受付（ビルダーを通さない）。
    札が販売中・販売前（受付中・受付前）で、締切が今日以降。締切が書いていない受付は、公演日が今日以降なら数える。"""
    out = []
    last = max((d or {}).get('dates') or [''])
    for r in (d or {}).get('receptions') or []:
        if not re.search(r'販売中|販売前|受付中|受付前', r.get('status') or ''):
            continue
        if BL.SELLER_SIDE.search(r.get('title') or ''):
            continue
        if r.get('cards') and all(re.search(r'予定販売|受付終了|販売終了', c.get('status') or '') for c in r['cards']):
            continue                                 # 受付は販売中でも券種が全部売り切れ・終了
        end = ((r.get('period') or {}).get('end') or [None])[0]
        if (end and end >= today) or (not end and last >= today):
            out.append('%s（%s・〜%s）' % ((r.get('title') or '受付')[:20], r.get('status'), end or '締切の記載なし'))
    return out


def dropped_but_alive(built, d, today):
    """ビルダーが組めなかった（公演が終わった等で捨てた）のに、売り場ではまだ買える受付があるか。
    🚨2026-09-30 ZAIKOのスタリオン＝配信中なのに「組めない＝終わった＝正常」と読んで見逃した。"""
    if built:
        return []
    alive = live_raw_receptions(d, today)
    return ['組み立てで捨てられたが、売り場ではまだ買える受付がある：%s' % ' / '.join(alive)] if alive else []


def rebuild(eid, today):
    d = LH.parse_event(LH.fetch(f'{LH.BASE}/e/{eid}'), eid)
    built, why = BL.build(d, today)
    return (built['tickets'] if built else []), why, d, built


def _selftest():
    today = '2026-09-30'
    st_rec = {'status': '販売中', 'title': '配信チケット受付',
              'period': {'start': ('2026-09-20', '20:00'), 'end': ('2026-10-05', '23:59'), 'text': ''},
              'cards': [{'name': '視聴チケット', 'status': '販売中'}]}
    d = {'id': 'x', 'url': 'https://livepocket.jp/e/x', 'name': 'スタリオン型', 'dates': ['2026-09-28'],
         'start_time': '22:00', 'venue': 'スタジオ', 'prefecture': '東京', 'performers': [],
         'cats': [['音楽', '']], 'receptions': [st_rec]}
    assert live_raw_receptions(d, today), '配信中の受付を買えると読む'
    assert dropped_but_alive(None, d, today), 'ビルダーが捨てた配信中のイベントを鳴らす'
    built, why = BL.build(json.loads(json.dumps(d)), today)
    assert built and built['tickets'][0]['date'] == '2026-10-05', (built, why)   # 直ったビルダーは組める
    assert not dropped_but_alive(built, d, today)
    assert not raw_check(built['tickets'], d, today)
    assert raw_check([{'type': '配信チケット受付（東京 9/28 22:00公演）〜9/28', 'date': '2026-09-28'}], d, today)
    for r0 in (dict(st_rec, cards=[{'name': '視聴チケット', 'status': '予定販売数終了'}]),
               dict(st_rec, status='販売終了', cards=[{'name': '視聴チケット', 'status': '受付終了'}]),
               dict(st_rec, period={'start': None, 'end': ('2026-09-29', '23:59'), 'text': ''}),
               dict(st_rec, title='会場チケット', period={'start': None, 'end': None, 'text': ''},
                    cards=[{'name': '一般', 'status': '販売中'}])):
        dd = dict(d, receptions=[r0])
        assert BL.build(json.loads(json.dumps(dd)), today)[0] is None, r0
        assert not dropped_but_alive(None, dd, today), r0
    print('selftest OK（組めない＝終わった と決めつけない／生データで買える受付を見る）')
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ids', default='')
    ap.add_argument('--built', default='', help='投入前の組み上がりJSONを照合する')
    ap.add_argument('--today', default=datetime.date.today().isoformat())
    ap.add_argument('--sleep', type=float, default=1.0)
    ap.add_argument('--report', default=REPORT)
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        sys.exit(_selftest())

    if a.built:
        src = json.load(io.open(a.built, encoding='utf-8'))
        ev = src['entries'] if isinstance(src, dict) else src
        for n, e in enumerate(ev):
            e.setdefault('id', 'built#%d' % n)
    else:
        h = io.open('index.html', encoding='utf-8', newline='').read()
        ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))
    want = {int(x) for x in re.findall(r'\d+', a.ids)} if a.ids else None

    targets = []
    for e in ev:
        urls = sorted({m for t in (e.get('tickets') or []) + [{'url': (e.get('links') or {}).get('livepocket')}]
                       for m in re.findall(URL_RE, t.get('url') or '')})
        if not urls:
            continue
        if want and e['id'] not in want:
            continue
        targets.append((e, urls))

    ng, ok, fetcherr, rawng = [], 0, [], []
    for e, urls in targets:
        rebuilt, bad, raws, dropped = [], False, [], []
        for eid in urls:
            try:
                tks, why, d, built = rebuild(eid, a.today)
                rebuilt += tks
                raws.append(d)
                # 🚨2026-09-30 組めなかった（公演が終わった等）を「正常」と決めつけない＝生データで買える受付を見る
                dropped += ['e/%s（%s）%s' % (eid, why, m) for m in dropped_but_alive(built, d, a.today)]
            except Exception as ex:
                fetcherr.append((e['id'], eid, str(ex)[:80]))
                bad = True
            time.sleep(a.sleep)
        if bad:
            continue
        reg = [t for t in (e.get('tickets') or []) if 'livepocket.jp' in (t.get('url') or '')]
        rc = dropped + [m for d in raws for m in raw_check(reg, d, a.today)]
        if rc:
            rawng.append((e, rc))
        rk, gk = {key(t) for t in reg}, {key(t) for t in rebuilt}
        if rk == gk:
            ok += 1
            continue
        ng.append((e, sorted(rk - gk, key=str), sorted(gk - rk, key=str)))

    rep = io.open(a.report, 'w', encoding='utf-8')
    rep.write('=== gate_livepocket_slots (today=%s) 対象%d件 %s ===\n'
              % (a.today, len(targets), ('built=' + a.built) if a.built else 'index.html'))
    for e, only_reg, only_page in ng:
        rep.write('\n🚨 id=%s %s\n' % (e['id'], (e.get('name') or '')[:40]))
        for k in only_reg:
            rep.write('    登録にだけある: %s\n' % (k,))
        for k in only_page:
            rep.write('    実ページにだけある: %s\n' % (k,))
    for e, rc in rawng:
        rep.write('\n🚨生データ突合（ビルダーを通さない） id=%s %s\n' % (e['id'], (e.get('name') or '')[:40]))
        for m in rc:
            rep.write('    %s\n' % m)
    for i, eid, why in fetcherr:
        rep.write('❌ id=%s e/%s 読めなかった: %s\n' % (i, eid, why))
    rep.write('\n=== 集計: 一致 %d / 🚨食い違い %d / 🚨生データ突合 %d / ❌読めなかった %d ===\n'
              % (ok, len(ng), len(rawng), len(fetcherr)))
    rep.close()
    sys.stderr.write('gate_livepocket_slots: match=%d ng=%d rawng=%d fetcherr=%d -> %s\n'
                     % (ok, len(ng), len(rawng), len(fetcherr), a.report))
    sys.exit(1 if (ng or fetcherr or rawng) else 0)


if __name__ == '__main__':
    main()
