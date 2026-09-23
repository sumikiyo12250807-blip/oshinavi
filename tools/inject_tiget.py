# -*- coding: utf-8 -*-
"""TIGETの組み上がりを新着プール（genre:"new"）に投入する恒久ツール。

  python tools/inject_tiget.py tmp/built_tiget_MMDD.json            … 調べるだけ
  python tools/inject_tiget.py tmp/built_tiget_MMDD.json --apply    … 書き込む

## やること

1. **二重登録を外す**
   - ① TIGETのURL（`tiget.net/events/<id>`）が既に index.html にある → 入れない
   - ② 正規化した名前 × 公演日 が登録と一致 → ⚠️**入れずに報告**（別の売り場で登録済みの疑い）
   - ③ 同名の登録がある → ⚠️入れずに報告（畳む先があるかは人が見る）
2. **idは本番の番号で振る**＝いまの最大id と `last_batch.json` の最大 id_to の次から
   （削除済みidは再利用しない＝[[feedback_candidate_list_stable_numbering]]）
3. **NEW_ORDER は後ろに追記**（上書きすると同日2回目の投入で前のバッチが新着タブから消える）
4. 書いたあと **`genre:"new"` の件数と NEW_ORDER の件数が一致するか数える**
   （[[feedback_new_order_array]]＝ズレると新着タブが壊れる）
5. index.html は CRLF。**json.dumps の改行を CRLF に直してから書く**
   （[[feedback_index_html_crlf_preserve]]＝LF化すると sort_guard が誤ブロック）

🚨**投入の前に `tools/gate_tiget_slots.py` を通して exit 0 を確かめる**（投入後にも回す）。
🚨**ぴあ以外なので振り分けはユーザーの確認後**＝ここは `genre:"new"` で止める。
"""
import argparse
import datetime
import io
import json
import re
import sys
import unicodedata

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
PATH = 'index.html'


def norm(s):
    s = unicodedata.normalize('NFKC', s or '').lower()
    return re.sub(r'[\s　・･,，.。!！?？~〜\-—–_/／\(\)（）\[\]【】「」『』"\'’]', '', s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--report', default='tmp/inject_tiget_report.txt')
    # 🚨🆕2026-09-23＝③「同名の登録あり（**公演日は違う**）」を入れられるようにした。
    #   ②「名前×公演日が一致」は今までどおり止める（本当の二重登録）。
    #   ③はTIGETに多い**定期公演のvol.違い**（I☆Cicle vol.95／Teamくれれっ娘！Vol.1380 など）で、
    #   既存も vol. ごとに別エントリで登録している＝止めると**別の日の公演を丸ごと落とす**。
    #   実測 2026-09-23 夜＝要確認96件のうち88件がこれだった（[[feedback_harvest_name_dedup_blindspot]]
    #   ＝名前で重複を判定すると巻き添えが出る、と同じ型）。
    ap.add_argument('--same-name-ok', action='store_true')
    a = ap.parse_args()

    src = json.load(open(a.src, encoding='utf-8'))
    built = src['entries'] if isinstance(src, dict) else src
    h = io.open(PATH, encoding='utf-8', newline='').read()
    NL = '\r\n' if '\r\n' in h else '\n'
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
    EVENTS = json.loads(m.group(2))

    have_urls = set(re.findall(r'tiget\.net/events/(\d+)', h))
    namedate, by_name = set(), {}
    for e in EVENTS:
        blob = json.dumps(e, ensure_ascii=False)
        days = set(re.findall(r'\d{4}-\d{2}-\d{2}', blob))
        for n in {norm(e.get('artist')), norm(e.get('name'))}:
            if not n:
                continue
            by_name.setdefault(n, []).append(e['id'])
            for d in days:
                namedate.add((n, d))

    put, dup, maybe = [], [], []
    for e in sorted(built, key=lambda x: (x.get('date') or '', x.get('name') or '')):
        ids = {x for u in [e['links'].get('tiget')] + (e.get('_merged_from') or [])
               for x in re.findall(r'/events/(\d+)', u or '')}
        if ids & have_urls:
            dup.append((e, 'TIGETのURLが既に登録にある %s' % sorted(ids & have_urls)))
            continue
        na, nn = norm(e.get('artist')), norm(e.get('name'))
        if (na, e['date']) in namedate or (nn, e['date']) in namedate:
            maybe.append((e, '名前×公演日が登録と一致'))
            continue
        hit = sorted(set((by_name.get(na) or []) + (by_name.get(nn) or [])))
        if hit and not a.same_name_ok:
            maybe.append((e, '同名の登録あり id%s' % hit[:6]))
            continue
        if hit:
            e['_samename'] = hit[:6]     # 後から追える印（畳む先の候補）
        put.append(e)

    lb = json.load(io.open('.claude/state/last_batch.json', encoding='utf-8'))['batches']
    nid = max([e['id'] for e in EVENTS] + [b.get('id_to') or 0 for b in lb])
    for e in put:
        nid += 1
        e['id'] = nid

    rep = io.open(a.report, 'w', encoding='utf-8')
    rep.write('=== inject_tiget (%s) %s ===\n' % (datetime.date.today().isoformat(), a.src))
    rep.write('組み上がり %d件 → 投入 %d / URL重複 %d / ⚠️要確認 %d\n'
              % (len(built), len(put), len(dup), len(maybe)))
    if put:
        rep.write('  投入する id %d〜%d\n' % (put[0]['id'], put[-1]['id']))
    rep.write('\n--- ⚠️要確認（入れない）---\n')
    for e, why in maybe:
        rep.write('  %s 公演%s … %s\n    %s\n' % (e['name'][:44], e['date'], why, e['links']['tiget']))
    rep.write('\n--- URLが既にある（入れない）---\n')
    for e, why in dup:
        rep.write('  %s 公演%s … %s\n' % (e['name'][:40], e['date'], why))
    rep.write('\n--- 投入する ---\n')
    for e in put:
        rep.write('id%d\t%s\t%s\t%s\t%s\t枠%d\n'
                  % (e['id'], e.get('_genre'), e['name'][:44], e['dateLabel'][:26],
                     e['venue'][:22], len(e['tickets'])))

    if a.apply and put:
        for e in put:
            EVENTS.append({'id': e['id'],
                           **{k: v for k, v in e.items() if k != 'id' and not k.startswith('_merged')}})
        mo = re.search(r'(NEW_ORDER\s*=\s*)\[([0-9,\s]*)\]', h)
        cur = [int(x) for x in re.findall(r'\d+', mo.group(2))]
        merged = cur + [e['id'] for e in put if e['id'] not in cur]
        h2 = re.sub(r'(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]',
                    r'\g<1>' + '[' + ', '.join(map(str, merged)) + ']', h, count=1)
        m2 = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h2, re.S)
        bak = 'index.html.bak_%s_tiget' % datetime.date.today().strftime('%m%d')
        io.open(bak, 'w', encoding='utf-8', newline='').write(h)
        io.open(PATH, 'w', encoding='utf-8', newline='').write(
            h2[:m2.start()] + m2.group(1)
            + json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
            + m2.group(3) + h2[m2.end():])
        # 突合＝プールとNEW_ORDERの件数が合っているか
        h3 = io.open(PATH, encoding='utf-8', newline='').read()
        ev3 = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h3, re.S).group(1))
        pool = {x['id'] for x in ev3 if x.get('genre') == 'new'}
        arr = set(json.loads(re.search(r'const NEW_ORDER = (\[[^\]]*\])', h3, re.S).group(1)))
        rep.write('\nEVENTS %d件 / 新着プール %d件 / NEW_ORDER %d件\n' % (len(ev3), len(pool), len(arr)))
        rep.write('配列にあるがプールに無い %s\n' % sorted(arr - pool)[:5])
        rep.write('プールにあるが配列に無い %s\n' % sorted(pool - arr)[:5])
        raw = open(PATH, 'rb').read()
        rep.write('CRCRLF %d / 素のLF %d （どちらも0が正）\n'
                  % (raw.count(b'\r\r\n'), len(re.findall(rb'(?<!\r)\n', raw))))
        assert arr == pool, '新着プールとNEW_ORDERがズレている'
        rep.write('backup: %s\n' % bak)
    rep.close()
    sys.stderr.write('inject_tiget: put=%d dup=%d maybe=%d apply=%s -> %s\n'
                     % (len(put), len(dup), len(maybe), a.apply, a.report))


if __name__ == '__main__':
    main()
