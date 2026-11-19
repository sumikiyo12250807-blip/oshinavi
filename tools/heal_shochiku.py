# -*- coding: utf-8 -*-
"""チケットWeb松竹 由来カードの枠を**発売日スケジュールのページから作り直して差し替える**（heal_ticketdive.py と同じ形）。

  python tools/heal_shochiku.py                 … gate_shochiku_slots のレポートで鳴った id を下見
  python tools/heal_shochiku.py --ids 1,2       … id 指定で下見
  python tools/heal_shochiku.py --apply         … 書き込む（そのあと gate_shochiku_slots.py --ids で 0 を確かめる）
  python tools/heal_shochiku.py --selftest

## 作り直し方
shochiku_harvest.harvest（東・西の2ページ）→ build_shochiku_entries.build。
カードとページの公演は「飛び先（ページ#劇場）＋公演名」で結ぶ（同じ劇場の別公演も同じ飛び先のため）。
## 守ること（heal_ticketdive と同じ）
- 作り直しが空（公演が終わった・ページから消えた・読めない）なら触らない＝消さない。件数を報告に出す
- 松竹以外の売り場の枠は残す＝松竹の枠だけ差し替える
- id・ジャンル・名前・会場は触らない
- カードの日付は、松竹だけのカードで作り直しと違う時に date・dateLabel を差し替える（会期の変更）
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


SH = _load('shochiku_harvest')
BS = _load('build_shochiku_entries')
if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
REPORT = 'tmp/heal_shochiku_report.txt'
MARK = 'ticket-web-shochiku.com'


def heal_one(e, built):
    """カード e に作り直し built を当てる（e を書き換える）。返り値＝変えたことの説明のリスト。"""
    notes = []
    others = [t for t in e.get('tickets') or [] if MARK not in (t.get('url') or '')]
    e['tickets'] = others + built['tickets']
    if not others and (built['date'] != e.get('date') or built['dateLabel'] != e.get('dateLabel')):
        notes.append('カードの日付: %s ｜ %s → %s ｜ %s' % (e.get('date'), e.get('dateLabel'), built['date'], built['dateLabel']))
        e['date'], e['dateLabel'] = built['date'], built['dateLabel']
    return notes


def _selftest():
    e = {'id': 1, 'name': '十二月大歌舞伎', 'date': '2026-12-25', 'dateLabel': 'x',
         'tickets': [{'type': 'ぴあ枠', 'url': 'https://t.pia.jp/x'},
                     {'type': '旧', 'url': 'https://www1.ticket-web-shochiku.com/t/info/a.html#box1'}]}
    b = {'name': '十二月大歌舞伎', 'date': '2026-12-26', 'dateLabel': 'y',
         'tickets': [{'type': '新', 'url': 'https://www1.ticket-web-shochiku.com/t/info/a.html#box1'}]}
    notes = heal_one(e, b)
    assert [t['type'] for t in e['tickets']] == ['ぴあ枠', '新'] and e['date'] == '2026-12-25' and notes == [], e
    e2 = {'name': 'B', 'date': '2026-12-03', 'dateLabel': 'x',
          'tickets': [{'type': '旧', 'url': 'https://www1.ticket-web-shochiku.com/t/info/a.html#box1'}]}
    heal_one(e2, b)
    assert e2['date'] == '2026-12-26' and e2['dateLabel'] == 'y', e2
    print('selftest OK: 松竹の枠だけ差し替え/他の売り場が無いカードだけ日付を直す')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ids', default='')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--today', default=datetime.datetime.now(BS.JST).date().isoformat())
    ap.add_argument('--sleep', type=float, default=3.0)
    ap.add_argument('--gate-report', default='tmp/gate_shochiku_report.txt')
    ap.add_argument('--report', default=REPORT)
    a = ap.parse_args([x for x in sys.argv[1:] if x != '--selftest'])
    if a.ids:
        want = {int(x) for x in re.findall(r'\d+', a.ids)}
    else:
        want = {int(x) for x in re.findall(r'🚨 id=(\d+)', io.open(a.gate_report, encoding='utf-8').read())}
    src = io.open('index.html', encoding='utf-8', newline='').read()
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
    events = json.loads(m.group(2))
    rows, errs = SH.harvest(a.sleep, log=lambda *x: None)
    fresh = {}
    for ev in rows:
        fresh[(ev['url'], re.sub(r'\s+', '', ev['title']))] = ev
    rep = io.open(a.report, 'w', encoding='utf-8')
    done, empty, err = 0, [], [('-', p['url'], p['error']) for p in errs]
    for e in events:
        if e['id'] not in want:
            continue
        url = (e.get('links') or {}).get('shochiku') or ''
        ev = fresh.get((url, re.sub(r'\s+', '', e.get('name') or '')))
        if not ev:
            empty.append((e, '売り場のページにこの公演が無い（消えた・名前が変わった）'))
            continue
        built, why = BS.build(ev, a.today)
        if not built:
            empty.append((e, why))
            continue
        old = [t for t in e.get('tickets') or [] if MARK in (t.get('url') or '')]
        rep.write('\n■ id=%s %s  松竹の枠 %d → %d\n' % (e['id'], (e.get('name') or '')[:40], len(old), len(built['tickets'])))
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
    sys.stderr.write('heal_shochiku: healed=%d empty=%d fetcherr=%d apply=%s -> %s\n'
                     % (done, len(empty), len(err), a.apply, a.report))
    if not a.apply or err:
        return
    nl = '\r\n' if '\r\n' in src else '\n'
    out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
    io.open('index.html', 'w', encoding='utf-8', newline='').write(out)


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        _selftest()
        sys.exit(0)
    main()
