# -*- coding: utf-8 -*-
"""TicketDive の組み上がりを新着プール（genre:"new"）に投入する（inject_tiget.py と同じ形）。

  python tools/inject_ticketdive.py tmp/built_ticketdive_MMDD.json            … 調べるだけ（下見）
  python tools/inject_ticketdive.py tmp/built_ticketdive_MMDD.json --apply    … 書き込む
  python tools/inject_ticketdive.py --selftest

## 二重登録を外す
- ① TicketDive の URL（`ticketdive.com/event/<url>`）が既に index.html にある → 入れない
- ② 正規化した名前（出演者 or 公演名）× 公演日 が登録と一致 → **入れずに「ボタンを足す候補」**として別ファイル
  （`--buttons`。同じ公演が別の売り場で載っている＝そのカードに TicketDive のボタンを足すかを人が見る）
- ③ 同名の登録あり（公演日は違う）→ ⚠️入れずに報告。`--same-name-ok` で入れる（定期公演の vol.違い＝TIGET と同じ）
## 書き込み（--apply の時だけ）
- id は いまの最大id と last_batch.json の最大 id_to の次から（削除済みidは再利用しない）
- NEW_ORDER は後ろに追記・書いた後に genre:"new" の件数と NEW_ORDER が一致するか数える
- index.html は CRLF を保つ
🚨投入の前に `gate_ticketdive_slots.py --built <組み上がり>` を通して exit 0 を確かめる（投入後にも回す）。
🚨index.html に TicketDive のボタン（linkDefs の key "ticketdive"）がまだ無い＝足すまでボタンが出ない。
"""
import argparse
import datetime
import io
import json
import os
import re
import sys
import unicodedata

if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
PATH = 'index.html'
URL_RE = r'ticketdive\.com/event/([A-Za-z0-9_\-.%]+)'


def norm(s):
    s = unicodedata.normalize('NFKC', s or '').lower()
    return re.sub(r'[\s　・･,，.。!！?？~〜\-—–_/／\(\)（）\[\]【】「」『』"\'’]', '', s)


def index_show_days(e):
    """登録カードの**公演日**の集合（締切・発売日は入れない＝同じ出演者の別の日の締切で当たらないように）。
    dateLabel の年月日＋date＋枠の「M/D公演」（年は dateLabel の範囲に入る年）。"""
    days = show_dates(e)
    lo, hi = min(days), max(days)
    for t in e.get('tickets') or []:
        for m in re.finditer(r'(?:R(\d+)年 )?(\d{1,2})/(\d{1,2})(?: \d{1,2}:\d{2})?公演', t.get('type') or ''):
            ys = [2018 + int(m.group(1))] if m.group(1) else range(int(lo[:4]), int(hi[:4]) + 1)
            for y in ys:
                try:
                    d = datetime.date(y, int(m.group(2)), int(m.group(3))).isoformat()
                except ValueError:
                    continue
                if lo <= d <= hi or m.group(1):
                    days.add(d)
    return days


def core_title(s):
    """題の芯＝『』の中（あれば）か、頭の［大阪公演］【東京公演】等と「舞台」「ミュージカル」を落とした題。
    （2026-11-12 実測＝TicketDive「［大阪公演］『組曲虐殺』」と登録「舞台『組曲虐殺』」が名前の完全一致で当たらなかった）"""
    s = unicodedata.normalize('NFKC', s or '')
    m = re.search(r'『([^』]{2,})』', s)
    if m:
        return '#' + norm(m.group(1))
    s = re.sub(r'^\s*(?:[\[［【(（][^\]］】)）]{0,12}[\]］】)）]\s*)+', '', s)
    s = re.sub(r'^(?:舞台|ミュージカル|朗読劇)', '', s.strip())
    return '#' + norm(s)


def index_keys(EVENTS):
    namedate, by_name = {}, {}
    for e in EVENTS:
        if not e.get('date'):
            continue
        days = index_show_days(e)
        ct = core_title(e.get('name'))
        if len(ct) >= 4:
            for d in days:
                namedate.setdefault((ct, d), []).append(e['id'])
        for n in {norm(e.get('artist')), norm(e.get('name'))}:
            if not n:
                continue
            by_name.setdefault(n, []).append(e['id'])
            for d in days:
                namedate.setdefault((n, d), []).append(e['id'])
    return namedate, by_name


def show_dates(e):
    """カードの公演日（枠の「M/D公演」は年が無いので、dateLabel の年月日から全部取る）。"""
    ds = set(re.findall(r'(\d{4})年(\d{1,2})月(\d{1,2})日', e.get('dateLabel') or ''))
    out = {'%s-%02d-%02d' % (y, int(m), int(d)) for y, m, d in ds}
    out.add(e['date'])
    return out


def classify(built, EVENTS, have_urls, same_name_ok):
    namedate, by_name = index_keys(EVENTS)
    put, dup, btn, maybe = [], [], [], []
    for e in sorted(built, key=lambda x: (x.get('date') or '', x.get('name') or '')):
        u = re.findall(URL_RE, e['links'].get('ticketdive') or '')
        if set(u) & have_urls:
            dup.append((e, 'TicketDive の URL が既に登録にある'))
            continue
        na, nn = norm(e.get('artist')), norm(e.get('name'))
        ct = core_title(e.get('name'))
        keys = [na, nn] + ([ct] if len(ct) >= 4 else [])
        hit_nd = sorted({i for d in show_dates(e) for k in keys for i in namedate.get((k, d), [])})
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
    EV = [{'id': 1, 'artist': 'COLOR of COLOR', 'name': 'COLOR of COLOR 1st YEAR', 'date': '2026-12-03',
           'tickets': [{'date': '2026-12-02'}], 'links': {}},
          {'id': 2, 'artist': 'X', 'name': 'ルージュブック定期公演', 'date': '2026-10-01', 'tickets': [], 'links': {}},
          {'id': 3, 'artist': 'Y', 'name': 'Y live', 'date': '2026-12-24', 'tickets': [],
           'links': {'ticketdive': 'https://ticketdive.com/event/ylive'}}]
    def mk(artist, name, date, url):
        return {'artist': artist, 'name': name, 'date': date, 'dateLabel': '', 'tickets': [],
                'links': {'ticketdive': 'https://ticketdive.com/event/' + url}}
    built = [mk('COLOR of COLOR', '別名', '2026-12-03', 'coc'),            # ② 名前×公演日 → ボタン候補
             mk('Z', 'ルージュブック定期公演', '2026-11-20', 'rb'),          # ③ 同名・別の日
             mk('Y', 'Y live', '2026-12-24', 'ylive'),                       # ① URL
             mk('W', '新しい公演', '2026-12-01', 'new')]
    put, dup, btn, maybe = classify(json.loads(json.dumps(built)), EV, {'ylive'}, False)
    assert [e['links']['ticketdive'][-3:] for e in put] == ['new'], put
    assert len(dup) == 1 and len(btn) == 1 and btn[0][1] == [1] and len(maybe) == 1, (dup, btn, maybe)
    put2 = classify(json.loads(json.dumps(built)), EV, {'ylive'}, True)[0]
    assert len(put2) == 2 and put2[0].get('_samename') == [2], put2
    # 題の芯（『』の中）× 公演日＝ボタン候補（ツアーの枠の「R9年 2/20公演」から公演日を取る・締切の日では当たらない）
    EV2 = [{'id': 9, 'artist': '劇団', 'name': '舞台『組曲虐殺』', 'date': '2027-04-04',
            'dateLabel': '2027年2月6日(土)〜2027年4月4日(日) 全国ツアー',
            'tickets': [{'type': '一般（大阪 R9年 2/20公演）〜2/1 23:59', 'date': '2027-02-01'}], 'links': {}}]
    b2 = [dict(mk('井上', '［大阪公演］『組曲虐殺』', '2027-02-20', 'gk'), dateLabel='2027年2月20日(土) 大阪'),
          dict(mk('井上', '［大阪公演］『組曲虐殺』', '2027-02-01', 'gk2'), dateLabel='2027年2月1日(月) 大阪')]
    _, _, btn2, _ = classify(b2, EV2, set(), True)
    assert [x[1] for x in btn2] == [[9]], btn2
    assert core_title('［大阪公演］『組曲虐殺』') == core_title('舞台『組曲虐殺』')
    assert core_title('[大阪公演]ミュージカル『アーモンド』') == core_title('ミュージカル『アーモンド』')
    print('selftest OK: ①URL重複/②名前×公演日・題の芯×公演日＝ボタン候補/③同名（--same-name-ok で入れる）')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--report', default='tmp/inject_ticketdive_report.txt')
    ap.add_argument('--buttons', default='tmp/ticketdive_button_cands.json', help='②ボタンを足す候補の出力先')
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
    json.dump([{'ticketdive': e['links']['ticketdive'], 'name': e['name'], 'artist': e['artist'], 'date': e['date'],
                'dateLabel': e['dateLabel'], 'venue': e['venue'],
                'match': [{'id': i, 'name': byid[i].get('name'), 'artist': byid[i].get('artist'),
                           'venue': byid[i].get('venue'), 'date': byid[i].get('date'), 'genre': byid[i].get('genre')}
                          for i in ids[:6]],
                'tickets': e['tickets']} for e, ids in btn],
              io.open(a.buttons, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    rep = io.open(a.report, 'w', encoding='utf-8')
    rep.write('=== inject_ticketdive (%s) %s ===\n' % (datetime.date.today().isoformat(), a.src))
    rep.write('組み上がり %d件 → 投入 %d / URL重複 %d / ボタン候補（名前×公演日が一致）%d / ⚠️同名で要確認 %d\n'
              % (len(built), len(put), len(dup), len(btn), len(maybe)))
    if put:
        rep.write('  投入する id %d〜%d\n' % (put[0]['id'], put[-1]['id']))
    rep.write('\n--- ボタンを足す候補（入れない・%s）---\n' % a.buttons)
    for e, ids in btn:
        rep.write('  %s 公演%s → 既存 id%s\n    %s\n' % (e['name'][:44], e['date'], ids[:6], e['links']['ticketdive']))
    rep.write('\n--- ⚠️同名の登録あり（入れない）---\n')
    for e, why in maybe:
        rep.write('  %s 公演%s … %s\n    %s\n' % (e['name'][:44], e['date'], why, e['links']['ticketdive']))
    rep.write('\n--- URLが既にある（入れない）---\n')
    for e, why in dup:
        rep.write('  %s 公演%s … %s\n' % (e['name'][:40], e['date'], why))
    rep.write('\n--- 投入する ---\n')
    for e in put:
        rep.write('id%d\t%s\t%s\t%s\t%s\t%s\t枠%d\n'
                  % (e['id'], e.get('_genre') or '(空)', e['name'][:44], e['dateLabel'][:26],
                     e['venue'][:22], e.get('prefecture') or '(県なし)', len(e['tickets'])))

    if a.apply and put:
        for e in put:
            EVENTS.append({'id': e['id'], **{k: v for k, v in e.items()
                                             if k not in ('id', '_prefFrom', '_unknownState')}})
        mo = re.search(r'(NEW_ORDER\s*=\s*)\[([0-9,\s]*)\]', h)
        cur = [int(x) for x in re.findall(r'\d+', mo.group(2))]
        merged = cur + [e['id'] for e in put if e['id'] not in cur]
        h2 = re.sub(r'(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]',
                    r'\g<1>' + '[' + ', '.join(map(str, merged)) + ']', h, count=1)
        m2 = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h2, re.S)
        bak = 'index.html.bak_%s_ticketdive' % datetime.date.today().strftime('%m%d')
        io.open(bak, 'w', encoding='utf-8', newline='').write(h)
        io.open(PATH, 'w', encoding='utf-8', newline='').write(
            h2[:m2.start()] + m2.group(1)
            + json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
            + m2.group(3) + h2[m2.end():])
        h3 = io.open(PATH, encoding='utf-8', newline='').read()
        ev3 = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h3, re.S).group(1))
        pool = {x['id'] for x in ev3 if x.get('genre') == 'new'}
        arr = set(json.loads(re.search(r'const NEW_ORDER = (\[[^\]]*\])', h3, re.S).group(1)))
        rep.write('\nEVENTS %d件 / 新着プール %d件 / NEW_ORDER %d件\n' % (len(ev3), len(pool), len(arr)))
        raw = open(PATH, 'rb').read()
        rep.write('CRCRLF %d / 素のLF %d （どちらも0が正）\n'
                  % (raw.count(b'\r\r\n'), len(re.findall(rb'(?<!\r)\n', raw))))
        assert arr == pool, '新着プールとNEW_ORDERがズレている'
        rep.write('backup: %s\n' % bak)
    rep.close()
    sys.stderr.write('inject_ticketdive: put=%d dup=%d buttons=%d samename=%d apply=%s -> %s\n'
                     % (len(put), len(dup), len(btn), len(maybe), a.apply, a.report))


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        _selftest()
        sys.exit(0)
    main()
