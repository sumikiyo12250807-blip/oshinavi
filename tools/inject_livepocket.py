# -*- coding: utf-8 -*-
"""livePocket の組み上がりを新着プール（genre:"new"）に投入する恒久ツール。

  python tools/inject_livepocket.py tmp/built_livepocket_MMDD.json            … 調べるだけ（下見）
  python tools/inject_livepocket.py tmp/built_livepocket_MMDD.json --apply    … 書き込む

## やること（inject_zaiko と同じ判定・同じ書き方）
1. **二重登録を外す**
   - ① livePocket のURL（`livepocket.jp/e/<id>`）が既にある → 入れない（id は英数字・主催者が付けた文字列もある）
   - ② 正規化した名前 × 公演日 × 会場 が登録と一致 → ⚠️**入れずに報告**（別の売り場で登録済みの疑い）
     🚨名前だけ・名前×公演日だけで外さない（TIGETで定期公演の vol. 違い88件を落とした＝
       [[feedback_harvest_name_dedup_blindspot]]）。同名があるだけのものは入れて、報告に「同名あり」と出す
2. idは本番の番号で振る（いまの最大id と last_batch.json の最大 id_to の次から）
3. NEW_ORDER は**後ろに追記**
4. 書いたあと `genre:"new"` の件数と NEW_ORDER の件数が一致するか数える
5. index.html は CRLF。json.dumps の改行を CRLF に直してから書く

🚨**投入の前に `tools/gate_livepocket_slots.py` を通して exit 0 を確かめる**（投入後にも --ids で回す）。
🚨ぴあ以外なので**振り分けはユーザー確認後**＝ここは `genre:"new"` で止める。
🚨購入ボタン（index.html の linkDefs／VENDOR_TICKET_KEYS／CSS と build_ai_page の VENDOR_ORDER）に
   `livepocket` が無いうちは、入れてもボタンが出ない＝先にそろえる（TIGETのときと同じ4か所）。
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
URL_RE = r'livepocket\.jp/e/([A-Za-z0-9_\-]+)'
DROP_KEYS = ('_merged', '_review', '_skipped_slots')


def norm(s):
    s = unicodedata.normalize('NFKC', s or '').lower()
    return re.sub(r'[\s　・･,，.。!！?？~〜\-—–_/／\(\)（）\[\]【】「」『』"\'’]', '', s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--limit', type=int, default=0, help='先頭N件だけ入れる（試すとき）')
    ap.add_argument('--report', default='tmp/inject_livepocket_report.txt')
    a = ap.parse_args()

    src = json.load(io.open(a.src, encoding='utf-8'))
    built = src['entries'] if isinstance(src, dict) else src
    h = io.open(PATH, encoding='utf-8', newline='').read()
    NL = '\r\n' if '\r\n' in h else '\n'
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
    EVENTS = json.loads(m.group(2))

    have_ids = set(re.findall(URL_RE, h))
    trio, by_name = set(), {}
    for e in EVENTS:
        days = set(re.findall(r'\d{4}-\d{2}-\d{2}', json.dumps(e, ensure_ascii=False)))
        nv = norm(e.get('venue'))
        for n in {norm(e.get('artist')), norm(e.get('name'))}:
            if not n:
                continue
            by_name.setdefault(n, []).append(e['id'])
            for d in days:
                trio.add((n, d, nv))

    put, dup, maybe = [], [], []
    seen_batch, seen_trio = set(), {}
    for e in sorted(built, key=lambda x: (x.get('date') or '', x.get('name') or '')):
        u = (e.get('links') or {}).get('livepocket') or ''
        ids = set(re.findall(URL_RE, u)) | {x for t in e.get('tickets') or [] for x in re.findall(URL_RE, t.get('url') or '')}
        if ids & have_ids:
            dup.append((e, 'livePocketのURLが既に登録にある %s' % sorted(ids & have_ids)))
            continue
        if ids & seen_batch:
            dup.append((e, '同じバッチの中で同じURLが2回'))
            continue
        na, nn, nv = norm(e.get('artist')), norm(e.get('name')), norm(e.get('venue'))
        if (na, e['date'], nv) in trio or (nn, e['date'], nv) in trio:
            maybe.append((e, '名前×公演日×会場が登録と一致'))
            continue
        # 🚨同じバッチの中で名前×公演日×会場が同じ別ページ（2026-09-28 実例＝POP UP の入場時間違いが8ページ）。
        #   URLが違うので畳まない（[[feedback_dedup_badges_keeps_urls]]）が、画面で見分けがつかない
        #   ことがある＝最初の1件だけ入れて、残りは要確認に回す（人が畳むか別で入れるか決める）
        bk = (nn, e['date'], nv)
        if bk in seen_trio:
            maybe.append((e, '同じバッチに名前×公演日×会場が同じ別ページあり（%s）' % seen_trio[bk]))
            continue
        seen_trio[bk] = (e.get('links') or {}).get('livepocket')
        hit = sorted(set((by_name.get(na) or []) + (by_name.get(nn) or [])))
        if hit:
            e['_samename'] = hit[:6]        # 入れる。畳む先の候補として後から追える印
        seen_batch |= ids
        put.append(e)

    rest = []
    if a.limit:
        put, rest = put[:a.limit], put[a.limit:]

    lb = json.load(io.open('.claude/state/last_batch.json', encoding='utf-8'))['batches']
    nid = max([e['id'] for e in EVENTS] + [b.get('id_to') or 0 for b in lb])
    for e in put:
        nid += 1
        e['id'] = nid

    rep = io.open(a.report, 'w', encoding='utf-8')
    rep.write('=== inject_livepocket (%s) %s apply=%s ===\n' % (datetime.date.today().isoformat(), a.src, a.apply))
    rep.write('組み上がり %d件 → 投入 %d / URL重複 %d / ⚠️要確認 %d / 今回は入れない %d\n'
              % (len(built), len(put), len(dup), len(maybe), len(rest)))
    if put:
        rep.write('  投入する id %d〜%d（下見の番号＝--apply の時点で変わることがある）\n' % (put[0]['id'], put[-1]['id']))
    rep.write('\n--- ⚠️要確認（入れない）---\n')
    for e, why in maybe:
        rep.write('  %s / %s / 公演%s … %s\n    %s\n' % (e['name'][:40], e['venue'][:20], e['date'], why,
                                                       (e.get('links') or {}).get('livepocket')))
    rep.write('\n--- URLが既にある（入れない）---\n')
    for e, why in dup:
        rep.write('  %s 公演%s … %s\n' % (e['name'][:40], e['date'], why))
    rep.write('\n--- 投入する ---\n')
    for e in put:
        rep.write('id%d\t%s\t%s\t%s\t%s\t枠%d\t%s%s\n'
                  % (e['id'], e.get('_genre'), e['name'][:40], e['dateLabel'][:26], e['venue'][:20],
                     len(e['tickets']), e['links']['livepocket'],
                     ('\t同名あり id%s' % e['_samename']) if e.get('_samename') else ''))

    if a.apply and put:
        for e in put:
            EVENTS.append({'id': e['id'],
                           **{k: v for k, v in e.items() if k != 'id' and not k.startswith(DROP_KEYS)}})
        mo = re.search(r'(NEW_ORDER\s*=\s*)\[([0-9,\s]*)\]', h)
        cur = [int(x) for x in re.findall(r'\d+', mo.group(2))]
        merged = cur + [e['id'] for e in put if e['id'] not in cur]
        h2 = re.sub(r'(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]',
                    r'\g<1>' + '[' + ', '.join(map(str, merged)) + ']', h, count=1)
        m2 = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h2, re.S)
        bak = 'index.html.bak_%s_livepocket' % datetime.date.today().strftime('%m%d')
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
        rep.write('ズレ %s\n' % sorted(pool ^ arr)[:5])
        raw = open(PATH, 'rb').read()
        rep.write('CRCRLF %d / 素のLF %d （どちらも0が正）\n'
                  % (raw.count(b'\r\r\n'), len(re.findall(rb'(?<!\r)\n', raw))))
        rep.write('index.html %.2fMB\n' % (len(raw) / 1024 / 1024))
        assert arr == pool, '新着プールとNEW_ORDERがズレている'
        rep.write('backup: %s\n' % bak)
    rep.close()
    print('inject_livepocket: put=%d dup=%d maybe=%d apply=%s -> %s'
          % (len(put), len(dup), len(maybe), a.apply, a.report))


if __name__ == '__main__':
    main()
