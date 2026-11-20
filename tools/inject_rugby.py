# -*- coding: utf-8 -*-
"""TicketRugby の組み上がりを新着プール（genre:"new"）に投入する（inject_bleague.py と同じ形）。

  python tools/inject_rugby.py tmp/x1120/newv/rugby/built.json            … 調べるだけ（下見）
  python tools/inject_rugby.py tmp/x1120/newv/rugby/built.json --apply    … 書き込む
  python tools/inject_rugby.py --selftest

## 二重登録を外す
- ① 発売情報のページの URL（`ticketrugby.jp/ticket_release_info/<番号>`）が既に index.html にある → 入れない
- ② **対戦カード（ホーム×アウェイ）× 試合日** が登録と一致 → 入れずに「ボタンを足す候補」（`--buttons`）
     登録（ぴあ）は「東京サンゴリアス対ブラックラムズ東京 NTTジャパンラグビー…」／出演者「A／B」の形。
     🚨チーム名の書き方が売り場で違う（「東京サントリーサンゴリアス」と「東京サンゴリアス」）＝出演者の欄の組でも当てる。
     🚨同じ試合でも売り場が違う＝畳むかどうかは人が見る（[[feedback_sports_home_away_never_merge]]）
- ③ 名前（出演者 or 公演名）× 試合日 が一致 → ②と同じ扱い
## 書き込み（--apply の時だけ）＝inject_bleague と同じ（id 採番・NEW_ORDER・CRLF）
🚨投入の前に `gate_rugby_slots.py --built <組み上がり>` を通して exit 0 を確かめる。
🚨index.html に TicketRugby のボタン（linkDefs の key "ticketrugby"）がまだ無い＝足すまでボタンが出ない。
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
spec = importlib.util.spec_from_file_location('inject_bleague', os.path.join(HERE, 'inject_bleague.py'))
IB = importlib.util.module_from_spec(spec)
spec.loader.exec_module(IB)            # norm / pair_of / show_days（決まりは同じ）
if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
PATH = 'index.html'
URL_RE = r'ticketrugby\.jp/ticket_release_info/(\d+)'
KEY = 'ticketrugby'


def pairs_of(e):
    """名前の「A対B」と出演者の「A／B」の両方（チーム名の書き方が名前と出演者で違う時がある）"""
    out = set()
    p = IB.pair_of(e)
    if p:
        out.add(p)
    parts = [x for x in re.split(r'／', e.get('artist') or '') if x.strip()]
    if len(parts) == 2:
        out.add((IB.norm(parts[0]), IB.norm(parts[1])))
    return out


def index_keys(EVENTS):
    by_pair, by_name = {}, {}
    for e in EVENTS:
        if not e.get('date'):
            continue
        days = IB.show_days(e)
        ps = pairs_of(e)
        for d in days:
            for p in ps:
                by_pair.setdefault((p, d), []).append(e['id'])
            for n in {IB.norm(e.get('artist')), IB.norm(e.get('name'))}:
                if n:
                    by_name.setdefault((n, d), []).append(e['id'])
    return by_pair, by_name


def classify(built, EVENTS, have_urls):
    by_pair, by_name = index_keys(EVENTS)
    put, dup, btn = [], [], []
    for e in sorted(built, key=lambda x: (x.get('date') or '', x.get('name') or '')):
        u = re.findall(URL_RE, e['links'].get(KEY) or '')
        if set(u) & have_urls:
            dup.append((e, '発売情報のページの URL が既に登録にある'))
            continue
        hit = set()
        for p in pairs_of(e):
            hit |= set(by_pair.get((p, e['date']), []))
        hit |= set(by_name.get((IB.norm(e.get('artist')), e['date']), []))
        hit |= set(by_name.get((IB.norm(e.get('name')), e['date']), []))
        # 名前の後ろの「（会場）」はこちらで足したもの＝外した名前でも当てる（ぴあ「…3回戦／花園」）
        core = re.sub(r'（[^（）]*(?:（[^（）]*）[^（）]*)?）$', '', e.get('name') or '')
        hit |= set(by_name.get((IB.norm(core), e['date']), []))
        if hit:
            btn.append((e, sorted(hit)))
            continue
        put.append(e)
    return put, dup, btn


def _selftest():
    EV = [{'id': 1, 'artist': 'ブラックラムズ東京／東京サンゴリアス',
           'name': 'ブラックラムズ東京対東京サントリーサンゴリアス／プレシーズンマッチ', 'date': '2026-11-21',
           'dateLabel': '2026年11月21日(土)', 'tickets': [], 'links': {}},
          {'id': 3, 'artist': '[大学]大会', 'name': '[大学]大会 ３回戦／花園', 'date': '2026-12-13', 'tickets': [], 'links': {}},
          {'id': 2, 'artist': 'X', 'name': 'Y', 'date': '2026-12-24', 'tickets': [],
           'links': {'ticketrugby': 'https://ticketrugby.jp/ticket_release_info/99'}}]

    def mk(name, artist, date, gid):
        return {'artist': artist, 'name': name, 'date': date, 'dateLabel': '', 'tickets': [],
                'links': {'ticketrugby': 'https://ticketrugby.jp/ticket_release_info/%d' % gid}}
    built = [mk('ブラックラムズ東京対東京サントリーサンゴリアス／プレシーズンマッチ（リコー総合グラウンド）',
                'ブラックラムズ東京／東京サンゴリアス', '2026-11-21', 5),     # ② 対戦カード×日
             mk('A対B（会場）', 'A／B', '2026-12-01', 6),
             mk('［大学］大会 3回戦／花園（花園ラグビー場）', '未定', '2026-12-13', 7),    # 後ろの（会場）を外して名前×日
             mk('Z', 'Z', '2026-12-24', 99)]                                   # ① URL
    put, dup, btn = classify(built, EV, {'99'})
    assert len(put) == 1 and len(dup) == 1 and [b[1] for b in btn] == [[1], [3]], (put, dup, btn)
    print('selftest OK: ①URL重複/②対戦カード（名前・出演者の両方）×試合日＝ボタン候補')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--report', default='tmp/inject_rugby_report.txt')
    ap.add_argument('--buttons', default='tmp/rugby_button_cands.json')
    a = ap.parse_args()
    src = json.load(io.open(a.src, encoding='utf-8'))
    built = src['entries'] if isinstance(src, dict) else src
    h = io.open(PATH, encoding='utf-8', newline='').read()
    NL = '\r\n' if '\r\n' in h else '\n'
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
    EVENTS = json.loads(m.group(2))
    have_urls = set(re.findall(URL_RE, h))
    put, dup, btn = classify(built, EVENTS, have_urls)
    lb = json.load(io.open('.claude/state/last_batch.json', encoding='utf-8'))['batches']
    nid = max([e['id'] for e in EVENTS] + [b.get('id_to') or 0 for b in lb])
    for e in put:
        nid += 1
        e['id'] = nid
    byid = {e['id']: e for e in EVENTS}
    json.dump([{KEY: e['links'][KEY], 'name': e['name'], 'artist': e['artist'], 'date': e['date'], 'venue': e['venue'],
                'match': [{'id': i, 'name': byid[i].get('name'), 'artist': byid[i].get('artist'), 'venue': byid[i].get('venue'),
                           'date': byid[i].get('date'), 'genre': byid[i].get('genre'),
                           'links': [k for k, v in (byid[i].get('links') or {}).items() if v]} for i in ids[:6]],
                'tickets': e['tickets']} for e, ids in btn],
              io.open(a.buttons, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    rep = io.open(a.report, 'w', encoding='utf-8')
    rep.write('=== inject_rugby (%s) %s ===\n' % (datetime.date.today().isoformat(), a.src))
    rep.write('組み上がり %d件 → 投入 %d / URL重複 %d / ボタン候補（対戦カード・名前×試合日が一致）%d\n'
              % (len(built), len(put), len(dup), len(btn)))
    if put:
        rep.write('  投入する id %d〜%d\n' % (put[0]['id'], put[-1]['id']))
    rep.write('\n--- ボタンを足す候補（入れない・%s）---\n' % a.buttons)
    for e, ids in btn:
        rep.write('  %s 試合%s → 既存 id%s\n    %s\n' % (e['name'][:50], e['date'], ids[:6], e['links'][KEY]))
    rep.write('\n--- URLが既にある（入れない）---\n')
    for e, why in dup:
        rep.write('  %s 試合%s … %s\n' % (e['name'][:44], e['date'], why))
    rep.write('\n--- 投入する ---\n')
    for e in put:
        rep.write('id%d\t%s\t%s\t%s\t%s\t%s\t枠%d\n' % (e['id'], e.get('_genre') or '(空)', e['name'][:50], e['dateLabel'][:26],
                                                    e['venue'][:22], e.get('prefecture') or '(県なし)', len(e['tickets'])))
    if a.apply and put:
        for e in put:
            EVENTS.append({'id': e['id'], **{k: v for k, v in e.items() if k not in ('id', '_skipped_slots')}})
        mo = re.search(r'(NEW_ORDER\s*=\s*)\[([0-9,\s]*)\]', h)
        cur = [int(x) for x in re.findall(r'\d+', mo.group(2))]
        merged = cur + [e['id'] for e in put if e['id'] not in cur]
        h2 = re.sub(r'(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]', r'\g<1>' + '[' + ', '.join(map(str, merged)) + ']', h, count=1)
        m2 = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h2, re.S)
        bak = 'index.html.bak_%s_rugby' % datetime.date.today().strftime('%m%d')
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
    sys.stderr.write('inject_rugby: put=%d dup=%d buttons=%d apply=%s -> %s\n' % (len(put), len(dup), len(btn), a.apply, a.report))


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        _selftest()
        sys.exit(0)
    main()
