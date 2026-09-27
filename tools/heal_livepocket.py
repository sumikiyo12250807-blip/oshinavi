# -*- coding: utf-8 -*-
"""livePocket 由来エントリの枠を**実ページから作り直して差し替える**（livePocket版のヒール）。

  python tools/heal_livepocket.py                 … gate_livepocket_slots のレポートで食い違ったidを下見
  python tools/heal_livepocket.py --ids 1,2       … id指定で下見
  python tools/heal_livepocket.py --apply         … 書き込む（そのあと gate_livepocket_slots.py --ids で 0 を確かめる）

## 作り直し方
番人（gate_livepocket_slots）と**同じ関数**（livepocket_harvest.parse_event → build_livepocket_entries.build）
で枠を作る＝同じ物差しなので、当てた後に番人を回せば 0 になる。

## 守ること（heal_tiget と同じ）
- 🚨**作り直しが空（出す側・公演が過去・読めない）なら触らない**＝消さない。件数を報告に出す
- livePocket 以外の売り場の枠は残す＝livePocket の枠だけ差し替える
- id・ジャンル・名前・会場は触らない
- index.html は CRLF を保って書く
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


LH = _load('tools/livepocket_harvest.py', 'lh')
BL = _load('tools/build_livepocket_entries.py', 'bl')
REPORT = 'tmp/heal_livepocket_report.txt'
URL_RE = r'livepocket\.jp/e/([A-Za-z0-9_\-]+)'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ids', default='')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--today', default=datetime.date.today().isoformat())
    ap.add_argument('--sleep', type=float, default=1.0)
    a = ap.parse_args()

    if a.ids:
        want = {int(x) for x in re.findall(r'\d+', a.ids)}
    else:
        want = {int(x) for x in re.findall(r'🚨 id=(\d+)',
                                           io.open('tmp/gate_livepocket_report.txt', encoding='utf-8').read())}

    src = io.open('index.html', encoding='utf-8', newline='').read()
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
    events = json.loads(m.group(2))

    rep = io.open(REPORT, 'w', encoding='utf-8')
    rep.write('=== heal_livepocket (today=%s) 対象%d件 apply=%s ===\n' % (a.today, len(want), a.apply))
    done, empty, err = 0, [], []
    for e in events:
        if e['id'] not in want:
            continue
        tickets = e.get('tickets') or []
        urls = sorted({x for t in tickets + [{'url': (e.get('links') or {}).get('livepocket')}]
                       for x in re.findall(URL_RE, t.get('url') or '')})
        rebuilt, bad, whys = [], False, []
        for eid in urls:
            try:
                d = LH.parse_event(LH.fetch(f'{LH.BASE}/e/{eid}'), eid)
            except Exception as ex:
                err.append((e['id'], eid, str(ex)[:80]))
                bad = True
                continue
            built, why = BL.build(d, a.today)
            if built:
                rebuilt += built['tickets']
            else:
                whys.append(why)
            time.sleep(a.sleep)
        if bad:
            continue
        if not rebuilt:
            empty.append((e, whys))
            continue
        others = [t for t in tickets if 'livepocket.jp' not in (t.get('url') or '')]
        old = [t for t in tickets if 'livepocket.jp' in (t.get('url') or '')]
        rep.write('\n■ id=%s %s  livePocket枠 %d → %d\n' % (e['id'], (e.get('name') or '')[:40], len(old), len(rebuilt)))
        for t in old:
            rep.write('    旧: %s | %s%s%s\n' % (t.get('type'), t.get('date'), ' 売切' if t.get('soldout') else '',
                                              ' 販売終了' if t.get('saleEnded') else ''))
        for t in rebuilt:
            rep.write('    新: %s | %s%s%s\n' % (t.get('type'), t.get('date'), ' 売切' if t.get('soldout') else '',
                                              ' 販売終了' if t.get('saleEnded') else ''))
        e['tickets'] = others + rebuilt
        done += 1

    rep.write('\n--- 作り直しが空（触らなかった）---\n')
    for e, whys in empty:
        rep.write('  id=%s %s … %s\n' % (e['id'], (e.get('name') or '')[:40], ' / '.join(w or '' for w in whys)))
    for i, eid, why in err:
        rep.write('❌ id=%s e/%s 読めなかった: %s\n' % (i, eid, why))
    rep.write('\n=== 差し替え %d / 空で触らず %d / 読めず %d ===\n' % (done, len(empty), len(err)))
    rep.close()
    sys.stderr.write('heal_livepocket: healed=%d empty=%d fetcherr=%d apply=%s -> %s\n'
                     % (done, len(empty), len(err), a.apply, REPORT))
    if not a.apply:
        return
    nl = '\r\n' if '\r\n' in src else '\n'
    out = (src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl)
           + m.group(3) + src[m.end():])
    io.open('index.html', 'w', encoding='utf-8', newline='').write(out)


if __name__ == '__main__':
    main()
