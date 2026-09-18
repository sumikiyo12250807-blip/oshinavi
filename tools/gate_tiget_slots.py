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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ids', default='')
    ap.add_argument('--today', default=datetime.date.today().isoformat())
    # 🚨TIGETを叩きすぎないための間。全件（1,900件超）回す時は必ず入れる
    ap.add_argument('--sleep', type=float, default=0.4)
    a = ap.parse_args()

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

    ng, ok, fetcherr = [], 0, []
    rep = io.open(REPORT, 'w', encoding='utf-8')
    rep.write('=== gate_tiget_slots (today=%s) 対象%d件 ===\n' % (a.today, len(targets)))
    for e, urls in targets:
        # 実ページからゼロから作り直す（登録値は見ない）
        rebuilt = []
        bad = False
        for eid in urls:
            try:
                d = TH.parse_event(TH.fetch(f'https://tiget.net/events/{eid}'), eid)
            except Exception as ex:
                fetcherr.append((e['id'], eid, str(ex)[:60]))
                bad = True
                continue
            d['cats'] = ['81']
            d['list'] = {}
            built, why = BT.build(d, a.today)
            if built:
                rebuilt += built['tickets']
        if bad:
            continue
        time.sleep(a.sleep)
        reg = [t for t in (e.get('tickets') or []) if 'tiget.net' in (t.get('url') or '')]

        def key(t):
            return (t.get('type'), t.get('date'), bool(t.get('soldout')),
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
    for i, eid, why in fetcherr:
        rep.write('❌ id=%s events/%s 読めなかった: %s\n' % (i, eid, why))
    rep.write('\n=== 集計: 一致 %d / 🚨食い違い %d / ❌読めなかった %d ===\n'
              % (ok, len(ng), len(fetcherr)))
    rep.close()
    # コンソールは文字化けするのでASCIIの要約だけ。中身は REPORT を読む
    sys.stderr.write('gate_tiget_slots: match=%d ng=%d fetcherr=%d -> %s\n'
                     % (ok, len(ng), len(fetcherr), REPORT))
    sys.exit(2 if (ng or fetcherr) else 0)


if __name__ == '__main__':
    main()
