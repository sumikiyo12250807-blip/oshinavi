# -*- coding: utf-8 -*-
"""チケットWeb松竹の組み上がりを新着プール（genre:"new"）に投入する（inject_ticketdive.py と同じ形）。

  python tools/inject_shochiku.py tmp/x1120/newv/shochiku/built.json            … 調べるだけ（下見）
  python tools/inject_shochiku.py tmp/x1120/newv/shochiku/built.json --apply    … 書き込む
  python tools/inject_shochiku.py --selftest

## 二重登録を外す
- ① 松竹の飛び先（発売日スケジュールのページ#劇場）**と公演名**の組が既に index.html にある → 入れない
  （🚨飛び先は劇場ごと＝同じ劇場の別の公演も同じ URL。URL だけで比べると別の公演を重複と見なす）
- ② 正規化した名前（公演名・題の芯『』）× 公演日（初日・千秋楽・枠の会期）が登録と一致 → **入れずに「ボタンを足す候補」**（`--buttons`）
- ③ 同名の登録あり（公演日は違う）→ ⚠️入れずに報告。`--same-name-ok` で入れる
## 書き込み（--apply の時だけ）
- id は いまの最大id と last_batch.json の最大 id_to の次から（削除済みidは再利用しない）
- NEW_ORDER は後ろに追記・書いた後に genre:"new" の件数と NEW_ORDER が一致するか数える・index.html は CRLF を保つ
🚨投入の前に `gate_shochiku_slots.py --built <組み上がり>` を通して exit 0 を確かめる（投入後にも回す）。
🚨index.html に松竹のボタン（linkDefs の key "shochiku"）がまだ無い＝足すまでボタンが出ない（枠のバッジからは飛べる）。
"""
import argparse
import datetime
import difflib
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


IT = _load('inject_ticketdive')       # norm / core_title / index_keys / show_dates（同じ物差し）
if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
PATH = 'index.html'
KEY = 'shochiku'


def own_days(e):
    """組み上がりの公演日＝初日〜千秋楽の全部の日（長い公演は他の売り場が「12/2公演」の日だけで持つことがある）。"""
    ds = sorted(IT.show_dates(e))
    lo, hi = datetime.date.fromisoformat(ds[0]), datetime.date.fromisoformat(ds[-1])
    out = set()
    while lo <= hi:
        out.add(lo.isoformat())
        lo += datetime.timedelta(days=1)
    return out


def have_pairs(EVENTS):
    return {((e.get('links') or {}).get(KEY), IT.norm(e.get('name'))) for e in EVENTS if (e.get('links') or {}).get(KEY)}


def common_len(a, b):
    """2つの文字の、いちばん長い共通部分の長さ。"""
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    return sm.find_longest_match(0, len(a), 0, len(b)).size


def venue_day_hits(e, EVENTS):
    """🆕（2026-11-20 実測）登録は「歌舞伎座 吉例顔見世大歌舞伎」「『髑髏城の七人 …』」のように頭に劇場名・『』が付く＝
    名前の完全一致で当たらない。**同じ会場（正規化して片方がもう片方を含む）× 公演日が重なる × 名前の共通部分が5字以上**も（「流白浪燦星」＝5字で当たる・会場と日が重なる時だけ）
    ボタン候補に回す（入れない・人が見る）。"""
    vn = IT.norm(e.get('venue'))
    nn = IT.norm(e.get('name'))
    days = own_days(e)
    out = []
    for x in EVENTS:
        if not x.get('date'):
            continue
        xv = IT.norm(x.get('venue'))
        if not vn or not xv or not (vn in xv or xv in vn):
            continue
        if not (days & IT.index_show_days(x)):
            ds = sorted(IT.show_dates(x))
            if not (ds and ds[0] <= max(days) and min(days) <= ds[-1]):
                continue
        if common_len(nn, IT.norm(x.get('name'))) >= 5:
            out.append(x['id'])
    return sorted(out)


def classify(built, EVENTS, have, same_name_ok):
    namedate, by_name = IT.index_keys(EVENTS)
    put, dup, btn, maybe = [], [], [], []
    for e in sorted(built, key=lambda x: (x.get('date') or '', x.get('name') or '')):
        if (e['links'].get(KEY), IT.norm(e.get('name'))) in have:
            dup.append((e, '松竹の飛び先＋公演名が既に登録にある'))
            continue
        na, nn = IT.norm(e.get('artist')), IT.norm(e.get('name'))
        ct = IT.core_title(e.get('name'))
        keys = [na, nn] + ([ct] if len(ct) >= 4 else [])
        hit_nd = sorted({i for d in own_days(e) for k in keys for i in namedate.get((k, d), [])})
        if not hit_nd:
            hit_nd = venue_day_hits(e, EVENTS)
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
    U = 'https://www1.ticket-web-shochiku.com/t/info/sale_schedule_east.html#box1'
    EV = [{'id': 1, 'artist': '十二月大歌舞伎', 'name': '十二月大歌舞伎', 'date': '2026-12-25',
           'dateLabel': '2026年12月2日(水)〜2026年12月25日(金) 東京', 'tickets': [], 'links': {}},
          {'id': 2, 'artist': 'X', 'name': '新春浅草歌舞伎', 'date': '2026-01-26', 'dateLabel': '2026年1月2日(金)〜2026年1月26日(月) 東京',
           'tickets': [], 'links': {}},
          {'id': 3, 'artist': 'A', 'name': '吉例顔見世大歌舞伎', 'date': '2026-11-25', 'tickets': [], 'links': {KEY: U}},
          {'id': 4, 'artist': 'B', 'name': '舞台『組曲虐殺』', 'date': '2026-11-10', 'dateLabel': '2026年11月10日(火) 京都',
           'tickets': [], 'links': {}}]

    def mk(name, s, e, url=U):
        return {'artist': name, 'name': name, 'date': e, 'dateLabel': '%s〜%s' % (s, e), 'tickets': [],
                'links': {KEY: url}}
    built = [mk('十二月大歌舞伎', '2026年12月2日(水)', '2026-12-25'),                       # ② 名前×公演日
             mk('新春浅草歌舞伎', '2027年1月2日(土)', '2027-01-26'),                        # ③ 同名・別の年
             mk('吉例顔見世大歌舞伎', '2026年11月1日(日)', '2026-11-25'),                   # ① 飛び先＋名前
             mk('初春大歌舞伎', '2027年1月3日(日)', '2027-01-27'),                          # 同じ飛び先・別の公演＝入れる
             mk('爆笑喜劇『組曲虐殺』', '2026年11月3日(火)', '2026-11-25')]                     # ② 題の芯×会期の中の日
    put, dup, btn, maybe = classify(json.loads(json.dumps(built)), EV, have_pairs(EV), False)
    assert [e['name'] for e in put] == ['初春大歌舞伎'], put
    assert len(dup) == 1 and sorted(x[1] for x in btn) == [[1], [4]] and len(maybe) == 1, (dup, btn, maybe)
    # 頭に劇場名が付いた登録＝同じ会場×公演日が重なる×共通部分5字以上でボタン候補（別の会場・別の時期は当てない）
    EV2 = [{'id': 7, 'artist': 'x', 'name': '歌舞伎座 吉例顔見世大歌舞伎', 'venue': '歌舞伎座', 'date': '2026-11-25',
            'dateLabel': '2026年11月1日(日)〜2026年11月25日(水)', 'tickets': [], 'links': {}},
           {'id': 8, 'artist': 'y', 'name': '吉例顔見世大歌舞伎', 'venue': '南座', 'date': '2026-11-25',
            'dateLabel': '2026年11月1日(日)〜2026年11月25日(水)', 'tickets': [], 'links': {}}]
    b2 = dict(mk('吉例顔見世大歌舞伎 特別', '2026年11月1日(日)', '2026-11-25'), venue='歌舞伎座')
    assert classify([b2], EV2, set(), False)[2][0][1] == [7]
    b3 = dict(mk('吉例顔見世大歌舞伎 特別', '2027年11月1日(月)', '2027-11-25'), venue='歌舞伎座')
    assert classify([b3], EV2, set(), True)[0], '別の年は当てない'
    print('selftest OK: ①飛び先＋公演名/②名前・題の芯×会期の日＝ボタン候補/③同名/同じ劇場の別公演は入れる/'
          '会場×公演日×名前の共通部分')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--report', default='tmp/inject_shochiku_report.txt')
    ap.add_argument('--buttons', default='tmp/shochiku_button_cands.json', help='②ボタンを足す候補の出力先')
    ap.add_argument('--same-name-ok', action='store_true')
    a = ap.parse_args()

    src = json.load(io.open(a.src, encoding='utf-8'))
    built = src['entries'] if isinstance(src, dict) else src
    h = io.open(PATH, encoding='utf-8', newline='').read()
    NL = '\r\n' if '\r\n' in h else '\n'
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
    EVENTS = json.loads(m.group(2))
    put, dup, btn, maybe = classify(built, EVENTS, have_pairs(EVENTS), a.same_name_ok)

    lb = json.load(io.open('.claude/state/last_batch.json', encoding='utf-8'))['batches']
    nid = max([e['id'] for e in EVENTS] + [b.get('id_to') or 0 for b in lb])
    for e in put:
        nid += 1
        e['id'] = nid

    byid = {e['id']: e for e in EVENTS}
    json.dump([{KEY: e['links'][KEY], 'name': e['name'], 'artist': e['artist'], 'date': e['date'],
                'dateLabel': e['dateLabel'], 'venue': e['venue'],
                'match': [{'id': i, 'name': byid[i].get('name'), 'artist': byid[i].get('artist'),
                           'venue': byid[i].get('venue'), 'date': byid[i].get('date'), 'genre': byid[i].get('genre')}
                          for i in ids[:6]],
                'tickets': e['tickets']} for e, ids in btn],
              io.open(a.buttons, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    rep = io.open(a.report, 'w', encoding='utf-8')
    rep.write('=== inject_shochiku (%s) %s ===\n' % (datetime.date.today().isoformat(), a.src))
    rep.write('組み上がり %d件 → 投入 %d / 飛び先＋名前が重複 %d / ボタン候補（名前×公演日が一致）%d / ⚠️同名で要確認 %d\n'
              % (len(built), len(put), len(dup), len(btn), len(maybe)))
    if put:
        rep.write('  投入する id %d〜%d\n' % (put[0]['id'], put[-1]['id']))
    rep.write('\n--- ボタンを足す候補（入れない・%s）---\n' % a.buttons)
    for e, ids in btn:
        rep.write('  %s 公演%s → 既存 id%s %s\n    %s\n' % (e['name'][:44], e['date'], ids[:6],
                                                          ['%s' % (byid[i].get('name') or '')[:30] for i in ids[:3]],
                                                          e['links'][KEY]))
    rep.write('\n--- ⚠️同名の登録あり（入れない）---\n')
    for e, why in maybe:
        rep.write('  %s 公演%s … %s\n    %s\n' % (e['name'][:44], e['date'], why, e['links'][KEY]))
    rep.write('\n--- 飛び先＋名前が既にある（入れない）---\n')
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
        bak = 'index.html.bak_%s_shochiku' % datetime.date.today().strftime('%m%d')
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
    sys.stderr.write('inject_shochiku: put=%d dup=%d buttons=%d samename=%d apply=%s -> %s\n'
                     % (len(put), len(dup), len(btn), len(maybe), a.apply, a.report))


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        _selftest()
        sys.exit(0)
    main()
