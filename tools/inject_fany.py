# -*- coding: utf-8 -*-
"""FANYチケットの組み上がりを新着プール（genre:"new"）に投入する恒久ツール。

  python tools/inject_fany.py tmp/built_fany_MMDD.json            … 調べるだけ
  python tools/inject_fany.py tmp/built_fany_MMDD.json --apply    … 書き込む

## やること（inject_tiget.py と同じ作法）

1. **二重登録を外す**
   - ① その**公演id**（申込URL `/reception/<sales_id>/<performance_id>`）が既に登録にある → 入れない
     （イベント単位の `/event/detail/<id>` では見ない＝同じイベントの別公演が消える。
      申込URLを1つも持たない組み上がりだけ、イベントURLで見る）
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

## 2026-09-21 夜の穴（直した）

番人 gate_fany_slots で「売り場にあるのに登録に無い枠」が、これからの公演だけで52件123枠出た
（山里亮太の140 11/13・11/15、よしもと落語 二人会 10/18・11/8 など）。公演id（performance_id）の
照合は正しかったが、②「名前×公演日×会場」の索引が**登録エントリ本文の全ISO日付**（＝各枠の
**締切日**も）を「公演日」として積んでいたため、同じイベントの**翌日公演の一般発売締切（前日
23:59）**が「この日の公演は登録済み」に見え、別公演が要確認で落ちていた。直し方＝
- 登録側が **FANYの申込URL（/reception/）を持つエントリ**（＝FANYで入れた1公演1エントリ）は、
  索引に**その公演日（date）だけ**を積む。しかも**同じ event_id 同士は②を見ない**
  （同じイベントの別公演・同日の別開演時刻は公演idで区別できる＝①で足りる）
- それ以外（ぴあ等の別売り場のエントリ・links.fany を足し込んだぴあ登録）は従来どおり本文の
  日付で見る（ツアーの別日を拾うため）＝別売り場との二重は引き続き要確認で止める
- ただし**そのイベントが既にFANYの1公演1エントリで入っている**なら、別売り場の登録に当たっても
  止めない。初回投入で、ぴあの通し登録（例 山里亮太の140 東京 11/9〜11/15＝締切11/13）に
  当たった日（11/13・11/15）だけが落ち、残りの日はFANYで入っていた＝同じイベントが歯抜けになり、
  番人が毎日「売り場にあるのに登録に無い」と鳴らしていた（9/21夜の52件123枠の正体はこれ）
`python tools/inject_fany.py --selftest` で判定を確かめられる。
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


RE_PERF = re.compile(r'fany\.lol/reception/\d+/(\d+)')
RE_EVT = re.compile(r'fany\.lol/event/detail/(\d+)')


def _perfs(e):
    return {p for t in (e.get('tickets') or []) for p in RE_PERF.findall(t.get('url') or '')}


def _evt(e):
    m = RE_EVT.search((e.get('links') or {}).get('fany') or '')
    return m.group(1) if m else None


def classify(built, EVENTS):
    """組み上がりを (put, dup, maybe) に分ける。判定の本体（--selftest はここを試す）。

    🚨重複は**公演単位**で見る＝申込URL `/reception/<sales_id>/<performance_id>` の
      performance_id。event_id（/event/detail/<id>）で見ると、**同じイベントの別公演**が
      全部「登録済み」に見えて入らない（1公演＝1エントリにしているので事故になる）。
    """
    have_perf, have_evt, fany_evts = set(), set(), set()
    # 名前×公演日×会場 → その索引を積んだ登録エントリの event_id（FANYエントリなら）の集合
    trio = {}
    for e in EVENTS:
        ps = _perfs(e)
        have_perf |= ps
        ev = _evt(e)
        if ev:
            have_evt.add(ev)
        if ps and ev:
            fany_evts.add(ev)
        if ps:
            # FANYで入れた1公演1エントリ＝公演日だけ。締切日を公演日と取り違えない（2026-09-21）
            days, tag = {e.get('date')} - {None, ''}, ev
        else:
            # 別売り場のエントリ＝本文の日付を全部（ツアーの別日も拾う）。event_id では免除しない
            days, tag = set(re.findall(r'\d{4}-\d{2}-\d{2}', json.dumps(e, ensure_ascii=False))), None
        ven = norm(e.get('venue'))
        for n in {norm(e.get('artist')), norm(e.get('name'))} - {''}:
            for d in days:
                trio.setdefault((n, d, ven), set()).add(tag)

    put, dup, maybe = [], [], []
    for e in sorted(built, key=lambda x: (x.get('date') or '', x.get('name') or '')):
        perfs = _perfs(e)
        if perfs and perfs <= have_perf:
            dup.append((e, 'この公演（performance %s）は既に登録にある' % sorted(perfs)))
            continue
        fid = _evt(e)
        if not perfs and fid and fid in have_evt:
            dup.append((e, 'FANYのURLが既に登録にある %s' % fid))
            continue
        na, nn, nv = norm(e.get('artist')), norm(e.get('name')), norm(e.get('venue'))
        hit = set()
        for n in {na, nn} - {''}:
            hit |= trio.get((n, e.get('date'), nv), set())
        # 同じ event_id のFANYエントリだけに当たった＝同じイベントの別公演（公演idは①で見た）
        others = hit - {fid}
        # このイベントは既に**FANYの1公演1エントリで入っている**＝残りの公演だけ別売り場の登録を
        # 理由に止めると、同じイベントの公演が歯抜けになる（2026-09-21＝山里亮太の140 東京は
        # 11/9〜11/15のうち11/13・11/15だけ、ぴあの通し登録に当たって落ちていた）
        if fid in fany_evts:
            others.discard(None)
        if others:
            maybe.append((e, '名前×公演日×会場が登録と一致'))
            continue
        put.append(e)
    return put, dup, maybe


def _selftest():
    def fe(eid, date, perf, name='本公演　１回目', venue='なんばグランド花月', deadline=None):
        return {'id': perf, 'artist': 'A', 'name': name, 'date': date, 'venue': venue,
                'links': {'fany': 'https://ticket.fany.lol/event/detail/%s' % eid},
                'tickets': [{'type': '一般発売', 'date': deadline or date,
                             'url': 'https://ticket.fany.lol/reception/1/%s' % perf}]}
    reg = [
        # 登録済み FANY：event 100 の 11/14 公演（一般発売の締切が前日 11/13）
        fe(100, '2026-11-14', 5001, deadline='2026-11-13'),
        # 登録済み FANY：event 200 の 10/18 11:30 公演
        fe(200, '2026-10-18', 6001),
        # ぴあ登録（links.fany を足し込んだ形）：12/1 公演、FANYの申込URLは持たない
        {'id': 9, 'artist': 'B', 'name': 'Bライブ', 'date': '2026-12-01', 'venue': 'Zepp',
         'links': {'fany': 'https://ticket.fany.lol/event/detail/300', 'pia': 'x'},
         'tickets': [{'type': '一般', 'date': '2026-11-20', 'url': 'https://t.pia.jp/x'}]},
        # 別イベントの FANY エントリ：同名・同会場・12/5
        fe(400, '2026-12-05', 7001, name='共通の名前', venue='劇場X'),
        # ぴあの通し登録（11/9〜11/15・締切11/13）＋ 同じ公演のFANY 11/9 が既に1公演1エントリで入っている
        {'id': 10, 'artist': 'C', 'name': 'C独演会', 'date': '2026-11-15', 'venue': 'ホールY',
         'links': {'pia': 'x'},
         'tickets': [{'type': '一般', 'date': '2026-11-13', 'url': 'https://t.pia.jp/y'}]},
        fe(500, '2026-11-09', 9001, 'C独演会', 'ホールY'),
    ]
    cases = [
        ('同じ公演id＝重複', fe(100, '2026-11-14', 5001), 'dup'),
        ('同じイベントの前日公演（締切日と同じ日）＝入れる', fe(100, '2026-11-13', 5002), 'put'),
        ('同じイベント・同じ日の別開演時刻＝入れる', fe(200, '2026-10-18', 6002), 'put'),
        ('ぴあ登録と名前×日×会場が一致＝要確認', fe(300, '2026-12-01', 8001, 'Bライブ', 'Zepp'), 'maybe'),
        ('別イベントのFANYと名前×日×会場が一致＝要確認', fe(401, '2026-12-05', 7002, '共通の名前', '劇場X'), 'maybe'),
        ('同名でも別日＝入れる', fe(401, '2026-12-06', 7003, '共通の名前', '劇場X'), 'put'),
        ('ぴあ通し登録に当たるが同じイベントのFANYが既にある＝入れる（歯抜けにしない）',
         fe(500, '2026-11-13', 9002, 'C独演会', 'ホールY'), 'put'),
        ('同じ条件でFANYの兄弟が無い別イベント＝要確認', fe(501, '2026-11-15', 9101, 'C独演会', 'ホールY'), 'maybe'),
    ]
    ng = 0
    for label, b, want in cases:
        put, dup, maybe = classify([b], reg)
        got = 'put' if put else 'dup' if dup else 'maybe'
        ok = got == want
        ng += not ok
        print('%s %s（期待 %s／結果 %s）' % ('OK' if ok else 'NG', label, want, got))
    print('selftest %s' % ('OK' if not ng else 'NG %d' % ng))
    return 1 if ng else 0


def main():
    if '--selftest' in sys.argv:
        sys.exit(_selftest())
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

    put, dup, maybe = classify(built, EVENTS)

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
