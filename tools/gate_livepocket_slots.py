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
    return (t.get('type'), t.get('date'), bool(t.get('soldout')), bool(t.get('saleEnded')),
            bool(t.get('saleEndUnknown')))


def rebuild(eid, today):
    d = LH.parse_event(LH.fetch(f'{LH.BASE}/e/{eid}'), eid)
    built, why = BL.build(d, today)
    return (built['tickets'] if built else []), why


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ids', default='')
    ap.add_argument('--built', default='', help='投入前の組み上がりJSONを照合する')
    ap.add_argument('--today', default=datetime.date.today().isoformat())
    ap.add_argument('--sleep', type=float, default=1.0)
    ap.add_argument('--report', default=REPORT)
    a = ap.parse_args()

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

    ng, ok, fetcherr = [], 0, []
    for e, urls in targets:
        rebuilt, bad = [], False
        for eid in urls:
            try:
                tks, why = rebuild(eid, a.today)
                rebuilt += tks
            except Exception as ex:
                fetcherr.append((e['id'], eid, str(ex)[:80]))
                bad = True
            time.sleep(a.sleep)
        if bad:
            continue
        reg = [t for t in (e.get('tickets') or []) if 'livepocket.jp' in (t.get('url') or '')]
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
    for i, eid, why in fetcherr:
        rep.write('❌ id=%s e/%s 読めなかった: %s\n' % (i, eid, why))
    rep.write('\n=== 集計: 一致 %d / 🚨食い違い %d / ❌読めなかった %d ===\n' % (ok, len(ng), len(fetcherr)))
    rep.close()
    sys.stderr.write('gate_livepocket_slots: match=%d ng=%d fetcherr=%d -> %s\n'
                     % (ok, len(ng), len(fetcherr), a.report))
    sys.exit(1 if (ng or fetcherr) else 0)


if __name__ == '__main__':
    main()
