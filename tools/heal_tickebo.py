# -*- coding: utf-8 -*-
"""チケットボード由来カードの枠を**受付ページの JSON から作り直して差し替える**（heal_ticketdive.py と同じ形）。

  python tools/heal_tickebo.py                 … gate_tickebo_slots のレポートで鳴った id を下見
  python tools/heal_tickebo.py --ids 1,2       … id 指定で下見
  python tools/heal_tickebo.py --apply         … 書き込む（そのあと gate_tickebo_slots.py --ids で 0 を確かめる）
  python tools/heal_tickebo.py --selftest

## 作り直し方
tickebo_harvest.Site.sales（/web/api/evt/sales-list）→ build_tickebo_entries.build（ジャンル札はカードの _srcgenre から戻す）。
## 守ること
- 作り直しが空（公演が過去・受付が全部終わった・読めない）なら触らない＝消さない。件数を報告に出す
- チケットボード以外の売り場の枠は残す＝チケットボードの枠だけ差し替える
- id・ジャンル・名前・会場は触らない（変わった時は報告だけ）
- カードの日付は、チケットボードだけのカードで作り直しと違う時に date・dateLabel を差し替える
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


TH = _load('tickebo_harvest')
BK = _load('build_tickebo_entries')
if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
REPORT = 'tmp/heal_tickebo_report.txt'
URL_RE = r'ticket\.tickebo\.jp/show/event\.html\?info=(\d+)'


FS = _load('fill_slot_pref')
SHOW_RE = re.compile(r'（(?:[^（）\s]+ )?((?:R9年\s*)?\d{1,2}/\d{1,2})公演）')


def _show_key(t):
    m = SHOW_RE.search(t.get('type') or '')
    return re.sub(r'\s', '', m.group(1)) if m else None


def heal_one(e, built, today=None):
    notes = []
    old_tb = [t for t in e.get('tickets') or [] if 'tickebo.jp' in (t.get('url') or '')]
    others = [t for t in e.get('tickets') or [] if 'tickebo.jp' not in (t.get('url') or '')]
    # 🆕11/26 穴①：作り直しは受付の終わった窓（予定枚数終了など）を出さない → 締切がまだ先の古い枠が消えた
    #   （56115 高嶋ちさ子 東京 12/23＝画面は「予定枚数終了」）。作り直しに同じ公演日の枠が無く、締切が今日以降の古い枠は残して報告する（印は人が売り場を見て付ける）
    today = today or datetime.date.today().isoformat()
    newkeys = {_show_key(t) for t in built['tickets']}
    keep = [t for t in old_tb if _show_key(t) and _show_key(t) not in newkeys and (t.get('date') or '') >= today]
    for t in keep:
        notes.append('⚠️作り直しに無い枠を残した（売り場で予定枚数終了か販売終了かを見て印を付ける）: %s' % t.get('type'))
    e['tickets'] = others + built['tickets'] + keep
    # 🆕11/26 穴②：作り直した枠の括弧に県が入らない（会場名から県を当てられない）→ エントリの県が1つなら入れる（fill_slot_pref と同じ決まり）
    p = (e.get('prefecture') or '').strip()
    for t, m in FS.missing(e):
        t['type'] = t['type'][:m.start(1)] + p + ' ' + t['type'][m.start(1):]
    if not others and (built['date'] != e.get('date') or built['dateLabel'] != e.get('dateLabel')):
        notes.append('カードの日付: %s ｜ %s → %s ｜ %s' % (e.get('date'), e.get('dateLabel'), built['date'], built['dateLabel']))
        e['date'], e['dateLabel'] = built['date'], built['dateLabel']
    n = lambda s: re.sub(r'[\s　]', '', s or '')
    if n(built.get('name')) != n(e.get('name')):
        notes.append('⚠️公演名が変わった（触っていない）: %s → %s' % (e.get('name'), built.get('name')))
    if n(built.get('venue')) != n(e.get('venue')):
        notes.append('⚠️会場が変わった（触っていない）: %s → %s' % (e.get('venue'), built.get('venue')))
    return notes


def _selftest():
    e = {'name': 'A', 'venue': 'V', 'date': '2026-12-19', 'dateLabel': 'x',
         'tickets': [{'type': 'ぴあ枠', 'url': 'https://t.pia.jp/x'},
                     {'type': '旧', 'url': 'https://ticket.tickebo.jp/show/event.html?info=1'}]}
    b = {'name': 'A', 'venue': 'V', 'date': '2026-12-20', 'dateLabel': 'y',
         'tickets': [{'type': '新', 'url': 'https://ticket.tickebo.jp/show/event.html?info=1'}]}
    assert heal_one(e, b) == [] and [t['type'] for t in e['tickets']] == ['ぴあ枠', '新'] and e['date'] == '2026-12-19'
    e2 = {'name': 'A', 'venue': 'V2', 'date': '2026-12-19', 'dateLabel': 'x',
          'tickets': [{'type': '旧', 'url': 'https://ticket.tickebo.jp/show/event.html?info=1'}]}
    notes = heal_one(e2, b)
    assert e2['date'] == '2026-12-20' and e2['venue'] == 'V2' and len(notes) == 2, (e2, notes)
    # 🆕11/26 締切が先の古い枠で作り直しに無い公演日は残す・括弧に県を入れる
    e3 = {'name': 'A', 'venue': 'V', 'prefecture': '東京', 'date': '2026-12-18', 'dateLabel': 'x',
          'tickets': [{'type': '一般（山形 12/19公演）〜12/18', 'date': '2026-12-18', 'url': 'https://ticket.tickebo.jp/show/event.html?info=1'},
                      {'type': '一般（東京 12/23公演）〜12/22', 'date': '2026-12-22', 'url': 'https://ticket.tickebo.jp/show/event.html?info=1'},
                      {'type': '一般（東京 11/20公演）〜11/19', 'date': '2026-11-19', 'url': 'https://ticket.tickebo.jp/show/event.html?info=1'}]}
    b3 = {'name': 'A', 'venue': 'V', 'date': '2026-12-18', 'dateLabel': 'x',
          'tickets': [{'type': '一般（12/19公演）〜12/18', 'date': '2026-12-18', 'url': 'https://ticket.tickebo.jp/show/event.html?info=1'}]}
    n3 = heal_one(e3, b3, today='2026-11-26')
    ty3 = [t['type'] for t in e3['tickets']]
    assert ty3 == ['一般（東京 12/19公演）〜12/18', '一般（東京 12/23公演）〜12/22'], ty3
    assert len(n3) == 1 and '12/23' in n3[0], n3
    print('selftest OK: チケットボードの枠だけ差し替え/チケットボードだけのカードは日付も直す/名前・会場は報告だけ/締切が先の消えた公演日は残す/括弧に県')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ids', default='')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--sleep', type=float, default=3.0)
    a = ap.parse_args([x for x in sys.argv[1:] if x != '--selftest'])
    if a.ids:
        want = {int(x) for x in re.findall(r'\d+', a.ids)}
    else:
        want = {int(x) for x in re.findall(r'🚨 id=(\d+)', io.open('tmp/gate_tickebo_report.txt', encoding='utf-8').read())}
    src = io.open('index.html', encoding='utf-8', newline='').read()
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
    events = json.loads(m.group(2))
    site = TH.Site(a.sleep)
    now = datetime.datetime.now(TH.JST).replace(tzinfo=None)
    today = now.date().isoformat()
    rep = io.open(REPORT, 'w', encoding='utf-8')
    done, empty, err = 0, [], []
    for e in events:
        if e['id'] not in want:
            continue
        nos = sorted({u for t in (e.get('tickets') or []) + [{'url': (e.get('links') or {}).get('tickebo')}]
                      for u in re.findall(URL_RE, t.get('url') or '')})
        if len(nos) != 1:
            err.append((e['id'], nos, '受付ページが1つでない'))
            continue
        try:
            d = site.sales(nos[0])
        except Exception as ex:
            err.append((e['id'], nos, str(ex)[:60]))
            continue
        cats = [c for c in re.sub(r'^tickebo:', '', e.get('_srcgenre') or '').split(',') if c]
        srcd = {'id': int(nos[0]), 'url': 'https://ticket.tickebo.jp/show/event.html?info=%s' % nos[0], 'top': {'cats': cats},
                'data': {k: d.get(k) for k in ('eventGroup', 'sales', 'events')}}
        built, why = BK.build(srcd, today, now)
        if not built:
            empty.append((e, why))
            continue
        old = [t for t in e.get('tickets') or [] if 'tickebo.jp' in (t.get('url') or '')]
        rep.write('\n■ id=%s %s  チケットボード枠 %d → %d\n' % (e['id'], (e.get('name') or '')[:44], len(old), len(built['tickets'])))
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
    sys.stderr.write('heal_tickebo: healed=%d empty=%d fetcherr=%d apply=%s -> %s\n' % (done, len(empty), len(err), a.apply, REPORT))
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
