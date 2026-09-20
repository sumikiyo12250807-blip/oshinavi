# -*- coding: utf-8 -*-
"""FANYチケットの組み上がりを新着プール（genre:"new"）に投入する恒久ツール。

  python tools/inject_fany.py tmp/built_fany_MMDD.json            … 調べるだけ
  python tools/inject_fany.py tmp/built_fany_MMDD.json --apply    … 書き込む

## やること（inject_tiget.py と同じ作法）

1. **二重登録を外す**
   - ① FANYのURL（`ticket.fany.lol/event/detail/<id>`）が既に index.html にある → 入れない
   - ② 正規化した名前 × 公演日 × 会場 が登録と一致 → ⚠️**入れずに報告**
     🚨会場まで見るのは、FANYの公演名が「本公演　１回目」のように**使い回しの名前**で、
        名前＋日付だけだと**別の劇場の別公演を同じものと誤判定する**から
        （TIGETで「名前×公演日」だけで70件外し、調べたら7件中0件が本当の二重登録だった＝
         NoGoDの5会場が丸ごと消えるところだった。[[feedback_harvest_name_dedup_blindspot]]）
   - ③ 同名の登録があるだけ（日付も会場も違う）→ **入れる**（別日の別公演なので二重ではない）
2. **idは本番の番号で振る**＝いまの最大id と `last_batch.json` の最大 id_to の次から
3. **NEW_ORDER は後ろに追記**
4. 書いたあと `genre:"new"` の件数と NEW_ORDER の件数が一致するか数える
5. index.html は CRLF。json.dumps の改行を CRLF に直してから書く

🚨ぴあ以外なので**振り分けはユーザーの確認後**＝ここは `genre:"new"` で止める。
"""
import argparse
import datetime
import io
import json
import re
import sys
import unicodedata

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', write_through=True)
PATH = 'index.html'


def norm(s):
    s = unicodedata.normalize('NFKC', s or '').lower()
    return re.sub(r'[\s　・･,，.。!！?？~〜\-—–_/／\(\)（）\[\]【】「」『』"\'’]', '', s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--limit', type=int, default=0, help='先頭N件だけ入れる（試すとき）')
    ap.add_argument('--report', default='tmp/inject_fany_report.txt')
    a = ap.parse_args()

    src = json.load(open(a.src, encoding='utf-8'))
    built = src['entries'] if isinstance(src, dict) else src
    h = io.open(PATH, encoding='utf-8', newline='').read()
    NL = '\r\n' if '\r\n' in h else '\n'
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
    EVENTS = json.loads(m.group(2))

    have_urls = set(re.findall(r'ticket\.fany\.lol/event/detail/(\d+)', h))
    # 名前×公演日×会場 の索引（会場は表記ゆれがあるので正規化して部分一致でも見る）
    trio, by_name = set(), {}
    for e in EVENTS:
        blob = json.dumps(e, ensure_ascii=False)
        days = set(re.findall(r'\d{4}-\d{2}-\d{2}', blob))
        ven = norm(e.get('venue'))
        for n in {norm(e.get('artist')), norm(e.get('name'))}:
            if not n:
                continue
            by_name.setdefault(n, []).append(e['id'])
            for d in days:
                trio.add((n, d, ven))

    put, dup, maybe = [], [], []
    for e in sorted(built, key=lambda x: (x.get('date') or '', x.get('name') or '')):
        fid = re.search(r'/event/detail/(\d+)', e['links'].get('fany') or '')
        if fid and fid.group(1) in have_urls:
            dup.append((e, 'FANYのURLが既に登録にある %s' % fid.group(1)))
            continue
        na, nn, nv = norm(e.get('artist')), norm(e.get('name')), norm(e.get('venue'))
        if (na, e['date'], nv) in trio or (nn, e['date'], nv) in trio:
            maybe.append((e, '名前×公演日×会場が登録と一致'))
            continue
        put.append(e)

    if a.limit:
        put, rest = put[:a.limit], put[a.limit:]
    else:
        rest = []

    lb = json.load(io.open('.claude/state/last_batch.json', encoding='utf-8'))['batches']
    nid = max([e['id'] for e in EVENTS] + [b.get('id_to') or 0 for b in lb])
    for e in put:
        nid += 1
        e['id'] = nid

    rep = io.open(a.report, 'w', encoding='utf-8')
    rep.write('=== inject_fany (%s) %s ===\n' % (datetime.date.today().isoformat(), a.src))
    rep.write('組み上がり %d件 → 投入 %d / URL重複 %d / ⚠️要確認 %d / 今回は入れない %d\n'
              % (len(built), len(put), len(dup), len(maybe), len(rest)))
    if put:
        rep.write('  投入する id %d〜%d\n' % (put[0]['id'], put[-1]['id']))
    rep.write('\n--- ⚠️要確認（入れない＝名前×公演日×会場が既存と一致）---\n')
    for e, why in maybe:
        rep.write('  %s / %s / 公演%s … %s\n    %s\n'
                  % (e['name'][:40], e['venue'][:20], e['date'], why, e['links']['fany']))
    rep.write('\n--- URLが既にある（入れない）---\n')
    for e, why in dup:
        rep.write('  %s 公演%s … %s\n' % (e['name'][:40], e['date'], why))
    rep.write('\n--- 投入する ---\n')
    for e in put:
        rep.write('id%d\t%s\t%s\t%s\t%s\t枠%d\n'
                  % (e['id'], e.get('_genre'), e['name'][:40], e['dateLabel'][:24],
                     e['venue'][:20], len(e['tickets'])))

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
        bak = 'index.html.bak_%s_fany' % datetime.date.today().strftime('%m%d')
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
        rep.write('配列にあるがプールに無い %s\n' % sorted(arr - pool)[:5])
        rep.write('プールにあるが配列に無い %s\n' % sorted(pool - arr)[:5])
        raw = open(PATH, 'rb').read()
        rep.write('CRCRLF %d / 素のLF %d （どちらも0が正）\n'
                  % (raw.count(b'\r\r\n'), len(re.findall(rb'(?<!\r)\n', raw))))
        rep.write('index.html %.2fMB\n' % (len(raw) / 1024 / 1024))
        assert arr == pool, '新着プールとNEW_ORDERがズレている'
        rep.write('backup: %s\n' % bak)
    rep.close()
    print('inject_fany: put=%d dup=%d maybe=%d apply=%s -> %s'
          % (len(put), len(dup), len(maybe), a.apply, a.report))


if __name__ == '__main__':
    main()
