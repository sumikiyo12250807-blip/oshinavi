# -*- coding: utf-8 -*-
"""TIGET由来エントリの枠を**実ページから作り直して差し替える**（TIGET版のヒール）。

  python tools/heal_tiget.py                 … gate_tiget_slots のレポートで食い違ったidを下見
  python tools/heal_tiget.py --ids 1,2       … id指定で下見
  python tools/heal_tiget.py --apply         … 書き込む（そのあと gate_tiget_slots.py --ids で 0 を確かめる）

## なぜ要るか（2026-09-19 新設）

TIGETは「告知したらすぐ売る・当日券を当日に足す・売り切れたら印が付く」売り場で、
登録した枠が毎日ずれる。9/19朝の番人で 2,461件中152件が実ページと食い違った
（当日券が増えた／売り切れ・販売終了の印が付いた／券種が消えた）。ぴあのヒールはぴあ専用なので、
TIGETにはこれが要る。

## 作り直し方

`gate_tiget_slots.py` と**同じ関数**（tiget_harvest.parse_event → build_tiget_entries.build）で枠を作る
＝番人と同じ物差しなので、当てた後に番人を回せば 0 になる。

## 守ること

- 🚨**作り直しが空（出す側の申込・公演が過去・読めない）なら触らない**＝消さない。件数を報告に出す
- TIGET以外の売り場の枠（ぴあ・楽天等）は残す＝TIGETの枠だけ差し替える
- id・ジャンル・名前・会場は触らない
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
    prev = sys.stdout
    _KEEP.append(prev)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _KEEP.append(sys.stdout)
    sys.stdout = prev
    return mod


TH = _load('tools/tiget_harvest.py', 'th')
BT = _load('tools/build_tiget_entries.py', 'bt')
REPORT = 'tmp/heal_tiget_report.txt'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ids', default='')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--today', default=datetime.date.today().isoformat())
    ap.add_argument('--sleep', type=float, default=0.4)
    a = ap.parse_args()

    if a.ids:
        want = {int(x) for x in re.findall(r'\d+', a.ids)}
    else:
        want = {int(x) for x in re.findall(r'🚨 id=(\d+)', io.open('tmp/gate_tiget_report.txt', encoding='utf-8').read())}

    src = io.open('index.html', encoding='utf-8', newline='').read()
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
    events = json.loads(m.group(2))

    rep = io.open(REPORT, 'w', encoding='utf-8')
    done, empty, err = 0, [], []
    for e in events:
        if e['id'] not in want:
            continue
        tickets = e.get('tickets') or []
        urls = sorted({x for t in tickets + [{'url': (e.get('links') or {}).get('tiget')}]
                       for x in re.findall(r'tiget\.net/events/(\d+)', t.get('url') or '')})
        rebuilt, bad = [], False
        for eid in urls:
            try:
                d = TH.parse_event(TH.fetch(f'https://tiget.net/events/{eid}'), eid)
            except Exception as ex:
                err.append((e['id'], eid, str(ex)[:60]))
                bad = True
                continue
            d['cats'] = ['81']
            d['list'] = {}
            built, why = BT.build(d, a.today)
            if built:
                rebuilt += built['tickets']
            time.sleep(a.sleep)
        if bad:
            continue
        if not rebuilt:
            empty.append(e)
            continue
        others = [t for t in tickets if 'tiget.net' not in (t.get('url') or '')]
        old = [t for t in tickets if 'tiget.net' in (t.get('url') or '')]
        rep.write('\n■ id=%s %s  TIGET枠 %d → %d\n' % (e['id'], (e.get('name') or '')[:40], len(old), len(rebuilt)))
        for t in old:
            rep.write('    旧: %s | %s%s\n' % (t.get('type'), t.get('date'), ' 売切' if t.get('soldout') else ''))
        for t in rebuilt:
            rep.write('    新: %s | %s%s%s\n' % (t.get('type'), t.get('date'), ' 売切' if t.get('soldout') else '',
                                              ' 販売終了' if t.get('saleEnded') else ''))
        e['tickets'] = others + rebuilt
        done += 1

    rep.write('\n--- 作り直しが空（触らなかった）---\n')
    for e in empty:
        rep.write('  id=%s %s\n' % (e['id'], (e.get('name') or '')[:40]))
    for i, eid, why in err:
        rep.write('❌ id=%s events/%s 読めなかった: %s\n' % (i, eid, why))
    rep.write('\n=== 差し替え %d / 空で触らず %d / 読めず %d ===\n' % (done, len(empty), len(err)))
    rep.close()
    sys.stderr.write('heal_tiget: healed=%d empty=%d fetcherr=%d apply=%s -> %s\n'
                     % (done, len(empty), len(err), a.apply, REPORT))
    if not a.apply:
        return
    nl = '\r\n' if '\r\n' in src else '\n'
    out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
    io.open('index.html', 'w', encoding='utf-8', newline='').write(out)


if __name__ == '__main__':
    main()
