# -*- coding: utf-8 -*-
"""楽天チケットの「これから発売」を取りに行くハーベスト（入口をsitemapの並び順に変えた版）。

  python tools/rakuten_presale_harvest.py --maps 26,27 --out tmp/rakuten_presale.json
  python tools/rakuten_presale_harvest.py --selftest

## なぜ作ったか（2026-09-09 と 09-10 に2回ユーザーに言われた）

> 「楽天チケットからは今買えるのしかない。これから発売のは売ってないの？」（9/9）
> 「楽天から持ってきたチケットが売ってるのしかない件　これから発売のチケット探して、そっちを優先にして」（9/10）

**真因＝入口が `lastmod` 頼みだった。** 楽天は lastmod をほとんど更新しないので、
「直近◯日更新」で絞ると 27,105件中 119件しか見えない（[[reference_rakuten_harvest]]）。

## ✅ 入口の正解＝**post-sitemap の番号は投稿順**（2026-09-10 実測）

| sitemap | 公演URL | lastmod の範囲 |
|---|---|---|
| post-sitemap.xml (1) | 958 | 2019-05 |
| post-sitemap26.xml | 997 | 2025-03 〜 2026-07 |
| **post-sitemap27.xml** | **265** | **2026-04 〜 2026-09** |

＝**番号が大きいほど新しい公演**。26+27 の 1,262件で「今動いている公演」がほぼ入る。
日付で絞るのではなく**後ろのsitemapから舐める**のが正しい入口。

## 売り状態は cms-api で取る

公演カードの class は売り切れても 'active' のままなので、
`tools/rakuten_perf_status.py`（購入ボタンのAJAX）で公演ごとの
「購入する／予定枚数終了」を取り、**買えない公演を発売前と数えない**ようにする。
"""
import argparse
import datetime
import json
import re
import sys
import time

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_harvest as RH
import rakuten_perf_status as PS

TODAY = datetime.date.today().isoformat()
RT = re.compile(r'/rt[0-9a-z]{4,8}/?$', re.I)
SITEMAP = 'https://ticket.rakuten.co.jp/post-sitemap%s.xml'


def map_urls(nums):
    """指定した post-sitemap から公演URLを集める（新しい番号から順に）。"""
    out = []
    for n in nums:
        u = SITEMAP % ('' if n == 1 else n)
        try:
            body = PS.fetch(u)
        except Exception as ex:
            sys.stderr.write('  sitemap%s 取得失敗 %r\n' % (n, ex))
            continue
        locs = [l for l in re.findall(r'<loc>([^<]+)</loc>', body) if RT.search(l)]
        sys.stderr.write('  sitemap%s: 公演URL %d件\n' % (n, len(locs)))
        # 後ろほど新しいので逆順に
        out += list(reversed(locs))
    seen, uniq = set(), []
    for u in out:
        if u not in seen:
            seen.add(u)
            uniq.append(u)
    return uniq


def classify(rec, status_rows):
    """このページを「発売前 / 販売中 / 対象外」に分ける。

    発売前＝**販売枠の開始が明日以降**のものが1つでもある（[[feedback_presale_first_harvest]]）。
    売り切れ判定＝公演カードの売り状態が全部 soldout なら、その公演は数えない。
    """
    future = [p for p in rec['perfs'] if (p.get('end') or p['date']) > TODAY]
    if not future:
        return 'past', [], []
    sold = {}
    for r in status_rows or []:
        sold.setdefault(r['date'], []).append(r['status'])
    alive_perf = [p for p in future
                  if not (sold.get(p['date']) and all(s == 'soldout' for s in sold[p['date']]))]
    if not alive_perf:
        return 'soldout', [], []

    presale, onsale = [], []
    for w in rec['windows']:
        sd, _st = RH.win_dates(w.get('timming'))
        if sd and sd[:10] > TODAY:
            presale.append(w)
        else:
            onsale.append(w)
    return ('presale' if presale else 'onsale'), presale, onsale


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--maps', default='27,26', help='見る post-sitemap の番号（カンマ区切り）')
    ap.add_argument('--out', default='tmp/rakuten_presale.json')
    ap.add_argument('--limit', type=int, default=0, help='試すページ数の上限（0=全部）')
    ap.add_argument('--sleep', type=float, default=0.4)
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        _selftest()
        return 0

    nums = [int(x) for x in a.maps.split(',') if x.strip()]
    sys.stderr.write('=== 入口: post-sitemap %s ===\n' % nums)
    urls = map_urls(nums)
    if a.limit:
        urls = urls[:a.limit]
    sys.stderr.write('公演URL %d件を見る\n' % len(urls))

    out = {'presale': [], 'onsale': [], 'soldout': [], 'past': [], 'error': []}
    for i, u in enumerate(urls, 1):
        try:
            rec = RH.parse_page(u, RH.fetch(u))
        except Exception as ex:
            out['error'].append({'url': u, 'why': repr(ex)[:80]})
            continue
        if not rec.get('name') or not rec.get('perfs'):
            out['error'].append({'url': u, 'why': '公演が読めない形式'})
            continue
        rows = []
        try:
            r = PS.perf_status(u)
            rows = r['rows'] if r.get('ok') else []
        except Exception:
            rows = []
        kind, presale, _onsale = classify(rec, rows)
        item = {
            'url': u, 'name': rec['name'], '_genre': rec.get('_genre'),
            'perfs': len(rec['perfs']),
            'first': min(p['date'] for p in rec['perfs']),
            'last': max((p.get('end') or p['date']) for p in rec['perfs']),
            'presale_windows': [{'type': w.get('type'), 'timming': w.get('timming')} for w in presale],
            'windows': [{'type': w.get('type'), 'timming': w.get('timming')} for w in rec['windows']],
            'status_rows': [{'date': c['date'], 'time': c['time'], 'status': c['status'],
                             'buy_url': c.get('buy_url', '')} for c in rows],
        }
        out[kind].append(item)
        if i % 50 == 0:
            sys.stderr.write('  [%d/%d] 発売前%d / 販売中%d / 売切%d / 過去%d / 読めない%d\n'
                             % (i, len(urls), len(out['presale']), len(out['onsale']),
                                len(out['soldout']), len(out['past']), len(out['error'])))
        time.sleep(a.sleep)

    json.dump(out, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('見たページ %d件' % len(urls))
    print('  🎯これから発売 %d件' % len(out['presale']))
    print('  販売中       %d件' % len(out['onsale']))
    print('  売り切れのみ  %d件' % len(out['soldout']))
    print('  過去公演     %d件' % len(out['past']))
    print('  読めない     %d件' % len(out['error']))
    print('→ %s' % a.out)
    return 0


def _selftest():
    rec = {'name': 'テスト', 'perfs': [{'date': '2099-01-01', 'end': ''}],
           'windows': [{'type': '一般発売', 'timming': '2099/01/01(金) 10:00 〜 '}]}
    k, pre, on = classify(rec, [])
    assert k == 'presale' and len(pre) == 1, (k, pre)
    rec2 = dict(rec, windows=[{'type': '一般発売', 'timming': '2020/01/01(水) 10:00 〜 '}])
    assert classify(rec2, [])[0] == 'onsale'
    rec3 = dict(rec, perfs=[{'date': '2020-01-01', 'end': ''}])
    assert classify(rec3, [])[0] == 'past'
    # 全公演が売り切れなら発売前と数えない
    rows = [{'date': '2099-01-01', 'status': 'soldout'}]
    assert classify(rec, rows)[0] == 'soldout'
    # 1公演でも買えるなら数える
    rows2 = [{'date': '2099-01-01', 'status': 'soldout'}, {'date': '2099-01-01', 'status': 'buyable'}]
    assert classify(rec, rows2)[0] == 'presale'
    assert RT.search('https://ticket.rakuten.co.jp/music/rtxr679/')
    assert not RT.search('https://ticket.rakuten.co.jp/notice/')
    print('selftest OK: 発売前/販売中/過去/売切の分け方 / 公演URLの見分け')


if __name__ == '__main__':
    sys.exit(main())
