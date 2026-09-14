# -*- coding: utf-8 -*-
"""e+ の「〆切日に発売時刻がくっつく」枠を、e+ の実ページから締切を取り直して直す（ぴあのヒールの e+ 版・2026-09-14 常設化）。

どんな枠か＝発売日（startDate）が今日以前・締切（date）が未来なのに、券種名が「…（…公演）9/12 10:00発売」で終わる e+ の枠。
  画面はこの形を「〜締切日 発売時刻」と出す＝**締切の時刻が嘘**（発売の時刻が入っている）。
  ぴあの heal_stale_deadlines はぴあしか読まないので、e+ の枠は毎日たまる（9/14 に78件161枠）。
  tools/fix_eplus_deadlines.py は「今日」が 7/22 固定・新着だけ・startDate のある枠を飛ばすので、これには使えない。

当て方＝枠自身の -P URL を1回ずつ読み、受付期間の「開始日・開始時刻」がその枠の startDate・発売時刻と同じ窓を探す。
  ・受付中/受付前の窓が1つに決まる → 券種名の末尾を「〜M/D H:MM」（e+ の締切）に、date を締切日に
  ・その窓が「予定枚数終了」→ 消さずに soldout（DELETE_GATE 1.）
  ・その窓が「受付終了/販売終了」→ 消さずに soldout＋saleEnded（DELETE_GATE 1.）
  ・見つからない／決まらない／読めない → 触らずに一覧に出す（人が見る）
  ・今日の発売で時刻より前の枠は、まだ正しいので触らない
e+ は叩きすぎると 503 で黙って壊れる＝1ページずつ1秒あける。ほかの e+ の道具と同時に流さない。

使い方:
  python tools/heal_eplus_started.py                 … サイト全体から探して、書き込まずに一覧だけ
  python tools/heal_eplus_started.py --ids 1,2,3     … そのエントリだけ
  python tools/heal_eplus_started.py --apply         … 書き込む（改行 CRLF を保つ）
出力: tmp/heal_eplus_started_MMDD_HHMM.md（分類ごとの一覧）
"""
import datetime
import io
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import eplus_harvest as eh

sys.stdout.reconfigure(encoding='utf-8')
NOW = datetime.datetime.now()
TODAY = NOW.date()
T_ISO = TODAY.isoformat()
eh.TODAY = TODAY
APPLY = '--apply' in sys.argv
IDS = None
if '--ids' in sys.argv:
    IDS = {int(x) for x in sys.argv[sys.argv.index('--ids') + 1].split(',') if x.strip()}
# 時刻まで付ける＝同じ日に2回流すと前の一覧を上書きする（2026-09-14 初回の試しで朝の161枠の一覧を消した）
REPORT = 'tmp/heal_eplus_started_%s.md' % NOW.strftime('%m%d_%H%M')


def windows(html):
    """受付期間の窓を全部（終わった窓も）返す。状態は section 本体の文言で読む（parse_windows と同じ規則）。"""
    out = []
    secs = [s for s in re.split(r'(?=<section class="block-ticket">)', html)
            if s.startswith('<section class="block-ticket">')]
    for sec in secs:
        body = sec.split('</section>', 1)[0]
        span = re.search(r'<span class="ticket-status__item[^"]*">([^<]+)</span>', body)
        stxt = (span.group(1) if span else '').strip()
        hm = re.search(r'block-ticket__header[^>]*>(.*?)</header>', body, re.S)
        text = eh._flat(hm.group(1) if hm else body)
        m = eh._PERIOD.search(text)
        if not m:
            continue
        g = m.groups()
        out.append({'label': re.sub(r'\s+', '', re.sub(r'受付期間.*', '', text)),
                    'sd': '%04d-%02d-%02d' % (int(g[0]), int(g[1]), int(g[2])),
                    'st': '%d:%s' % (int(g[3]), g[4]),
                    'ed': datetime.date(int(g[5]), int(g[6]), int(g[7])),
                    'et': '%d:%s' % (int(g[8]), g[9]),
                    'stxt': stxt})
    return out


def nlabel(s):
    return re.sub(r'[\s★☆◇◆■◎●▲△▼▽※<>＜＞]', '', s or '')


def main():
    src = io.open('index.html', encoding='utf-8', newline='').read()
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
    events = json.loads(m.group(2))

    targets = []
    for e in events:
        if IDS is not None and e['id'] not in IDS:
            continue
        for t in e.get('tickets') or []:
            ty = t.get('type') or ''
            sd = t.get('startDate') or ''
            mm = re.search(r'(\d{1,2}/\d{1,2}) (\d{1,2}):(\d{2})発売$', ty)
            if t.get('soldout') or not mm or not sd or sd > T_ISO or not (t.get('date') or '') > T_ISO:
                continue
            if 'eplus.jp' not in (t.get('url') or ''):
                continue
            if sd == T_ISO and (int(mm.group(2)), int(mm.group(3))) > (NOW.hour, NOW.minute):
                continue  # 今日の発売で時刻前＝まだ正しい
            targets.append((e, t, sd, '%d:%s' % (int(mm.group(2)), mm.group(3))))

    cache = {}
    for _, t, _, _ in targets:
        u = t['url']
        if u in cache:
            continue
        try:
            cache[u] = windows(eh.fetch(u))
        except Exception as ex:
            cache[u] = ex
        time.sleep(1.0)

    res = {'FIX': [], 'SAME': [], 'SOLD': [], 'ENDED': [], 'NOMATCH': [], 'AMBIG': [], 'ERR': []}
    for e, t, sd, st in targets:
        ws = cache[t['url']]
        row = [e['id'], (e.get('name') or '')[:30], t['type'], t['url']]
        if isinstance(ws, Exception):
            res['ERR'].append(row + [str(ws)[:60]])
            continue
        cands = [w for w in ws if w['sd'] == sd and w['st'] == st]
        if len({(w['ed'], w['et'], w['stxt']) for w in cands}) > 1:
            kind = nlabel(re.match(r'^(.*?)（', t['type']).group(1) if '（' in t['type'] else '')
            narrowed = [w for w in cands if kind and (kind in nlabel(w['label']) or nlabel(w['label']) in kind)]
            if len({(w['ed'], w['et'], w['stxt']) for w in narrowed}) == 1:
                cands = narrowed
        if not cands:
            res['NOMATCH'].append(row + [' / '.join('%s %s〜%s %s %s' % (w['label'][:16], w['sd'], w['ed'], w['et'], w['stxt']) for w in ws)[:200]])
            continue
        if len({(w['ed'], w['et'], w['stxt']) for w in cands}) > 1:
            res['AMBIG'].append(row + [' / '.join('%s〜%s %s %s' % (w['label'][:16], w['ed'], w['et'], w['stxt']) for w in cands)[:200]])
            continue
        w = cands[0]
        if any(d in w['stxt'] for d in eh._DEAD):
            if '予定枚数終了' in w['stxt']:
                res['SOLD'].append(row + [w['stxt']])
                if APPLY:
                    t['soldout'] = True
                    t['soldoutSince'] = T_ISO
            else:
                res['ENDED'].append(row + [w['stxt']])
                if APPLY:
                    t['soldout'] = True
                    t['saleEnded'] = True
                    t['saleEndedSince'] = T_ISO
            continue
        new_type = re.sub(r'\d{1,2}/\d{1,2} \d{1,2}:\d{2}発売$', '〜%d/%d %s' % (w['ed'].month, w['ed'].day, w['et']), t['type'])
        new_date = w['ed'].isoformat()
        res['FIX' if new_date == t['date'] else 'SAME'].append(row + ['%s → %s ｜date %s → %s' % (t['type'], new_type, t['date'], new_date)])
        if APPLY:
            t['type'] = new_type
            t['date'] = new_date

    out = io.open(REPORT, 'w', encoding='utf-8')
    W = out.write
    W('# e+ の「〆切日に発売時刻」枠の取り直し（%s）\n\n' % NOW.strftime('%Y-%m-%d %H:%M'))
    W('対象の枠 %d ／ 読んだページ %d（読めない %d）\n\n' % (
        len(targets), len(cache), sum(1 for v in cache.values() if isinstance(v, Exception))))
    names = {'FIX': '締切を入れた（date はそのまま）', 'SAME': '締切を入れた＋date も直した', 'SOLD': '予定枚数終了＝売り切れの印',
             'ENDED': '受付終了＝販売終了の印', 'NOMATCH': '合う窓が無い＝触らない', 'AMBIG': '窓が決まらない＝触らない',
             'ERR': '読めない＝触らない'}
    for k, rows in res.items():
        W('## %s %d\n\n' % (names[k], len(rows)))
        for r in rows:
            W('- id%s %s ｜%s\n  %s\n  %s\n' % (r[0], r[1], r[2], r[4], r[3]))
        W('\n')
    out.close()
    print(' / '.join('%s %d' % (k, len(v)) for k, v in res.items()), '→', REPORT)
    if not APPLY:
        print('(--apply で書き込み)')
        return
    nl = '\r\n' if '\r\n' in src else '\n'
    body = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl)
    io.open('index.html', 'w', encoding='utf-8', newline='').write(src[:m.start()] + m.group(1) + body + m.group(3) + src[m.end():])
    print('書き込み完了')


if __name__ == '__main__':
    main()
