# -*- coding: utf-8 -*-
"""楽天の枠に「予定枚数終了」を付け外しする（ぴあの mark_soldout に当たる恒久ツール）。

  python tools/rakuten_mark_soldout.py            … 調べるだけ
  python tools/rakuten_mark_soldout.py --apply    … index.html に反映
  python tools/rakuten_mark_soldout.py --ids 7494,3224
  python tools/rakuten_mark_soldout.py --selftest

## なぜ要るか（2026-09-10 ユーザーが画面で発見）

「木下グループが売り切れ出てる」。id7494 は14公演中12公演が「予定枚数終了」なのに
OSHINAVI は全部「買える枠」で出していた。**機械ゲートが1つも捕まえられなかった**＝
ぴあの `pia_statustext` に当たる道具が楽天に無かった。

🚨楽天の売り状態は**生HTMLに1文字も無い**（公演カードの class は売り切れても active のまま）。
`tools/rakuten_perf_status.py` が購入ボタンのAJAXから取る。

## 判定の作法（[[feedback_saleended_vs_soldout]]／[[feedback_soldout_keep_visible]]）

- 枠が名乗っている公演日（バッジの「（県 M/D公演）」）に当たる**その公演のカード**だけを見る
- その公演のカードが**全部 soldout** の時だけ印を付ける（1枚でも買えるなら触らない）
- 楽天が「予定枚数終了」と明記しているので `soldout`（`saleEnded` は付けない）
- 売り切れは**消さない**
- **逆向きも見る**＝買えるようになっていたら印を外す
- 🚨調べられなかったページは**件数を必ず出す**（「売り切れていない」ではなく「確かめられていない」）
"""
import argparse
import datetime
import json
import re
import sys
import urllib.parse

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_perf_status as PS

TODAY = datetime.date.today().isoformat()
BADGE = re.compile(r'（[^（）]*?((?:R\d+年\s*)?\d{1,2}/\d{1,2}(?:〜(?:R\d+年\s*)?\d{1,2}/\d{1,2})?)'
                   r'(?:\s+\d{1,2}:\d{2})?公演）')


def raw_url(u):
    m = re.search(r'murl=([^&]+)', u or '')
    return urllib.parse.unquote(m.group(1)) if m else (u or '')


def md(iso_s):
    return '%d/%d' % (int(iso_s[5:7]), int(iso_s[8:10]))


def badge_days(ty):
    """バッジの「（県 M/D公演）」から M/D を取り出す（R9年と開演時刻は落とす）。"""
    m = BADGE.search(ty or '')
    if not m:
        return []
    return [re.sub(r'^R\d+年\s*', '', x.strip()) for x in m.group(1).split('〜')]


def judge(ticket, by_md, rows=None):
    """その枠は 'soldout' / 'buyable' / None（判定できない）。

    🚨バッジが「10/4〜10/6公演」の範囲形の時は**間の日も見る**。
      端の2日だけ見ると、真ん中の公演が買えるのに売り切れと書く事故になる。
    """
    days = badge_days(ticket.get('type'))
    if not days:
        return None
    cs = []
    if len(days) > 1 and rows:
        iso = {}
        for c in rows:
            iso.setdefault(md(c['date']), c['date'])
        lo, hi = iso.get(days[0]), iso.get(days[-1])
        if lo and hi:
            cs = [c for c in rows if lo <= c['date'] <= hi]
    if not cs:
        for d in days:
            cs += by_md.get(d, [])
    if not cs:
        return None
    if all(c['status'] == 'soldout' for c in cs):
        return 'soldout'
    if any(c['status'] == 'buyable' for c in cs):
        return 'buyable'
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--ids', default='')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        _selftest()
        return 0

    only = {int(x) for x in a.ids.split(',') if x.strip()}
    src = open('index.html', encoding='utf-8').read()
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
    events = json.loads(m.group(2))

    targets = []
    for e in events:
        if only and e['id'] not in only:
            continue
        slots = [t for t in (e.get('tickets') or []) if 'rakuten' in raw_url(t.get('url'))]
        if not slots:
            continue
        urls = []
        for t in slots:
            u = raw_url(t['url'])
            if u not in urls:
                urls.append(u)
        lr = raw_url((e.get('links') or {}).get('rakuten'))
        if lr and lr not in urls:
            urls.append(lr)
        targets.append((e, slots, urls))

    print('=== rakuten_mark_soldout (today=%s) 対象%d件 ===\n' % (TODAY, len(targets)))
    cache = {}
    marked = unmarked = 0
    skipped = []
    for e, slots, urls in targets:
        rows, why = [], None
        for u in urls:
            if u not in cache:
                try:
                    cache[u] = PS.perf_status(u)
                except Exception as ex:
                    cache[u] = {'ok': False, 'why': repr(ex)[:70], 'rows': []}
            r = cache[u]
            if not r.get('ok'):
                why = r.get('why')
                continue
            rows += r['rows']
        if not rows:
            skipped.append((e['id'], e.get('name', '')[:40], why or '公演カードが取れない'))
            continue
        by_md = {}
        for c in rows:
            by_md.setdefault(md(c['date']), []).append(c)
        for t in slots:
            v = judge(t, by_md, rows)
            if v == 'soldout' and not t.get('soldout'):
                t['soldout'] = True
                t['soldoutSince'] = TODAY
                t.pop('saleEnded', None)
                t.pop('saleEndedSince', None)
                marked += 1
                print('🔴 id=%-5s %-46s → 予定枚数終了' % (e['id'], t['type'][:46]))
            elif v == 'buyable' and t.get('soldout'):
                t.pop('soldout', None)
                t.pop('soldoutSince', None)
                unmarked += 1
                print('🟢 id=%-5s %-46s → 買えるので印を外す' % (e['id'], t['type'][:46]))

    print('\n=== 印を付けた %d枠 / 外した %d枠 / ⏭️調べられなかった %d件 ==='
          % (marked, unmarked, len(skipped)))
    if skipped:
        print('   ※⏭️は「売り切れていない」ではなく「確かめられていない」')
        for i, n, w in skipped:
            print('   id=%-5s %-40s %s' % (i, n, w))

    if not a.apply:
        print('\n(--apply で書き込み)')
        return 0
    arr = json.dumps(events, ensure_ascii=False, indent=2)
    open('index.html', 'w', encoding='utf-8').write(
        src[:m.start()] + m.group(1) + arr + m.group(3) + src[m.end():])
    print('\n書き込み完了')
    return 0


def _selftest():
    assert badge_days('一般発売（東京 9/30公演）〜9/24 23:59') == ['9/30']
    assert badge_days('一般発売（東京 10/4〜10/6公演）〜9/30 23:59') == ['10/4', '10/6']
    assert badge_days('一般発売（大阪 R9年 4/3 16:30公演）〜R9年 4/3 17:00') == ['4/3']
    assert badge_days('よくわからない券種') == []
    by = {'9/30': [{'status': 'soldout'}, {'status': 'soldout'}],
          '10/1': [{'status': 'soldout'}, {'status': 'buyable'}],
          '10/2': [{'status': 'unknown'}]}
    assert judge({'type': '一般発売（東京 9/30公演）〜9/24'}, by) == 'soldout'
    # 1枚でも買えるなら触らない
    assert judge({'type': '一般発売（東京 10/1公演）〜9/25'}, by) == 'buyable'
    # 分からないものは触らない
    assert judge({'type': '一般発売（東京 10/2公演）〜9/26'}, by) is None
    # ページに無い公演も触らない
    assert judge({'type': '一般発売（東京 12/9公演）〜12/1'}, by) is None
    # 🚨範囲バッジは**間の日も見る**＝端が売切でも真ん中が買えるなら印を付けない
    rows = [{'date': '2026-10-04', 'status': 'soldout'},
            {'date': '2026-10-05', 'status': 'buyable'},
            {'date': '2026-10-06', 'status': 'soldout'}]
    by2 = {}
    for c in rows:
        by2.setdefault(md(c['date']), []).append(c)
    t = {'type': '一般発売（東京 10/4〜10/6公演）〜9/30'}
    assert judge(t, by2, rows) == 'buyable', judge(t, by2, rows)
    # 間も含めて全部売切なら印を付ける
    rows2 = [dict(c, status='soldout') for c in rows]
    by3 = {}
    for c in rows2:
        by3.setdefault(md(c['date']), []).append(c)
    assert judge(t, by3, rows2) == 'soldout'
    print('selftest OK: バッジの公演日の取り出し / 全部売切の時だけ印 / 1枚でも買えるなら触らない'
          ' / 範囲バッジは間の日も見る')


if __name__ == '__main__':
    sys.exit(main())
