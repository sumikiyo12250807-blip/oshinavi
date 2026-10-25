# -*- coding: utf-8 -*-
"""登録済みの出演者の欄を、売り場の個別ページから全員に作り直す（2026-10-25 新設）。

  python tools/backfill_artist.py tiget                 … 下見（tmp/backfill_artist_tiget.txt）
  python tools/backfill_artist.py tiget --apply         … 書き込む
  python tools/backfill_artist.py zaiko|livepocket [--ids 1,2] [--sleep 1.0]

## なぜ要るか

2026-10-24夜 すちこ「1」＝出演者の欄は全員。TIGET・livePocket・ZAIKO の組み立ては 10/24 まで
出演者を先頭3組で切っていた（[:3]）。組み立ては直したが、登録済みは3組のまま残っている。

## 守ること

- 当てるのは「今の出演者がちょうど3組で、作り直した出演者の先頭3組と同じ」ものだけ（＝3組で切られていた形）
- 売り場のページが1つだけのエントリだけ（畳んだカード・複数の売り場は触らない）
- 出演者の欄だけを書き換える（枠・名前・会場・ジャンルは触らない）。作り直しが空・読めないものは触らない
- 同じ売り場の番人・収集と同時に流さない（livePocket は2本で WAF に止まる）
"""
import argparse
import collections
import datetime
import importlib.util
import io
import json
import re
import sys
import time

sys.path.insert(0, 'tools')
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


KEY = {'tiget': r'tiget\.net/events/(\d+)', 'livepocket': r'livepocket\.jp/e/([\w-]+)', 'zaiko': r'(https://[\w-]+\.zaiko\.io/(?:ja/)?e/[\w-]+)'}


def builder(v, today):
    if v == 'tiget':
        TH = _load('tools/tiget_harvest.py', 'th')
        BT = _load('tools/build_tiget_entries.py', 'bt')

        def f(e, k):
            d = TH.parse_event(TH.fetch(f'https://tiget.net/events/{k}'), k)
            d['cats'] = ['81']
            d['list'] = {}
            b, _ = BT.build(d, today)
            return (b or {}).get('artist')
        return f
    if v == 'livepocket':
        LH = _load('tools/livepocket_harvest.py', 'lh')
        BL = _load('tools/build_livepocket_entries.py', 'bl')

        def f(e, k):
            d = LH.parse_event(LH.fetch(f'{LH.BASE}/e/{k}'), k)
            b, _ = BL.build(d, today)
            return (b or {}).get('artist')
        return f
    if v == 'zaiko':
        import build_zaiko_entries as BZ
        import gate_zaiko_slots as GZ
        import zaiko_harvest as ZH

        def f(e, k):
            d = ZH.parse_event(ZH.fetch(k), k)
            if d is None:
                return None
            b, _ = BZ.build_one(GZ.listrow_from_entry(e, k), d, today, collections.Counter())
            return (b or {}).get('artist')
        return f
    raise SystemExit('tiget|livepocket|zaiko')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('vendor')
    ap.add_argument('--ids', default='')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--sleep', type=float, default=0.6)
    a = ap.parse_args()
    v = a.vendor
    today = datetime.date.today().isoformat()
    want = {int(x) for x in re.findall(r'\d+', a.ids)}
    h = io.open('index.html', encoding='utf-8', newline='').read()
    m = re.search(r'const\s+EVENTS\s*=\s*(\[)', h)
    st = m.start(1)
    E, end = json.JSONDecoder().raw_decode(h, st)
    rx = re.compile(KEY[v])
    tg = []
    for e in E:
        if want and e['id'] not in want:
            continue
        if len((e.get('artist') or '').split('／')) != 3:
            continue
        ks = set(rx.findall(' '.join((t.get('url') or '') for t in e.get('tickets') or []) + ' ' + ((e.get('links') or {}).get(v) or '')))
        if len(ks) != 1:
            continue
        tg.append((e, ks.pop()))
    get = builder(v, today)
    rep = io.open(f'tmp/backfill_artist_{v}.txt', 'w', encoding='utf-8')
    rep.write(f'=== backfill_artist {v} today={today} 対象 {len(tg)} ===\n'); rep.flush()
    todo, same, other, err = [], 0, 0, 0
    for n, (e, k) in enumerate(tg, 1):
        try:
            new = get(e, k)
        except Exception as ex:
            err += 1
            rep.write(f'❌ id={e["id"]} {k} {str(ex)[:60]}\n')
            new = None
        time.sleep(a.sleep)
        old = e.get('artist') or ''
        if not new or new == old:
            same += 1 if new else 0
            continue
        if '／'.join(new.split('／')[:3]) != old:
            other += 1
            rep.write(f'↷ id={e["id"]} 先頭3組と合わない＝触らない\n    {old}\n  → {new}\n')
            continue
        todo.append((e, new))
        rep.write(f'✏️ id={e["id"]} {(e.get("name") or "")[:30]}\n    {old}\n  → {new}\n')
        if n % 50 == 0:
            rep.flush()
    rep.write(f'\n=== 書き換え {len(todo)} / 同じ {same} / 先頭3組と合わない {other} / 読めず {err} / apply={a.apply} ===\n')
    rep.close()
    sys.stderr.write(f'backfill_artist {v}: todo={len(todo)} same={same} other={other} err={err} apply={a.apply}\n')
    if not a.apply or not todo:
        return
    # 走らせている間に index.html が書き換わっていてもよいように、読み直して artist だけ当てる
    h = io.open('index.html', encoding='utf-8', newline='').read()
    m = re.search(r'const\s+EVENTS\s*=\s*(\[)', h)
    st = m.start(1)
    E, end = json.JSONDecoder().raw_decode(h, st)
    by = {e['id']: e for e in E}
    nput = 0
    for e0, new in todo:
        e = by.get(e0['id'])
        if e and e.get('artist') == e0.get('artist'):
            e['artist'] = new
            nput += 1
    nl = '\r\n' if '\r\n' in h else '\n'
    body = '[\n' + ',\n'.join(json.dumps(x, ensure_ascii=False, separators=(',', ':')) for x in E) + '\n]'
    out = h[:st] + body.replace('\n', nl) + h[end:]
    io.open('index.html', 'wb').write(out.encode('utf-8'))
    sys.stderr.write(f'書いた {nput}\n')


if __name__ == '__main__':
    main()
