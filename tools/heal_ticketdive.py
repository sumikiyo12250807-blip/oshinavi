# -*- coding: utf-8 -*-
"""TicketDive 由来カードの枠を**公演ページから作り直して差し替える**（heal_tiget.py と同じ形）。

  python tools/heal_ticketdive.py                 … gate_ticketdive_slots のレポートで鳴った id を下見
  python tools/heal_ticketdive.py --ids 1,2       … id 指定で下見
  python tools/heal_ticketdive.py --apply         … 書き込む（そのあと gate_ticketdive_slots.py --ids で 0 を確かめる）
  python tools/heal_ticketdive.py --selftest

## 作り直し方
ticketdive_harvest.Site.event（/_next/data の JSON）→ build_ticketdive_entries.build。
## 守ること（heal_tiget と同じ）
- 作り直しが空（公演が過去・枠が無い・読めない）なら触らない＝消さない。件数を報告に出す
- TicketDive 以外の売り場の枠は残す＝TicketDive の枠だけ差し替える
- id・ジャンル・名前・会場は触らない（公演名が変わった時は報告だけ）
- カードの日付は、TicketDive だけのカードで作り直しと違う時に date・dateLabel を差し替える（公演日の変更）
- 出演者の欄は「公演名のまま（手直ししていない）」時だけ作り直しの出演者に差し替える
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


TD = _load('ticketdive_harvest')
BD = _load('build_ticketdive_entries')
if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
REPORT = 'tmp/heal_ticketdive_report.txt'
URL_RE = r'ticketdive\.com/event/([A-Za-z0-9_\-.%]+)'


def heal_one(e, built):
    """カード e に作り直し built を当てる（e を書き換える）。返り値＝変えたことの説明のリスト。"""
    notes = []
    tickets = e.get('tickets') or []
    others = [t for t in tickets if 'ticketdive.com' not in (t.get('url') or '')]
    e['tickets'] = others + built['tickets']
    if not others and (built['date'] != e.get('date') or built['dateLabel'] != e.get('dateLabel')):
        notes.append('カードの日付: %s ｜ %s → %s ｜ %s' % (e.get('date'), e.get('dateLabel'), built['date'], built['dateLabel']))
        e['date'], e['dateLabel'] = built['date'], built['dateLabel']
    n = lambda s: re.sub(r'[\s　]', '', s or '')
    if built.get('artist') and built['artist'] != built.get('name') and n(e.get('artist')) == n(e.get('name')):
        notes.append('出演者: %s → %s' % (e.get('artist'), built['artist']))
        e['artist'] = built['artist']
    if n(built.get('name')) != n(e.get('name')):
        notes.append('⚠️公演名が変わった（触っていない）: %s → %s' % (e.get('name'), built.get('name')))
    return notes


def _selftest():
    e = {'id': 1, 'name': 'A公演', 'artist': 'A公演', 'date': '2026-12-03', 'dateLabel': '2026年12月3日(木) 東京',
         'tickets': [{'type': 'ぴあ枠', 'url': 'https://t.pia.jp/x'},
                     {'type': '旧', 'url': 'https://ticketdive.com/event/a'}]}
    b = {'name': 'A公演', 'artist': 'あ', 'date': '2026-12-03', 'dateLabel': '2026年12月3日(木) 東京',
         'tickets': [{'type': '新', 'url': 'https://ticketdive.com/event/a'}]}
    notes = heal_one(e, b)
    assert [t['type'] for t in e['tickets']] == ['ぴあ枠', '新'] and e['artist'] == 'あ', e
    assert notes == ['出演者: A公演 → あ'], notes
    # TicketDive だけのカードは日付も直す／手で直した出演者は巻き戻さない
    e2 = {'name': 'B', 'artist': '手直し', 'date': '2026-12-03', 'dateLabel': 'x',
          'tickets': [{'type': '旧', 'url': 'https://ticketdive.com/event/b'}]}
    heal_one(e2, dict(b, name='B', date='2026-12-05', dateLabel='2026年12月5日(土) 東京'))
    assert e2['date'] == '2026-12-05' and e2['artist'] == '手直し', e2
    print('selftest OK: TicketDive の枠だけ差し替え/日付の直し/出演者は公演名のままの時だけ')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ids', default='')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--today', default=datetime.datetime.now(BD.JST).date().isoformat())
    ap.add_argument('--sleep', type=float, default=3.0)
    ap.add_argument('--place-table', action='store_true')
    a = ap.parse_args([x for x in sys.argv[1:] if x != '--selftest'])
    if a.ids:
        want = {int(x) for x in re.findall(r'\d+', a.ids)}
    else:
        want = {int(x) for x in re.findall(r'🚨 id=(\d+)', io.open('tmp/gate_ticketdive_report.txt', encoding='utf-8').read())}
    src = io.open('index.html', encoding='utf-8', newline='').read()
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
    events = json.loads(m.group(2))
    site = TD.Site(a.sleep)
    rep = io.open(REPORT, 'w', encoding='utf-8')
    done, empty, err = 0, [], []
    for e in events:
        if e['id'] not in want:
            continue
        urls = sorted({u for t in (e.get('tickets') or []) + [{'url': (e.get('links') or {}).get('ticketdive')}]
                       for u in re.findall(URL_RE, t.get('url') or '')})
        if len(urls) != 1:
            err.append((e['id'], urls, 'TicketDive の公演ページが1つでない'))
            continue
        try:
            d = site.event(urls[0])
        except Exception as ex:
            err.append((e['id'], urls, str(ex)[:60]))
            continue
        built, why = BD.build(d, a.today, place_table=a.place_table)
        if not built:
            empty.append((e, why))
            continue
        old = [t for t in e.get('tickets') or [] if 'ticketdive.com' in (t.get('url') or '')]
        rep.write('\n■ id=%s %s  TicketDive枠 %d → %d\n' % (e['id'], (e.get('name') or '')[:40], len(old), len(built['tickets'])))
        for t in old:
            rep.write('    旧: %s | %s%s\n' % (t.get('type'), t.get('date'), ' 売切' if t.get('soldout') else ''))
        for t in built['tickets']:
            rep.write('    新: %s | %s%s\n' % (t.get('type'), t.get('date'), ' 売切' if t.get('soldout') else ''))
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
    sys.stderr.write('heal_ticketdive: healed=%d empty=%d fetcherr=%d apply=%s -> %s\n'
                     % (done, len(empty), len(err), a.apply, REPORT))
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
