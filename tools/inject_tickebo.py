# -*- coding: utf-8 -*-
"""チケットボードの組み上がりを新着プール（genre:"new"）に投入する（inject_ticketdive.py と同じ形）。

  python tools/inject_tickebo.py tmp/x1120/newv/tickebo/built.json            … 調べるだけ（下見）
  python tools/inject_tickebo.py tmp/x1120/newv/tickebo/built.json --apply    … 書き込む
  python tools/inject_tickebo.py --selftest

## 二重登録を外す（inject_ticketdive と同じ決まり＝関数を借りる）
- ① 受付ページの URL（`ticket.tickebo.jp/show/event.html?info=<番号>`）が既に index.html にある → 入れない
- ② 正規化した名前（出演者 or 公演名・題の芯）× 公演日（カードの公演日のどれか）が登録と一致 → 入れずに「ボタンを足す候補」（`--buttons`）
- ③ 同名の登録あり（公演日は違う）→ ⚠️入れずに報告。`--same-name-ok` で入れる
## 書き込み（--apply の時だけ）＝inject_ticketdive と同じ（id 採番・NEW_ORDER・CRLF）
🚨投入の前に `gate_tickebo_slots.py --built <組み上がり>` を通して exit 0 を確かめる。
🚨index.html にチケットボードのボタン（linkDefs の key "tickebo"）がまだ無い＝足すまでボタンが出ない。
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
spec = importlib.util.spec_from_file_location('inject_ticketdive', os.path.join(HERE, 'inject_ticketdive.py'))
TD = importlib.util.module_from_spec(spec)
spec.loader.exec_module(TD)           # norm / core_title / index_keys / show_dates（決まりは同じ）
if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
PATH = 'index.html'
URL_RE = r'ticket\.tickebo\.jp/show/event\.html\?info=(\d+)'
KEY = 'tickebo'


def show_days(e):
    """カードの公演日＝dateLabel の両端・date・枠の「M/D公演」（範囲の dateLabel の間の日は枠の公演日で拾う）"""
    days = TD.show_dates(e)
    lo, hi = min(days), max(days)
    for t in e.get('tickets') or []:
        for m in re.finditer(r'(?:R(\d+)年 )?(\d{1,2})/(\d{1,2})(?: \d{1,2}:\d{2})?(?:〜[^）]*)?公演', t.get('type') or ''):
            ys = [2018 + int(m.group(1))] if m.group(1) else range(int(lo[:4]), int(hi[:4]) + 1)
            for y in ys:
                try:
                    d = datetime.date(y, int(m.group(2)), int(m.group(3))).isoformat()
                except ValueError:
                    continue
                if lo <= d <= hi:
                    days.add(d)
    return days


def classify(built, EVENTS, have_urls, same_name_ok):
    namedate, by_name = TD.index_keys(EVENTS)
    put, dup, btn, maybe = [], [], [], []
    for e in sorted(built, key=lambda x: (x.get('date') or '', x.get('name') or '')):
        u = re.findall(URL_RE, e['links'].get(KEY) or '')
        if set(u) & have_urls:
            dup.append((e, '受付ページの URL が既に登録にある'))
            continue
        na, nn = TD.norm(e.get('artist')), TD.norm(e.get('name'))
        ct = TD.core_title(e.get('name'))
        keys = [na, nn] + ([ct] if len(ct) >= 4 else [])
        hit_nd = sorted({i for d in show_days(e) for k in keys for i in namedate.get((k, d), [])})
        if hit_nd:
            btn.append((e, hit_nd))
            continue
        hit = sorted(set((by_name.get(na) or []) + (by_name.get(nn) or [])))
        if hit and not same_name_ok:
            maybe.append((e, '同名の登録あり id%s' % hit[:6]))
            continue
        if hit:
            e['_samename'] = hit[:6]
        put.append(e)
    return put, dup, btn, maybe


def _selftest():
    EV = [{'id': 1, 'artist': 'NMIXX', 'name': 'NMIXX JAPAN DEBUT SHOWCASE', 'date': '2026-12-13',
           'dateLabel': '2026年12月12日(土)〜2026年12月13日(日)', 'tickets': [], 'links': {}},
          {'id': 2, 'artist': 'Z', 'name': 'Z', 'date': '2026-12-24', 'tickets': [],
           'links': {'tickebo': 'https://ticket.tickebo.jp/show/event.html?info=9'}}]

    def mk(artist, name, date, no, label=''):
        return {'artist': artist, 'name': name, 'date': date, 'dateLabel': label, 'tickets': [],
                'links': {KEY: 'https://ticket.tickebo.jp/show/event.html?info=%d' % no}}
    built = [mk('NMIXX', 'NMIXX SHOWCASE', '2026-12-13', 5, '2026年12月12日(土)〜2026年12月13日(日)'),   # ② 名前×日
             mk('NMIXX', '別のツアー', '2027-03-01', 6),                                                 # ③ 同名・別の日
             mk('Z', 'Z', '2026-12-24', 9),                                                              # ① URL
             mk('W', '新しい公演', '2026-12-01', 7)]
    put, dup, btn, maybe = classify(json.loads(json.dumps(built)), EV, {'9'}, False)
    assert len(put) == 1 and len(dup) == 1 and len(btn) == 1 and btn[0][1] == [1] and len(maybe) == 1, (put, dup, btn, maybe)
    print('selftest OK: ①URL重複/②名前×公演日＝ボタン候補/③同名（--same-name-ok で入れる）')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--report', default='tmp/inject_tickebo_report.txt')
    ap.add_argument('--buttons', default='tmp/tickebo_button_cands.json')
    ap.add_argument('--same-name-ok', action='store_true')
    a = ap.parse_args()
    src = json.load(io.open(a.src, encoding='utf-8'))
    built = src['entries'] if isinstance(src, dict) else src
    h = io.open(PATH, encoding='utf-8', newline='').read()
    NL = '\r\n' if '\r\n' in h else '\n'
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
    EVENTS = json.loads(m.group(2))
    have_urls = set(re.findall(URL_RE, h))
    put, dup, btn, maybe = classify(built, EVENTS, have_urls, a.same_name_ok)
    lb = json.load(io.open('.claude/state/last_batch.json', encoding='utf-8'))['batches']
    nid = max([e['id'] for e in EVENTS] + [b.get('id_to') or 0 for b in lb])
    for e in put:
        nid += 1
        e['id'] = nid
    byid = {e['id']: e for e in EVENTS}
    json.dump([{KEY: e['links'][KEY], 'name': e['name'], 'artist': e['artist'], 'date': e['date'], 'dateLabel': e['dateLabel'],
                'venue': e['venue'],
                'match': [{'id': i, 'name': byid[i].get('name'), 'artist': byid[i].get('artist'), 'venue': byid[i].get('venue'),
                           'date': byid[i].get('date'), 'genre': byid[i].get('genre'),
                           'links': [k for k, v in (byid[i].get('links') or {}).items() if v]} for i in ids[:6]],
                'tickets': e['tickets']} for e, ids in btn],
              io.open(a.buttons, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    rep = io.open(a.report, 'w', encoding='utf-8')
    rep.write('=== inject_tickebo (%s) %s ===\n' % (datetime.date.today().isoformat(), a.src))
    rep.write('組み上がり %d件 → 投入 %d / URL重複 %d / ボタン候補（名前×公演日が一致）%d / ⚠️同名で要確認 %d\n'
              % (len(built), len(put), len(dup), len(btn), len(maybe)))
    if put:
        rep.write('  投入する id %d〜%d\n' % (put[0]['id'], put[-1]['id']))
    rep.write('\n--- ボタンを足す候補（入れない・%s）---\n' % a.buttons)
    for e, ids in btn:
        rep.write('  %s 公演%s → 既存 id%s\n    %s\n' % (e['name'][:44], e['date'], ids[:6], e['links'][KEY]))
    rep.write('\n--- ⚠️同名の登録あり（入れない）---\n')
    for e, why in maybe:
        rep.write('  %s 公演%s … %s\n    %s\n' % (e['name'][:44], e['date'], why, e['links'][KEY]))
    rep.write('\n--- URLが既にある（入れない）---\n')
    for e, why in dup:
        rep.write('  %s 公演%s … %s\n' % (e['name'][:40], e['date'], why))
    rep.write('\n--- 投入する ---\n')
    for e in put:
        rep.write('id%d\t%s\t%s\t%s\t%s\t%s\t枠%d\n' % (e['id'], e.get('_genre') or '(空)', e['name'][:44], e['dateLabel'][:26],
                                                    e['venue'][:22], e.get('prefecture') or '(県なし)', len(e['tickets'])))
    if a.apply and put:
        for e in put:
            EVENTS.append({'id': e['id'], **{k: v for k, v in e.items() if k not in ('id', '_skipped_slots')}})
        mo = re.search(r'(NEW_ORDER\s*=\s*)\[([0-9,\s]*)\]', h)
        cur = [int(x) for x in re.findall(r'\d+', mo.group(2))]
        merged = cur + [e['id'] for e in put if e['id'] not in cur]
        h2 = re.sub(r'(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]', r'\g<1>' + '[' + ', '.join(map(str, merged)) + ']', h, count=1)
        m2 = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h2, re.S)
        bak = 'index.html.bak_%s_tickebo' % datetime.date.today().strftime('%m%d')
        io.open(bak, 'w', encoding='utf-8', newline='').write(h)
        io.open(PATH, 'w', encoding='utf-8', newline='').write(
            h2[:m2.start()] + m2.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
            + m2.group(3) + h2[m2.end():])
        h3 = io.open(PATH, encoding='utf-8', newline='').read()
        ev3 = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h3, re.S).group(1))
        pool = {x['id'] for x in ev3 if x.get('genre') == 'new'}
        arr = set(json.loads(re.search(r'const NEW_ORDER = (\[[^\]]*\])', h3, re.S).group(1)))
        rep.write('\nEVENTS %d件 / 新着プール %d件 / NEW_ORDER %d件\n' % (len(ev3), len(pool), len(arr)))
        raw = open(PATH, 'rb').read()
        rep.write('CRCRLF %d / 素のLF %d （どちらも0が正）\n' % (raw.count(b'\r\r\n'), len(re.findall(rb'(?<!\r)\n', raw))))
        assert arr == pool, '新着プールとNEW_ORDERがズレている'
        rep.write('backup: %s\n' % bak)
    rep.close()
    sys.stderr.write('inject_tickebo: put=%d dup=%d buttons=%d samename=%d apply=%s -> %s\n'
                     % (len(put), len(dup), len(btn), len(maybe), a.apply, a.report))


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        _selftest()
        sys.exit(0)
    main()
