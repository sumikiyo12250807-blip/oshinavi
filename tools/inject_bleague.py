# -*- coding: utf-8 -*-
"""B.LEAGUE チケットの組み上がりを新着プール（genre:"new"）に投入する（inject_ticketdive.py と同じ形）。

  python tools/inject_bleague.py tmp/x1120/newv/bleague/built.json            … 調べるだけ（下見）
  python tools/inject_bleague.py tmp/x1120/newv/bleague/built.json --apply    … 書き込む
  python tools/inject_bleague.py --selftest

## 二重登録を外す
- ① 試合ページの URL（`ticket.bleague.jp/clubs/<主催>/events/<eventId>`）が既に index.html にある → 入れない
- ② **対戦カード（ホーム×アウェイ）× 試合日** が登録と一致 → 入れずに「ボタンを足す候補」（`--buttons`）
     登録（ぴあ）の名前は「レバンガ北海道対川崎ブレイブサンダース りそなグループ…」／出演者「A／B」の形。
     ぴあのカードは2日分を1枚にしている（dateLabel が範囲）＝範囲の中の日も当てる。
     🚨同じ試合でも売り場が違う（ホーム側・アウェイ側）ことがある＝畳むかどうかは人が見る（[[feedback_sports_home_away_never_merge]]）
- ③ 名前（出演者 or 公演名）× 試合日 が一致 → ②と同じ扱い（特別試合など）
## 書き込み（--apply の時だけ）
- id は いまの最大id と last_batch.json の最大 id_to の次から（削除済みidは再利用しない）
- NEW_ORDER は後ろに追記・書いた後に genre:"new" の件数と NEW_ORDER が一致するか数える
- index.html は CRLF を保つ
🚨投入の前に `gate_bleague_slots.py --built <組み上がり>` を通して exit 0 を確かめる（投入後にも回す）。
🚨index.html に B.LEAGUE のボタン（linkDefs の key "bleague"）がまだ無い＝足すまでボタンが出ない。
"""
import argparse
import datetime
import io
import json
import re
import sys
import unicodedata

if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
PATH = 'index.html'
URL_RE = r'ticket\.bleague\.jp/clubs/[a-z0-9]+/events/([A-Za-z0-9]+)'


def norm(s):
    s = unicodedata.normalize('NFKC', s or '').lower()
    return re.sub(r'[\s　・･,，.。!！?？~〜\-—–_/／\(\)（）\[\]【】「」『』"\'’]', '', s)


def pair_of(e):
    """カードの対戦カード（ホーム, アウェイ）の正規化。名前「A対B …」か出演者「A／B」から。無ければ None。"""
    m = re.match(r'^\s*(.+?)\s*(?:対|vs\.?|VS\.?)\s*(.+?)(?:[（(\s]|$)', unicodedata.normalize('NFKC', e.get('name') or ''))
    if m and len(norm(m.group(1))) >= 2 and len(norm(m.group(2))) >= 2:
        return norm(m.group(1)), norm(m.group(2))
    parts = [p for p in re.split(r'／|/', e.get('artist') or '') if p.strip()]
    if len(parts) == 2:
        return norm(parts[0]), norm(parts[1])
    return None


def show_days(e):
    """カードの試合日の集合＝dateLabel の年月日（範囲なら間の日も）＋date。締切・発売日は入れない。"""
    ds = sorted('%s-%02d-%02d' % (y, int(m), int(d))
                for y, m, d in re.findall(r'(\d{4})年(\d{1,2})月(\d{1,2})日', e.get('dateLabel') or ''))
    out = set(ds) | ({e['date']} if e.get('date') else set())
    if len(ds) >= 2 and '〜' in (e.get('dateLabel') or ''):
        a, b = datetime.date.fromisoformat(ds[0]), datetime.date.fromisoformat(ds[-1])
        if (b - a).days <= 31:
            while a <= b:
                out.add(a.isoformat())
                a += datetime.timedelta(days=1)
    for t in e.get('tickets') or []:
        for m in re.finditer(r'(?:R(\d+)年 )?(\d{1,2})/(\d{1,2})(?: \d{1,2}:\d{2})?(?:・\d{1,2})?公演', t.get('type') or ''):
            if not e.get('date'):
                continue
            y = 2018 + int(m.group(1)) if m.group(1) else int(e['date'][:4])
            try:
                out.add(datetime.date(y, int(m.group(2)), int(m.group(3))).isoformat())
            except ValueError:
                pass
    return out


def index_keys(EVENTS):
    by_pair, by_name = {}, {}
    for e in EVENTS:
        if not e.get('date'):
            continue
        days = show_days(e)
        p = pair_of(e)
        for d in days:
            if p:
                by_pair.setdefault((p, d), []).append(e['id'])
            for n in {norm(e.get('artist')), norm(e.get('name'))}:
                if n:
                    by_name.setdefault((n, d), []).append(e['id'])
    return by_pair, by_name


def classify(built, EVENTS, have_urls):
    by_pair, by_name = index_keys(EVENTS)
    put, dup, btn = [], [], []
    for e in sorted(built, key=lambda x: (x.get('date') or '', x.get('name') or '')):
        u = re.findall(URL_RE, e['links'].get('bleague') or '')
        if set(u) & have_urls:
            dup.append((e, '試合ページの URL が既に登録にある'))
            continue
        p = pair_of(e)
        hit = sorted(set(by_pair.get((p, e['date']), []) if p else [])
                     | set(by_name.get((norm(e.get('artist')), e['date']), []))
                     | set(by_name.get((norm(e.get('name')), e['date']), [])))
        if hit:
            btn.append((e, hit))
            continue
        put.append(e)
    return put, dup, btn


def _selftest():
    EV = [{'id': 1, 'artist': 'レバンガ北海道対川崎ブレイブサンダース りそなグループ B.LEA',
           'name': 'レバンガ北海道対川崎ブレイブサンダース りそなグループ B.LEAGUE 2026-27 B.LEAGUE PREMIERリーグ戦',
           'date': '2026-12-20', 'dateLabel': '2026年12月19日(土)〜2026年12月20日(日)',
           'tickets': [{'type': '一般発売（北海道 12/19〜12/20公演）〜11/29 23:59', 'date': '2026-11-29'}], 'links': {}},
          {'id': 2, 'artist': 'X', 'name': 'Y', 'date': '2026-12-24', 'tickets': [],
           'links': {'bleague': 'https://ticket.bleague.jp/clubs/lh/events/ABC'}}]

    def mk(home, away, date, eid):
        return {'artist': '%s／%s' % (home, away), 'name': '%s対%s（会場） 大会' % (home, away), 'date': date,
                'dateLabel': '', 'tickets': [], 'links': {'bleague': 'https://ticket.bleague.jp/clubs/lh/events/' + eid}}
    built = [mk('レバンガ北海道', '川崎ブレイブサンダース', '2026-12-19', 'A1'),     # ② 範囲の中の日
             mk('レバンガ北海道', '川崎ブレイブサンダース', '2026-12-26', 'A2'),     # 別の日＝入れる
             mk('川崎ブレイブサンダース', 'レバンガ北海道', '2026-12-20', 'A3'),     # ホームとアウェイが逆＝別の試合
             mk('P', 'Q', '2026-12-24', 'ABC')]                                     # ① URL
    put, dup, btn = classify(built, EV, {'ABC'})
    assert [e['links']['bleague'][-2:] for e in put] == ['A3', 'A2'] or [e['links']['bleague'][-2:] for e in put] == ['A2', 'A3'], put
    assert len(dup) == 1 and len(btn) == 1 and btn[0][1] == [1], (dup, btn)
    assert pair_of({'name': '東京サンゴリアス対埼玉ワイルドナイツ NTT', 'artist': ''}) == ('東京サンゴリアス', '埼玉ワイルドナイツ')
    print('selftest OK: ①URL重複/②対戦カード×試合日（範囲の dateLabel も）＝ボタン候補/ホームとアウェイ逆は別')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--report', default='tmp/inject_bleague_report.txt')
    ap.add_argument('--buttons', default='tmp/bleague_button_cands.json', help='②ボタンを足す候補の出力先')
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
    json.dump([{'bleague': e['links']['bleague'], 'name': e['name'], 'artist': e['artist'], 'date': e['date'],
                'dateLabel': e['dateLabel'], 'venue': e['venue'],
                'match': [{'id': i, 'name': byid[i].get('name'), 'artist': byid[i].get('artist'),
                           'venue': byid[i].get('venue'), 'date': byid[i].get('date'), 'genre': byid[i].get('genre'),
                           'links': [k for k, v in (byid[i].get('links') or {}).items() if v]}
                          for i in ids[:6]],
                'tickets': e['tickets']} for e, ids in btn],
              io.open(a.buttons, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    rep = io.open(a.report, 'w', encoding='utf-8')
    rep.write('=== inject_bleague (%s) %s ===\n' % (datetime.date.today().isoformat(), a.src))
    rep.write('組み上がり %d件 → 投入 %d / URL重複 %d / ボタン候補（対戦カード・名前×試合日が一致）%d\n'
              % (len(built), len(put), len(dup), len(btn)))
    if put:
        rep.write('  投入する id %d〜%d\n' % (put[0]['id'], put[-1]['id']))
    rep.write('\n--- ボタンを足す候補（入れない・%s）---\n' % a.buttons)
    for e, ids in btn:
        rep.write('  %s 試合%s → 既存 id%s\n    %s\n' % (e['name'][:50], e['date'], ids[:6], e['links']['bleague']))
    rep.write('\n--- URLが既にある（入れない）---\n')
    for e, why in dup:
        rep.write('  %s 試合%s … %s\n' % (e['name'][:44], e['date'], why))
    rep.write('\n--- 投入する ---\n')
    for e in put:
        rep.write('id%d\t%s\t%s\t%s\t%s\t%s\t枠%d\n'
                  % (e['id'], e.get('_genre') or '(空)', e['name'][:50], e['dateLabel'][:26],
                     e['venue'][:22], e.get('prefecture') or '(県なし)', len(e['tickets'])))

    if a.apply and put:
        for e in put:
            EVENTS.append({'id': e['id'], **{k: v for k, v in e.items() if k != 'id'}})
        mo = re.search(r'(NEW_ORDER\s*=\s*)\[([0-9,\s]*)\]', h)
        cur = [int(x) for x in re.findall(r'\d+', mo.group(2))]
        merged = cur + [e['id'] for e in put if e['id'] not in cur]
        h2 = re.sub(r'(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]',
                    r'\g<1>' + '[' + ', '.join(map(str, merged)) + ']', h, count=1)
        m2 = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h2, re.S)
        bak = 'index.html.bak_%s_bleague' % datetime.date.today().strftime('%m%d')
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
    sys.stderr.write('inject_bleague: put=%d dup=%d buttons=%d apply=%s -> %s\n'
                     % (len(put), len(dup), len(btn), a.apply, a.report))


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        _selftest()
        sys.exit(0)
    main()
