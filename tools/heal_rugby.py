# -*- coding: utf-8 -*-
"""TicketRugby 由来カードの枠を**発売情報のページから作り直して差し替える**（heal_bleague.py と同じ形）。

  python tools/heal_rugby.py                 … gate_rugby_slots のレポートで鳴った id を下見
  python tools/heal_rugby.py --ids 1,2       … id 指定で下見
  python tools/heal_rugby.py --apply         … 書き込む（そのあと gate_rugby_slots.py --ids で 0 を確かめる）
  python tools/heal_rugby.py --selftest

## 作り直し方
rugby_harvest（一覧を全部読んで試合日・会場・状態を引く＋/ticket_release_info/<番号>）→ build_rugby_entries.build。
## 守ること
- 作り直しが空（試合が過去・受付が全部終わった・読めない）なら触らない＝消さない。件数を報告に出す
- TicketRugby 以外の売り場の枠は残す＝TicketRugby の枠だけ差し替える
- id・ジャンル・名前・会場は触らない（変わった時は報告だけ）
- カードの日付は、TicketRugby だけのカードで作り直しと違う時に date・dateLabel を差し替える
"""
import argparse
import datetime
import importlib.util
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + '.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


RH = _load('rugby_harvest')
BR = _load('build_rugby_entries')
if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
REPORT = 'tmp/heal_rugby_report.txt'
URL_RE = r'ticketrugby\.jp/ticket_release_info/(\d+)'


def heal_one(e, built):
    notes = []
    others = [t for t in e.get('tickets') or [] if 'ticketrugby.jp' not in (t.get('url') or '')]
    e['tickets'] = others + built['tickets']
    if not others and (built['date'] != e.get('date') or built['dateLabel'] != e.get('dateLabel')):
        notes.append('カードの日付: %s ｜ %s → %s ｜ %s' % (e.get('date'), e.get('dateLabel'), built['date'], built['dateLabel']))
        e['date'], e['dateLabel'] = built['date'], built['dateLabel']
    n = lambda s: re.sub(r'[\s　]', '', s or '')
    if n(built.get('name')) != n(e.get('name')):
        notes.append('⚠️名前が変わった（触っていない）: %s → %s' % (e.get('name'), built.get('name')))
    if n(built.get('venue')) != n(e.get('venue')):
        notes.append('⚠️会場が変わった（触っていない）: %s → %s' % (e.get('venue'), built.get('venue')))
    return notes


def _selftest():
    e = {'name': 'A対B（会場）', 'venue': '会場', 'date': '2026-12-19', 'dateLabel': 'x',
         'tickets': [{'type': 'ぴあ枠', 'url': 'https://t.pia.jp/x'},
                     {'type': '旧', 'url': 'https://ticketrugby.jp/ticket_release_info/1'}]}
    b = {'name': 'A対B（会場）', 'venue': '会場', 'date': '2026-12-19', 'dateLabel': 'y',
         'tickets': [{'type': '新', 'url': 'https://ticketrugby.jp/ticket_release_info/1'}]}
    assert heal_one(e, b) == [] and [t['type'] for t in e['tickets']] == ['ぴあ枠', '新'] and e['dateLabel'] == 'x'
    e2 = {'name': 'A', 'venue': '会場', 'date': '2026-12-19', 'dateLabel': 'x',
          'tickets': [{'type': '旧', 'url': 'https://ticketrugby.jp/ticket_release_info/1'}]}
    heal_one(e2, dict(b, date='2026-12-20', dateLabel='z'))
    assert e2['date'] == '2026-12-20', e2
    print('selftest OK: TicketRugby の枠だけ差し替え/TicketRugby だけのカードは日付も直す/名前・会場は報告だけ')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ids', default='')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--sleep', type=float, default=3.0)
    a = ap.parse_args([x for x in sys.argv[1:] if x != '--selftest'])
    if a.ids:
        want = {int(x) for x in re.findall(r'\d+', a.ids)}
    else:
        want = {int(x) for x in re.findall(r'🚨 id=(\d+)', io.open('tmp/gate_rugby_report.txt', encoding='utf-8').read())}
    src = io.open('index.html', encoding='utf-8', newline='').read()
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
    events = json.loads(m.group(2))
    targets = {}
    for e in events:
        if e['id'] in want:
            urls = sorted({u for t in (e.get('tickets') or []) + [{'url': (e.get('links') or {}).get('ticketrugby')}]
                           for u in re.findall(URL_RE, t.get('url') or '')})
            targets[e['id']] = urls
    site = RH.Site(a.sleep)
    gids = sorted({int(u[0]) for u in targets.values() if len(u) == 1})
    d = RH.harvest(site, gids) if gids else {'events': [], 'errors': []}
    byg = {ev['id']: ev for ev in d['events']}
    now = datetime.datetime.now(RH.JST).replace(tzinfo=None)
    today = now.date().isoformat()
    rep = io.open(REPORT, 'w', encoding='utf-8')
    done, empty, err = 0, [], []
    for e in events:
        if e['id'] not in want:
            continue
        urls = targets.get(e['id']) or []
        if len(urls) != 1:
            err.append((e['id'], urls, '発売情報のページが1つでない'))
            continue
        ev = byg.get(int(urls[0]))
        if not ev or not ev.get('date'):
            err.append((e['id'], urls, '一覧に無い・読めない（受付が終わった疑い）'))
            continue
        built, why = BR.build(ev, today, now)
        if not built:
            empty.append((e, why))
            continue
        old = [t for t in e.get('tickets') or [] if 'ticketrugby.jp' in (t.get('url') or '')]
        rep.write('\n■ id=%s %s  TicketRugby枠 %d → %d\n' % (e['id'], (e.get('name') or '')[:44], len(old), len(built['tickets'])))
        for t in old:
            rep.write('    旧: %s | %s%s\n' % (t.get('type'), t.get('date'), ' 売切' if t.get('soldout') else ''))
        for t in built['tickets']:
            rep.write('    新: %s | %s%s\n' % (t.get('type'), t.get('date'), ' 売切' if t.get('soldout') else ''))
        for n in heal_one(e, built):
            rep.write('    %s\n' % n)
        done += 1
    rep.write('\n--- 作り直しが空（触らなかった）---\n')
    for e, why in empty:
        rep.write('  id=%s %s … %s\n' % (e['id'], (e.get('name') or '')[:44], why))
    for i, u, why in err:
        rep.write('❌ id=%s %s 読めなかった: %s\n' % (i, u, why))
    rep.write('\n=== 差し替え %d / 空で触らず %d / 読めず %d ===\n' % (done, len(empty), len(err)))
    rep.close()
    sys.stderr.write('heal_rugby: healed=%d empty=%d fetcherr=%d apply=%s -> %s\n' % (done, len(empty), len(err), a.apply, REPORT))
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
