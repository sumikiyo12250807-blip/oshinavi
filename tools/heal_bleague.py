# -*- coding: utf-8 -*-
"""B.LEAGUE チケット由来カードの枠を**試合の API から作り直して差し替える**（heal_ticketdive.py と同じ形）。

  python tools/heal_bleague.py                 … gate_bleague_slots のレポートで鳴った id を下見
  python tools/heal_bleague.py --ids 1,2       … id 指定で下見
  python tools/heal_bleague.py --apply         … 書き込む（そのあと gate_bleague_slots.py --ids で 0 を確かめる）
  python tools/heal_bleague.py --selftest

## 作り直し方
bleague_harvest.Site（一覧 /event-summaries:grouped-by-tenant・詳細 /tenants/…/events/…・残り枚数）→ build_bleague_entries.build。
## 守ること（heal_ticketdive と同じ）
- 作り直しが空（試合が過去・準備中・中止・読めない）なら触らない＝消さない。件数を報告に出す
- B.LEAGUE 以外の売り場の枠は残す＝B.LEAGUE の枠だけ差し替える
- id・ジャンル・名前・会場は触らない（名前・会場が変わった時は報告だけ）
- カードの日付は、B.LEAGUE だけのカードで作り直しと違う時に date・dateLabel を差し替える（試合日の変更）
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


BH = _load('bleague_harvest')
BB = _load('build_bleague_entries')
if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
REPORT = 'tmp/heal_bleague_report.txt'
URL_RE = r'ticket\.bleague\.jp/clubs/([a-z0-9]+)/events/([A-Za-z0-9]+)'


def heal_one(e, built):
    notes = []
    others = [t for t in e.get('tickets') or [] if 'ticket.bleague.jp' not in (t.get('url') or '')]
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


def fetch_one(site, host, eid, today):
    """1試合を読み直す → ハーベストと同じ形の dict。一覧から summary を引く（状態・ページが開くか）。"""
    summ = next((s for s in site.by_tenant(host) if s.get('eventId') == eid), None)
    if summ is None:
        raise ValueError('主催クラブの一覧に無い（公開が終わった・試合が終わった）')
    ev = {'id': eid, 'host': host, 'url': BH.page_url(host, eid), 'summary': summ, 'detail': None, 'stock': None}
    if summ.get('canNavigateToDetail'):
        ev['detail'] = site.detail(host, eid)
        if summ.get('salesStatus') in ('ON_SALE', 'BEFORE_SALE'):
            ev['stock'] = site.stock(host, eid)
    return ev


def _selftest():
    e = {'id': 1, 'name': 'A対B（会場） 大会', 'venue': '会場', 'date': '2026-12-19', 'dateLabel': 'x',
         'tickets': [{'type': 'ぴあ枠', 'url': 'https://t.pia.jp/x'},
                     {'type': '旧', 'url': 'https://ticket.bleague.jp/clubs/lh/events/E'}]}
    b = {'name': 'A対B（会場） 大会', 'venue': '会場', 'date': '2026-12-19', 'dateLabel': 'y',
         'tickets': [{'type': '新', 'url': 'https://ticket.bleague.jp/clubs/lh/events/E'}]}
    notes = heal_one(e, b)
    assert [t['type'] for t in e['tickets']] == ['ぴあ枠', '新'] and e['dateLabel'] == 'x' and notes == [], (e, notes)
    e2 = {'name': 'A対B（会場） 大会', 'venue': '会場2', 'date': '2026-12-19', 'dateLabel': 'x',
          'tickets': [{'type': '旧', 'url': 'https://ticket.bleague.jp/clubs/lh/events/E'}]}
    notes = heal_one(e2, dict(b, date='2026-12-20', dateLabel='z'))
    assert e2['date'] == '2026-12-20' and e2['venue'] == '会場2' and len(notes) == 2, (e2, notes)
    print('selftest OK: B.LEAGUE の枠だけ差し替え/B.LEAGUE だけのカードは日付も直す/名前・会場は報告だけ')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ids', default='')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--today', default=datetime.datetime.now(BH.JST).date().isoformat())
    ap.add_argument('--sleep', type=float, default=3.0)
    a = ap.parse_args([x for x in sys.argv[1:] if x != '--selftest'])
    if a.ids:
        want = {int(x) for x in re.findall(r'\d+', a.ids)}
    else:
        want = {int(x) for x in re.findall(r'🚨 id=(\d+)', io.open('tmp/gate_bleague_report.txt', encoding='utf-8').read())}
    src = io.open('index.html', encoding='utf-8', newline='').read()
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
    events = json.loads(m.group(2))
    site = BH.Site(a.sleep)
    rep = io.open(REPORT, 'w', encoding='utf-8')
    done, empty, err = 0, [], []
    for e in events:
        if e['id'] not in want:
            continue
        urls = sorted({u for t in (e.get('tickets') or []) + [{'url': (e.get('links') or {}).get('bleague')}]
                       for u in re.findall(URL_RE, t.get('url') or '')})
        if len(urls) != 1:
            err.append((e['id'], urls, '試合ページが1つでない'))
            continue
        try:
            ev = fetch_one(site, urls[0][0], urls[0][1], a.today)
        except Exception as ex:
            err.append((e['id'], urls, str(ex)[:60]))
            continue
        built, why = BB.build(ev, a.today, datetime.datetime.now(BH.JST))
        if not built:
            empty.append((e, why))
            continue
        old = [t for t in e.get('tickets') or [] if 'ticket.bleague.jp' in (t.get('url') or '')]
        rep.write('\n■ id=%s %s  B.LEAGUE枠 %d → %d\n' % (e['id'], (e.get('name') or '')[:44], len(old), len(built['tickets'])))
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
    sys.stderr.write('heal_bleague: healed=%d empty=%d fetcherr=%d apply=%s -> %s\n'
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
