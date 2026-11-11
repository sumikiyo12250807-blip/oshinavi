# -*- coding: utf-8 -*-
"""チケットペイの組み上がりを新着プール（genre:"new"）に投入する（inject_tiget.py と同じ形・2026-11-12 新設）。

  python tools/inject_ticketpay.py tmp/built_ticketpay_MMDD.json            … 調べるだけ（index.html は読むだけ）
  python tools/inject_ticketpay.py tmp/built_ticketpay_MMDD.json --apply    … 書き込む
  python tools/inject_ticketpay.py --selftest

## やること
1. **二重登録を外す**
   - ① チケットペイのURL（`ticketpay.jp/booking/?event_id=<番号>`）が既に index.html にある → 入れない
   - ② 正規化した名前 × 公演日 が登録と一致 → ⚠️**入れずに報告**＝**ボタンを足す候補**として `--cands` のファイルに書く
     （別の売り場で登録済み＝そのカードにチケットペイのボタン・枠を足せる）
   - ③ 同名の登録があるが公演日は違う → 入れる（定期公演の回違いを落とさない＝TIGETの 9/23 の学び）。
     `_samename` に既存の id を残す（畳む先の候補）
2. **id は本番の番号で振る**＝いまの最大 id と `last_batch.json` の最大 id_to の次から（削除済み id は再利用しない）
3. **NEW_ORDER は後ろに追記**／書いたあと **genre:"new" の件数と NEW_ORDER の件数が一致するか数える**
4. index.html は CRLF。json.dumps の改行を CRLF に直してから書く
5. 🚨**画面にチケットペイのボタン（linkDefs の key "ticketpay"）が無いまま --apply しない**
   ＝links.ticketpay を足しても画面に出ない。無ければ止める。

🚨投入の前に `tools/gate_ticketpay_slots.py --built <組み上がり>` を通して食い違い0を確かめる。
🚨ぴあ以外なので、振り分けはゲートを通ってから（[[feedback_nonpia_user_eyes_until_gate]]）＝ここは genre:"new" で止める。
"""
import argparse
import datetime
import io
import json
import re
import sys
import unicodedata

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
PATH = 'index.html'
URL_ID = re.compile(r'ticketpay\.jp/booking/\?event_id=(\d+)')


def norm(s):
    s = unicodedata.normalize('NFKC', s or '').lower()
    return re.sub(r'[\s　・･,，.。!！?？~〜～\-—–_/／\(\)（）\[\]【】「」『』"\'’&＆]', '', s)


def core(s):
    """売り場ごとの飾りを落とした名前の芯（2026-11-12 試運転で発見＝「【一般】「RING FINALE 2026 〜DDT年内最終興行〜」12/27」が
    livePocket 登録の「RING FINALE 2026 〜DDT年内最終興行〜」（id42474・同じ日）と一致しなかった）。
    頭の【一般】＜一般先行＞などの札・後ろの「12/27」「一般販売」を落とす。"""
    s = unicodedata.normalize('NFKC', s or '')
    s = re.sub(r'^\s*(?:[【<＜\[［][^】>＞\]］]{1,12}[】>＞\]］]\s*)+', '', s)
    s = re.sub(r'\s*(?:\d{1,2}/\d{1,2}(?:\([^)]*\))?|一般販売|追加販売)\s*$', '', s)
    return norm(s)


def index_keys(events, h):
    have = set(URL_ID.findall(h))
    namedate, by_name, by_date = {}, {}, {}
    for e in events:
        days = {e.get('date')} | set(re.findall(r'\d{4}-\d{2}-\d{2}', e.get('dateLabel') or '')) \
            | {t.get('date') for t in e.get('tickets') or []}
        days.discard(None)
        # 公演日（カードの date と dateLabel に出る日）。dateLabel は「2026年12月27日」形なので直す
        days |= {'%s-%02d-%02d' % (y, int(m), int(d)) for y, m, d in re.findall(r'(\d{4})年(\d{1,2})月(\d{1,2})日', e.get('dateLabel') or '')}
        names = {norm(e.get('artist')), norm(e.get('name')), core(e.get('name'))} - {''}
        for n in names:
            by_name.setdefault(n, []).append(e['id'])
            for d in days:
                namedate.setdefault((n, d), []).append(e['id'])
        for d in days:
            by_date.setdefault(d, []).append((core(e.get('name')), e['id']))
    return have, namedate, (by_name, by_date)


def classify(built, have, namedate, idx):
    by_name, by_date = idx
    put, dup, cand = [], [], []
    for e in sorted(built, key=lambda x: (x.get('date') or '', x.get('name') or '')):
        ids = set(URL_ID.findall(e['links'].get('ticketpay') or ''))
        if ids & have:
            dup.append((e, 'チケットペイのURLが既に登録にある %s' % sorted(ids & have)))
            continue
        na, nn, nc = norm(e.get('artist')), norm(e.get('name')), core(e.get('name'))
        sdays = set(re.findall(r'\d{4}-\d{2}-\d{2}', ' '.join([e['date']] + [
            '%s-%02d-%02d' % (y, int(m), int(d)) for y, m, d in re.findall(r'(\d{4})年(\d{1,2})月(\d{1,2})日', e.get('dateLabel') or '')])))
        hit = set()
        for d in sdays:
            for n in (na, nn, nc):
                hit |= set(namedate.get((n, d)) or [])
            # 芯どうしがどちらかに含まれる（8字以上）＝同じ公演の疑い（同じ日だけ見る）
            for c, i in by_date.get(d) or []:
                if len(c) >= 8 and len(nc) >= 8 and (c in nc or nc in c):
                    hit.add(i)
        hit = sorted(hit)
        if hit:
            cand.append((e, hit))
            continue
        same = sorted(set((by_name.get(na) or []) + (by_name.get(nn) or []) + (by_name.get(nc) or [])))
        if same:
            e['_samename'] = same[:6]
        put.append(e)
    return put, dup, cand


def _selftest():
    ev = [{'id': 10, 'artist': 'JAYWALK', 'name': 'JAYWALK 不思議で素敵なクリスマス', 'date': '2026-12-03', 'tickets': []},
          {'id': 11, 'artist': 'X', 'name': 'Y', 'date': '2026-12-01',
           'tickets': [{'url': 'https://www.ticketpay.jp/booking/?event_id=500'}]}]
    h = json.dumps(ev, ensure_ascii=False)
    have, nd, bn = index_keys(ev, h)
    mk = lambda i, n, d, a=None: {'name': n, 'artist': a or n, 'date': d,
                                  'links': {'ticketpay': 'https://www.ticketpay.jp/booking/?event_id=%d' % i}}
    put, dup, cand = classify([mk(500, 'Z', '2026-12-09'),                                  # ① URL
                               mk(501, 'JAYWALK　不思議で素敵なクリスマス', '2026-12-03'),   # ② 名前×日付（全角空白でも）
                               mk(502, 'JAYWALK 不思議で素敵なクリスマス', '2026-12-24'),    # ③ 同名・別の日＝入れる
                               mk(503, '新しい公演', '2026-12-24')], have, nd, bn)
    assert [x[0]['name'] for x in dup] == ['Z'], dup
    assert [(x[0]['date'], x[1]) for x in cand] == [('2026-12-03', [10])], cand
    assert sorted(x['name'] for x in put) == ['JAYWALK 不思議で素敵なクリスマス', '新しい公演'], put
    assert [x.get('_samename') for x in put if x['date'] == '2026-12-24' and 'JAY' in x['name']] == [[10]]
    # 売り場の飾り（【一般】「…」12/27）を落とした芯で一致させる（RING FINALE の取りこぼし）
    ev2 = [{'id': 42474, 'artist': 'DDT', 'name': 'RING FINALE 2026 〜DDT年内最終興行〜', 'date': '2026-12-27',
            'dateLabel': '2026年12月27日(日) 11:30開演', 'tickets': []}]
    have, nd, idx = index_keys(ev2, json.dumps(ev2, ensure_ascii=False))
    put, dup, cand = classify([mk(600, '【一般】「RING FINALE 2026 〜DDT年内最終興行〜」12/27', '2026-12-27'),
                               mk(601, '【一般】「RING FINALE 2026 〜DDT年内最終興行〜」12/27', '2026-12-28')], have, nd, idx)
    assert [(x[0]['date'], x[1]) for x in cand] == [('2026-12-27', [42474])] and len(put) == 1, (cand, put)
    print('selftest OK（①URL重複 ②名前×公演日＝ボタン候補（売り場の飾りを落とした芯・含む関係）③同名別日は入れる）')
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src', nargs='?')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--report', default='tmp/inject_ticketpay_report.txt')
    ap.add_argument('--cands', default='tmp/ticketpay_button_cands.txt',
                    help='②名前×公演日が一致＝既存カードにボタンを足す候補の書き出し先')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        sys.exit(_selftest())

    src = json.load(open(a.src, encoding='utf-8'))
    built = src['entries'] if isinstance(src, dict) else src
    h = io.open(PATH, encoding='utf-8', newline='').read()
    NL = '\r\n' if '\r\n' in h else '\n'
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
    EVENTS = json.loads(m.group(2))
    have, namedate, by_name = index_keys(EVENTS, h)
    put, dup, cand = classify(built, have, namedate, by_name)
    byid = {e['id']: e for e in EVENTS}

    lb = json.load(io.open('.claude/state/last_batch.json', encoding='utf-8'))['batches']
    nid = max([e['id'] for e in EVENTS] + [b.get('id_to') or 0 for b in lb])
    for e in put:
        nid += 1
        e['id'] = nid

    rep = io.open(a.report, 'w', encoding='utf-8')
    rep.write('=== inject_ticketpay (%s) %s apply=%s ===\n' % (datetime.date.today().isoformat(), a.src, a.apply))
    rep.write('組み上がり %d件 → 投入 %d / URL重複 %d / ボタン候補（名前×公演日が一致） %d / うち同名別日 %d\n'
              % (len(built), len(put), len(dup), len(cand), sum(1 for e in put if e.get('_samename'))))
    if put:
        rep.write('  投入する id %d〜%d（--apply なしなら仮の番号）\n' % (put[0]['id'], put[-1]['id']))
    rep.write('\n--- ボタン候補（入れない・%s に書いた）---\n' % a.cands)
    for e, hit in cand:
        rep.write('  %s 公演%s → 既存 id%s\n' % (e['name'][:44], e['date'], hit[:4]))
    rep.write('\n--- URLが既にある（入れない）---\n')
    for e, why in dup:
        rep.write('  %s 公演%s … %s\n' % (e['name'][:40], e['date'], why))
    rep.write('\n--- 投入する ---\n')
    for e in put:
        rep.write('id%d\t%s\t%s\t%s\t%s\t枠%d%s\n'
                  % (e['id'], e.get('_genre') or '(空)', e['name'][:44], e['dateLabel'][:26], e['venue'][:22],
                     len(e['tickets']), '\t同名 id%s' % e['_samename'] if e.get('_samename') else ''))
    with io.open(a.cands, 'w', encoding='utf-8') as f:
        f.write('# チケットペイ：名前×公演日が登録と一致＝既存カードにボタン（links.ticketpay）と枠を足す候補 %s\n'
                % datetime.date.today().isoformat())
        f.write('# 既存id\t既存の名前\t公演日\tチケットペイの名前\tURL\n')
        for e, hit in cand:
            for i in hit:
                f.write('%s\t%s\t%s\t%s\t%s\n' % (i, (byid.get(i, {}).get('name') or '')[:40], e['date'],
                                                  e['name'][:40], e['links']['ticketpay']))

    if a.apply and put:
        if not re.search(r'key:\s*"ticketpay"', h):
            rep.write('\n🚨止めた：画面の linkDefs に key "ticketpay" が無い＝ボタンが出ない。先に画面へ足す\n')
            rep.close()
            sys.stderr.write('inject_ticketpay: STOP linkDefs has no "ticketpay" key\n')
            sys.exit(3)
        for e in put:
            EVENTS.append({'id': e['id'], **{k: v for k, v in e.items() if k != 'id'}})
        mo = re.search(r'(NEW_ORDER\s*=\s*)\[([0-9,\s]*)\]', h)
        cur = [int(x) for x in re.findall(r'\d+', mo.group(2))]
        merged = cur + [e['id'] for e in put if e['id'] not in cur]
        h2 = re.sub(r'(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]',
                    r'\g<1>' + '[' + ', '.join(map(str, merged)) + ']', h, count=1)
        m2 = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h2, re.S)
        bak = 'index.html.bak_%s_ticketpay' % datetime.date.today().strftime('%m%d')
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
    sys.stderr.write('inject_ticketpay: put=%d dup=%d cands=%d apply=%s -> %s\n'
                     % (len(put), len(dup), len(cand), a.apply, a.report))


if __name__ == '__main__':
    main()
