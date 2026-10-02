# -*- coding: utf-8 -*-
"""TIGET由来エントリの機械ゲート＝**実ページから枠をゼロから作り直して、登録と全件突合**する。

  python tools/gate_tiget_slots.py            … 登録のTIGET枠を全部照合
  python tools/gate_tiget_slots.py --ids 1,2  … id指定

終了コード 0＝全一致 / 2＝食い違いあり（投入・pushの前に必ず 0 を確認する）

## なぜ要るか

TIGETは新しい売り場で、ぴあほど信頼が積み上がっていない。
e+ で「抽選プレオーダーが丸ごと落ちていたのをユーザーが画面で発見＝機械ゲートが1つも無かった」
（[[project_eplus_harvester_bug_and_qc]]）のと同じ穴を最初から塞いでおく。

## 見るもの

1. **枠の数**（登録 ⇄ 実ページ）
2. **券種名＋公演日＋締切**の一致（バッジの文字をそのまま作り直して比べる）
3. 売り切れ・販売終了の印が実ページの文言と合っているか
4. 🚨**締切が書かれていない枠**（当日支払い）は `saleEndUnknown` が付いているか
   ＝公演日を締切に流用していないか（2026-09-09 ラフ×ラフと同じ嘘の型）
5. 🆕2026-09-30 ビルダーが**組めなかった**ページを「公演が終わった＝正常」と決めつけない。
   実ページの生データに受付中・受付前で締切が今日以降の券種があれば、生データ突合の食い違いとして鳴らす
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

_KEEP = []          # 🚨ラッパーを生かしておく入れ物（下を読む）


def _load(path, name):
    # 🚨読み込む道具は中で sys.stdout を utf-8 のラッパーに差し替える。
    #    差し替え前のラッパーが**GCされると下の buffer まで閉じる**（Pythonの罠）。
    #    だから前後どちらのラッパーも _KEEP に握っておき、元に戻す。
    prev = sys.stdout
    _KEEP.append(prev)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _KEEP.append(sys.stdout)
    sys.stdout = prev
    return mod


# 🚨読み込む道具が中で sys.stdout を差し替えるので、**先に読み込んでから**こちらで包む
#    （包んだ後に読み込むと二重に包まれて「closed file」で落ちる）
TH = _load('tools/tiget_harvest.py', 'th')
BT = _load('tools/build_tiget_entries.py', 'bt')
REPORT = 'tmp/gate_tiget_report.txt'


def raw_stream_check(reg, d, today):
    """🆕2026-09-28 **ビルダーを通さない**突合（ZAIKOのスタリオンで、番人がビルダーと同じ間違いをして一致した）。
    実ページの元の券種名に「配信・視聴・アーカイブ」があり、受付中／発売前で締切が読めるなら、
    登録に「配信/視聴/アーカイブ」を含み date＝その締切の枠があるか。返り値＝食い違いの説明のリスト。"""
    out = []
    for p in d.get('programs') or []:
        for t in p.get('tickets') or []:
            nm = t.get('name') or ''
            if not re.search(BT.STREAM_RE, nm) or BT.state_of(t.get('class')) not in ('live', 'unopened'):
                continue
            per = BT.last_period(t)
            ed = per[2] if per else ((t.get('end_at') or [None])[0])
            if not ed or ed < today:
                continue
            if not any(r.get('date') == ed and re.search(BT.STREAM_RE, r.get('type') or '') for r in reg):
                out.append('配信の券種「%s」（〜%s）が、登録に「配信」付き・締切%sで無い' % (nm[:20], ed, ed))
    return out


def live_raw_tickets(d, today):
    """🆕2026-09-30 実ページの生データで「いま買える／これから買える」券種（ビルダーを通さない）。
    受付中・受付前で、締切（受付期間の終わり or 注記の受付終了日時）が今日以降。
    締切が書いていない券種は、その公演日が今日以降なら買える側に数える（当日支払いの形）。"""
    out = []
    for p in d.get('programs') or []:
        for t in p.get('tickets') or []:
            nm = t.get('name') or ''
            if BT.is_seller_side(nm) or BT.state_of(t.get('class')) not in ('live', 'unopened'):
                continue
            per = BT.last_period(t)
            ed = per[2] if per else ((t.get('end_at') or [None])[0])
            if (ed and ed >= today) or (not ed and (p.get('date') or '') >= today):
                out.append('%s（公演%s〜%s）' % ((nm or 'チケット')[:20], p.get('date'), ed or '締切の記載なし'))
    return out


def dropped_but_alive(built, d, today):
    """ビルダーが組めなかった（公演が終わった等で捨てた）のに、売り場ではまだ買える券種があるか。
    🚨2026-09-30 ZAIKOのスタリオン＝配信中なのに「組めない＝終わった＝正常」と読んで見逃した。
    返り値＝食い違いの説明のリスト（空なら問題なし）。"""
    if built:
        return []
    alive = live_raw_tickets(d, today)
    if not alive:
        return []
    return ['組み立てで捨てられたが、売り場ではまだ買える券種がある：%s' % ' / '.join(alive)]


def _selftest():
    today = '2026-09-30'
    stream = {'name': '【配信】視聴チケット', 'class': 'is-available',
              'periods': [{'parsed': ['2026-09-20', '10:00', '2026-10-05', '23:59']}]}
    d = {'url': 'u', 'name': 'スタリオン型', 'venue': 'v', 'prefecture': '東京', 'cats': ['81'], 'list': {},
         'programs': [{'date': '2026-09-28', 'tickets': [stream]}]}
    assert live_raw_tickets(d, today), '配信中の券種を買えると読む'
    # 組めなかった（ビルダーの穴）のに売り場で買える＝鳴らす
    assert dropped_but_alive(None, d, today), 'ビルダーが捨てた配信中のイベントを鳴らす'
    # 直ったビルダーはこの形を組める＝鳴らない
    built, why = BT.build(json.loads(json.dumps(d)), today)
    assert built and built['tickets'][0]['date'] == '2026-10-05', (built, why)
    assert not dropped_but_alive(built, d, today)
    # 登録が「配信なし・〜9/28」なら生データ突合で鳴る／正しい登録は鳴らない
    assert raw_stream_check([{'type': 'チケット（東京 9/28公演）〜9/28', 'date': '2026-09-28'}], d, today)
    assert not raw_stream_check(built['tickets'], d, today)
    # 本当に終わったもの（売り切れ・受付終了・締切が過ぎた配信・会場券だけ）は鳴らさない
    for t in (dict(stream, **{'class': 'is-unable is-unavailable'}), dict(stream, **{'class': 'is-unable is-closed'}),
              dict(stream, periods=[{'parsed': ['2026-09-20', '10:00', '2026-09-29', '23:59']}]),
              {'name': '会場チケット', 'class': 'is-available', 'periods': []}):
        dd = dict(d, programs=[{'date': '2026-09-28', 'tickets': [t]}])
        assert BT.build(json.loads(json.dumps(dd)), today)[0] is None, t
        assert not dropped_but_alive(None, dd, today), t
    print('selftest OK（組めない＝終わった と決めつけない／生データで買える券種を見る）')
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ids', default='')
    ap.add_argument('--today', default=datetime.date.today().isoformat())
    # 🚨TIGETを叩きすぎないための間。全件（1,900件超）回す時は必ず入れる
    ap.add_argument('--sleep', type=float, default=0.4)
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        sys.exit(_selftest())

    h = open('index.html', encoding='utf-8', newline='').read()
    ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))
    want = {int(x) for x in re.findall(r'\d+', a.ids)} if a.ids else None

    targets = []
    for e in ev:
        urls = sorted({m for t in (e.get('tickets') or []) + [{'url': (e.get('links') or {}).get('tiget')}]
                       for m in re.findall(r'tiget\.net/events/(\d+)', t.get('url') or '')})
        if not urls:
            continue
        if want and e['id'] not in want:
            continue
        targets.append((e, urls))

    ng, ok, fetcherr, rawng, private = [], 0, [], [], []
    rep = io.open(REPORT, 'w', encoding='utf-8')
    rep.write('=== gate_tiget_slots (today=%s) 対象%d件 ===\n' % (a.today, len(targets)))
    for e, urls in targets:
        # 実ページからゼロから作り直す（登録値は見ない）
        rebuilt, raws, dropped = [], [], []
        bad = False
        for eid in urls:
            try:
                d = TH.parse_event(TH.fetch(f'https://tiget.net/events/{eid}'), eid)
            except Exception as ex:
                # 🆕2026-10-03 主催者が非公開にしたページは403＋「非公開設定」の本文＝「読めない」でなく外す候補
                #   （ウイコス17 27261/27262 を「読めなかった」のまま新着に残し、ユーザーが画面で見つけた）
                body = ''
                try:
                    raw = ex.read()
                    if ex.headers.get('Content-Encoding') == 'gzip':
                        import gzip
                        raw = gzip.decompress(raw)
                    body = raw.decode('utf-8', 'replace')
                except Exception:
                    pass
                if getattr(ex, 'code', None) == 403 and '非公開設定' in body:
                    private.append((e['id'], eid))
                else:
                    fetcherr.append((e['id'], eid, str(ex)[:60]))
                bad = True
                continue
            raws.append(d)
            d['cats'] = ['81']
            d['list'] = {}
            built, why = BT.build(d, a.today)
            if built:
                rebuilt += built['tickets']
            # 🚨2026-09-30 組めなかった（公演が終わった等）を「正常」と決めつけない＝生データで買える券種を見る
            dropped += ['events/%s（%s）%s' % (eid, why, m) for m in dropped_but_alive(built, d, a.today)]
        if bad:
            continue
        time.sleep(a.sleep)
        reg = [t for t in (e.get('tickets') or []) if 'tiget.net' in (t.get('url') or '')]
        rc = dropped + [m for d in raws for m in raw_stream_check(reg, d, a.today)]
        if rc:
            rawng.append((e, rc))

        def key(t):
            import fold_parts as FP   # 🆕9/30 畳んだ1部・2部の印を外して比べる
            return (FP.bare_type(t.get('type')), t.get('date'), bool(t.get('soldout')),
                    bool(t.get('saleEnded')), bool(t.get('saleEndUnknown')))
        rk, gk = {key(t) for t in reg}, {key(t) for t in rebuilt}
        # 券種名は県を含む＝ゲートは県抜きの骨格でも比べる（一覧の場所が取れない時のため）
        def strip_pref(k):
            return (re.sub(r'（[^（）]*?(\d{1,2}/\d{1,2}公演）)', r'（\1', k[0] or ''),) + k[1:]
        if rk == gk or {strip_pref(x) for x in rk} == {strip_pref(x) for x in gk}:
            ok += 1
            continue
        ng.append((e, sorted(rk - gk), sorted(gk - rk)))

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
        rep.write('❌ id=%s events/%s 読めなかった: %s\n' % (i, eid, why))
    for i, eid in private:
        rep.write('🔒 id=%s events/%s 主催者が非公開設定＝載せない（新着なら外して tools/tiget_watch.json へ）\n' % (i, eid))
    rep.write('\n=== 集計: 一致 %d / 🚨食い違い %d / 🚨生データ突合 %d / ❌読めなかった %d / 🔒非公開 %d ===\n'
              % (ok, len(ng), len(rawng), len(fetcherr), len(private)))
    rep.close()
    # コンソールは文字化けするのでASCIIの要約だけ。中身は REPORT を読む
    sys.stderr.write('gate_tiget_slots: match=%d ng=%d rawng=%d fetcherr=%d private=%d -> %s\n'
                     % (ok, len(ng), len(rawng), len(fetcherr), len(private), REPORT))
    sys.exit(2 if (ng or fetcherr or rawng or private) else 0)


if __name__ == '__main__':
    main()
