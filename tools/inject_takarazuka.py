# -*- coding: utf-8 -*-
"""宝塚歌劇の組み上がりを新着プール（genre:"new"）に投入する（inject_ticketdive.py と同じ形）。

  python tools/inject_takarazuka.py tmp/x1120/newv/takarazuka/built.json            … 調べるだけ（下見）
  python tools/inject_takarazuka.py tmp/x1120/newv/takarazuka/built.json --apply    … 書き込む
  python tools/inject_takarazuka.py --selftest

## 二重登録を外す（物差しは inject_shochiku と同じ）
- ① 宝塚のチケットページ（kageki.hankyu.co.jp/revue/…/ticket_<劇場>.html）＋公演名が既に index.html にある → 入れない
- ② 名前（公演名・題の芯『』）× 公演日が登録と一致、または **同じ劇場×会期が重なる×名前の共通部分5字以上**
  （登録はぴあの「宝塚歌劇月組公演 ルナティック・シアター『天穹のアルテミス』／…」の形＝完全一致で当たらない）
  → **入れずに「ボタンを足す候補」**（`--buttons`）
- ③ 同名の登録あり（公演日は違う）→ ⚠️入れずに報告。`--same-name-ok` で入れる
## 書き込み（--apply の時だけ）
- id は いまの最大id と last_batch.json の最大 id_to の次から・NEW_ORDER に追記・CRLF を保つ
🚨投入の前に `gate_takarazuka_slots.py --built <組み上がり>` を通して exit 0 を確かめる（投入後にも回す）。
🚨index.html に宝塚のボタン（linkDefs の key "takarazuka"）がまだ無い＝足すまでボタンが出ない（枠のバッジからは飛べる）。
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


IS = _load('inject_shochiku')         # classify / have_pairs（物差しをそろえる）
IS.KEY = 'takarazuka'
if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
PATH = 'index.html'
KEY = 'takarazuka'


def _selftest():
    U = 'https://kageki.hankyu.co.jp/revue/2026/x/ticket_takarazuka.html'
    EV = [{'id': 5459, 'artist': '鳳月杏／天紫珠李', 'venue': '宝塚大劇場', 'date': '2027-01-02',
           'name': '宝塚歌劇月組公演 ルナティック・シアター『天穹のアルテミス』／レヴュー ロマン『Belle Epoque』',
           'dateLabel': '2027年1月2日(土) 兵庫', 'tickets': [], 'links': {}},
          {'id': 9, 'artist': 'a', 'venue': '東京宝塚劇場', 'date': '2027-03-28', 'name': '宝塚歌劇 月組公演 『天穹のアルテミス』',
           'dateLabel': '2027年2月13日(土)〜2027年3月28日(日) 東京', 'tickets': [], 'links': {KEY: U.replace('takarazuka.html', 'tokyo.html')}}]

    def mk(name, venue, s, e, url):
        return {'artist': '宝塚歌劇月組', 'name': name, 'venue': venue, 'date': e, 'dateLabel': '%s〜%s' % (s, e),
                'tickets': [], 'links': {KEY: url}}
    built = [mk('宝塚歌劇 月組公演 『天穹のアルテミス』『Belle Époque』', '宝塚大劇場', '2026年12月12日(土)', '2027-01-24', U),
             mk('宝塚歌劇 月組公演 『天穹のアルテミス』', '東京宝塚劇場', '2027年2月13日(土)', '2027-03-28',
                U.replace('takarazuka.html', 'tokyo.html')),
             mk('宝塚歌劇 雪組公演 『Snowing!!』', '宝塚バウホール', '2027年1月5日(火)', '2027-01-21',
                U.replace('x/ticket_takarazuka', 'y/ticket_bow'))]
    put, dup, btn, maybe = IS.classify(json.loads(json.dumps(built)), EV, IS.have_pairs(EV), False)
    assert [e['name'] for e in put] == ['宝塚歌劇 雪組公演 『Snowing!!』'], put
    assert len(dup) == 1 and [x[1] for x in btn] == [[5459]], (dup, btn)
    print('selftest OK: ①ページ＋公演名/②同じ劇場×会期×名前の共通部分（ぴあの長い題）＝ボタン候補/別の公演は入れる')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--report', default='tmp/inject_takarazuka_report.txt')
    ap.add_argument('--buttons', default='tmp/takarazuka_button_cands.json', help='②ボタンを足す候補の出力先')
    ap.add_argument('--same-name-ok', action='store_true')
    a = ap.parse_args()

    src = json.load(io.open(a.src, encoding='utf-8'))
    built = src['entries'] if isinstance(src, dict) else src
    h = io.open(PATH, encoding='utf-8', newline='').read()
    NL = '\r\n' if '\r\n' in h else '\n'
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
    EVENTS = json.loads(m.group(2))
    put, dup, btn, maybe = IS.classify(built, EVENTS, IS.have_pairs(EVENTS), a.same_name_ok)

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
    rep.write('=== inject_takarazuka (%s) %s ===\n' % (datetime.date.today().isoformat(), a.src))
    rep.write('組み上がり %d件 → 投入 %d / ページ＋名前が重複 %d / ボタン候補（名前×公演日・劇場×会期が一致）%d / ⚠️同名で要確認 %d\n'
              % (len(built), len(put), len(dup), len(btn), len(maybe)))
    if put:
        rep.write('  投入する id %d〜%d\n' % (put[0]['id'], put[-1]['id']))
    rep.write('\n--- ボタンを足す候補（入れない・%s）---\n' % a.buttons)
    for e, ids in btn:
        rep.write('  %s 公演%s → 既存 id%s %s\n    %s\n' % (e['name'][:44], e['date'], ids[:6],
                                                          [(byid[i].get('name') or '')[:30] for i in ids[:3]], e['links'][KEY]))
    rep.write('\n--- ⚠️同名の登録あり（入れない）---\n')
    for e, why in maybe:
        rep.write('  %s 公演%s … %s\n    %s\n' % (e['name'][:44], e['date'], why, e['links'][KEY]))
    rep.write('\n--- ページ＋名前が既にある（入れない）---\n')
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
        bak = 'index.html.bak_%s_takarazuka' % datetime.date.today().strftime('%m%d')
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
    sys.stderr.write('inject_takarazuka: put=%d dup=%d buttons=%d samename=%d apply=%s -> %s\n'
                     % (len(put), len(dup), len(btn), len(maybe), a.apply, a.report))


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        _selftest()
        sys.exit(0)
    main()
