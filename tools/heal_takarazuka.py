# -*- coding: utf-8 -*-
"""宝塚歌劇 由来カードの枠を**公演のチケットページから作り直して差し替える**（heal_ticketdive.py と同じ形）。

  python tools/heal_takarazuka.py                 … gate_takarazuka_slots のレポートで鳴った id を下見
  python tools/heal_takarazuka.py --ids 1,2       … id 指定で下見
  python tools/heal_takarazuka.py --apply         … 書き込む（そのあと gate_takarazuka_slots.py --ids で 0 を確かめる）
  python tools/heal_takarazuka.py --selftest

## 作り直し方
takarazuka_harvest.harvest（カードのページを名指し）→ build_takarazuka_entries.build。
## 守ること（heal_ticketdive と同じ）
- 作り直しが空（公演が終わった・受付の欄が消えた・読めない）なら触らない＝消さない。件数を報告に出す
- 宝塚以外の売り場の枠は残す＝宝塚のページの枠だけ差し替える
- id・ジャンル・名前・会場・県は触らない（公演名が変わった時は報告だけ）
- カードの日付は、宝塚だけのカードで作り直しと違う時に date・dateLabel を差し替える（会期の変更）
"""
import argparse
import datetime
import importlib.util
import io
import json
import os
import re
import sys

_KEEP = []
HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name):
    prev = sys.stdout
    _KEEP.append(prev)
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + '.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _KEEP.append(sys.stdout)
    sys.stdout = prev
    return mod


TZ = _load('takarazuka_harvest')
BZ = _load('build_takarazuka_entries')
if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
REPORT = 'tmp/heal_takarazuka_report.txt'
MARK = 'kageki.hankyu.co.jp'


def heal_one(e, built):
    notes = []
    others = [t for t in e.get('tickets') or [] if MARK not in (t.get('url') or '')]
    e['tickets'] = others + built['tickets']
    if not others and (built['date'] != e.get('date') or built['dateLabel'] != e.get('dateLabel')):
        notes.append('カードの日付: %s ｜ %s → %s ｜ %s' % (e.get('date'), e.get('dateLabel'), built['date'], built['dateLabel']))
        e['date'], e['dateLabel'] = built['date'], built['dateLabel']
    if re.sub(r'\s', '', built.get('name') or '') != re.sub(r'\s', '', e.get('name') or ''):
        notes.append('⚠️公演名が変わった（触っていない）: %s → %s' % (e.get('name'), built.get('name')))
    return notes


def _selftest():
    U = 'https://kageki.hankyu.co.jp/revue/2026/x/ticket_takarazuka.html'
    e = {'id': 1, 'name': 'A', 'date': '2027-01-24', 'dateLabel': 'x',
         'tickets': [{'type': 'ぴあ枠', 'url': 'https://t.pia.jp/x'}, {'type': '旧', 'url': U}]}
    b = {'name': 'A', 'date': '2027-01-25', 'dateLabel': 'y', 'tickets': [{'type': '新', 'url': U}]}
    assert heal_one(e, b) == [] and [t['type'] for t in e['tickets']] == ['ぴあ枠', '新'] and e['date'] == '2027-01-24'
    e2 = {'name': 'A', 'date': '2027-01-24', 'dateLabel': 'x', 'tickets': [{'type': '旧', 'url': U}]}
    heal_one(e2, b)
    assert e2['date'] == '2027-01-25' and e2['dateLabel'] == 'y'
    assert heal_one(dict(e2), dict(b, name='B'))[-1].startswith('⚠️公演名が変わった')
    print('selftest OK: 宝塚の枠だけ差し替え/他の売り場が無いカードだけ日付を直す/公演名の変化は報告だけ')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ids', default='')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--today', default=datetime.datetime.now(BZ.JST).date().isoformat())
    ap.add_argument('--sleep', type=float, default=3.0)
    ap.add_argument('--gate-report', default='tmp/gate_takarazuka_report.txt')
    ap.add_argument('--report', default=REPORT)
    a = ap.parse_args([x for x in sys.argv[1:] if x != '--selftest'])
    if a.ids:
        want = {int(x) for x in re.findall(r'\d+', a.ids)}
    else:
        want = {int(x) for x in re.findall(r'🚨 id=(\d+)', io.open(a.gate_report, encoding='utf-8').read())}
    src = io.open('index.html', encoding='utf-8', newline='').read()
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
    events = json.loads(m.group(2))
    now = datetime.datetime.now(BZ.JST).replace(tzinfo=None)
    rep = io.open(a.report, 'w', encoding='utf-8')
    done, empty, err = 0, [], []
    for e in events:
        if e['id'] not in want:
            continue
        url = (e.get('links') or {}).get('takarazuka') or ''
        if not url:
            err.append((e['id'], url, '宝塚のページの飛び先が無い'))
            continue
        rows, errs = TZ.harvest(a.sleep, [url], log=lambda *x: None)
        if errs or not rows:
            err.append((e['id'], url, (errs[0]['error'] if errs else '読めない')[:60]))
            continue
        # 県はカードのものを使う（作り直しで県の出所が変わってもバッジがずれないように）
        built, why = BZ.build(rows[0], a.today, now, {BZ.venue_of(rows[0]): e.get('prefecture')} if e.get('prefecture') else {})
        if not built:
            empty.append((e, why))
            continue
        old = [t for t in e.get('tickets') or [] if MARK in (t.get('url') or '')]
        rep.write('\n■ id=%s %s  宝塚の枠 %d → %d\n' % (e['id'], (e.get('name') or '')[:40], len(old), len(built['tickets'])))
        for t in old:
            rep.write('    旧: %s | %s\n' % (t.get('type'), t.get('date')))
        for t in built['tickets']:
            rep.write('    新: %s | %s\n' % (t.get('type'), t.get('date')))
        for n in heal_one(e, built):
            rep.write('    %s\n' % n)
        done += 1
    rep.write('\n--- 作り直しが空（触らなかった）---\n')
    for e, why in empty:
        rep.write('  id=%s %s … %s\n' % (e['id'], (e.get('name') or '')[:40], why))
    for i, u, why in err:
        rep.write('❌ id=%s %s 読めなかった: %s\n' % (i, u, why))
    rep.write('\n=== 差し替え %d / 空で触らず %d / 読めず %d ===\n' % (done, len(empty), len(err)))
    rep.close()
    sys.stderr.write('heal_takarazuka: healed=%d empty=%d fetcherr=%d apply=%s -> %s\n'
                     % (done, len(empty), len(err), a.apply, a.report))
    if not a.apply:
        return
    nl = '\r\n' if '\r\n' in src else '\n'
    out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
    io.open('index.html', 'w', encoding='utf-8', newline='').write(out)


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        _selftest()
        sys.exit(0)
    main()
