# -*- coding: utf-8 -*-
"""ZAIKO（zaiko.io）のハーベスタ。

  python tools/zaiko_harvest.py --out tmp/zaiko_MMDD.json            … 一覧を全部引く
  python tools/zaiko_harvest.py --out tmp/zaiko_MMDD.json --detail   … 未登録の個別ページも引く
  python tools/zaiko_harvest.py --selftest

## 入口（2026-09-21 に実測して割った）

データは **`<script data-page="app" type="application/json">` の中身**（Inertia.js）。
🚨**属性値ではなくタグの中身**。`data-page="([^"]+)"` で取ると値の "app" を読む（1回つまずいた）。

```
一覧  https://zaiko.io/ja/events/category/<slug>?page=N   … 1ページ30件・props.hasMore で続き
個別  https://<主催>.zaiko.io/ja/e/<slug>                  … props.event に全部入っている
```

### 一覧の1件（props.group.items[]）
`title` ／ `details[]`（「AKB48劇場, 東京都」と「09月21日 (月) 13:00」）／
`tags[]`（`{{2026-09-21T13:00:00+09:00|countdown}}`＝**ISO日時**）／`action.url`（イベントURL）

### 個別の props.event
`name` ／ `venue.data`（`name`・`address`・`location`「東京都, 日本」）／`genres` ／
`performers[]`（`name`・`genres`）／`tickets[]`（`display_price`・`is_lottery`・`is_sale_started`・
`is_sale_ended`・**`is_sold_out`**・`is_stream`・`lottery_end_date{iso,date_string,time_string}`）

⚠️ZAIKOはAKB48劇場・hololive・声優公演が入る＝**ぴあに出ない推しの受け皿**。
"""
import argparse
import datetime
import html as H
import io
import json
import re
import sys
import time
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', write_through=True)

BASE = 'https://zaiko.io'
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36')

# カテゴリ（2026-09-21 にトップページのリンクから採った5種）
CATS = {
    'concerts-live-music': 'コンサート・ライブ',
    'performances-shows': '演劇・ショー',
    'festivals-fairs': 'フェス',
    'clubs-nightlife': 'クラブ・ナイトライフ',
    'tournaments-competitions': '大会・競技',
}


def fetch(url, tries=4, sleep=1.0):
    """本文を返す。取れなければ None（**嘘の空配列を返さない**）。"""
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.read().decode('utf-8', 'replace')
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(sleep * (i + 1) * 2)
    sys.stderr.write('  取れなかった: %s (%s)\n' % (url, last))
    return None


def page_data(html):
    """Inertia のデータ（script タグの中身）を dict で返す。"""
    if not html:
        return None
    m = re.search(r'<script[^>]*data-page="app"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        return None
    try:
        return json.loads(H.unescape(m.group(1)))
    except Exception:  # noqa: BLE001
        return None


def iso_from_tags(item):
    """tags の `{{2026-09-21T13:00:00+09:00|countdown}}` から公演日時のISOを取る。"""
    for t in item.get('tags') or []:
        m = re.search(r'(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2})', t.get('name') or '')
        if m:
            return m.group(1), m.group(2)
    return None, None


def detail_from_items(item):
    """details[] から 会場・県 と 表示用の日時文字列を取る。"""
    venue = pref = when = ''
    for d in item.get('details') or []:
        c = (d.get('content') or '').strip()
        if not c:
            continue
        if re.match(r'^\d{1,2}月\d{1,2}日', c):
            when = c
        elif ',' in c or '、' in c:
            # 「AKB48劇場, 東京都」＝会場, 県
            parts = [x.strip() for x in re.split(r'[,、]', c) if x.strip()]
            venue = parts[0]
            if len(parts) > 1:
                pref = parts[-1]
        elif not venue:
            venue = c
    return venue, pref, when


def sweep_category(slug, max_pages=200, sleep=0.7):
    """1カテゴリを頭から全ページ。戻り＝(list, 取れなかったページ)"""
    got, misses, page = {}, [], 1
    while page <= max_pages:
        url = '%s/ja/events/category/%s%s' % (BASE, slug, '' if page == 1 else '?page=%d' % page)
        d = page_data(fetch(url))
        if d is None:
            misses.append(page)
            page += 1
            continue
        props = d.get('props') or {}
        items = (props.get('group') or {}).get('items') or []
        for it in items:
            u = (it.get('action') or {}).get('url')
            if not u:
                continue
            iso, hm = iso_from_tags(it)
            venue, pref, when = detail_from_items(it)
            got[u] = {
                'url': u, 'title': it.get('title') or '', 'subtitle': it.get('subtitle') or '',
                'date': iso, 'time': hm, 'venue': venue, 'pref': pref, 'when_text': when,
                'cat': slug, 'list_id': it.get('id'),
            }
        if not items or not props.get('hasMore'):
            break
        page += 1
        if page % 10 == 0:
            print('    %s  %d件（%dページ目）' % (slug, len(got), page))
        time.sleep(sleep)
    return list(got.values()), misses


def parse_event(html, url):
    """個別ページ → 券種と会場の生データ。取れなければ None。"""
    d = page_data(html)
    if not d:
        return None
    ev = ((d.get('props') or {}).get('event')) or {}
    if not ev:
        return None
    ven = (ev.get('venue') or {}).get('data') or {}
    out = {
        'url': url,
        'name': ev.get('name') or '',
        'subtitle': ev.get('subtitle') or '',
        'status': ev.get('status'),
        'display_date_period': ev.get('display_date_period'),
        'display_open_date': ev.get('display_open_date'),
        'date_notes': ev.get('date_notes'),
        'venue_name': ven.get('name') or '',
        'venue_address': ven.get('address') or '',
        'venue_location': ven.get('location') or '',
        'genres': [g.get('name') for g in (ev.get('genres') or []) if isinstance(g, dict)],
        'performers': [{'name': p.get('name'),
                        'genres': [g.get('name') for g in (p.get('genres') or [])
                                   if isinstance(g, dict)]}
                       for p in (ev.get('performers') or [])],
        'tickets': [],
    }
    for t in ev.get('tickets') or []:
        # 🚨2026-09-21に取りこぼしを直した＝**発売開始日時も券種名も本当はある**。
        #   `on_sale_from`/`on_sale_until`（先着）と `lottery_start_date`/`lottery_end_date`（抽選）が
        #   それぞれ {date_string, time_string, iso} を持つ。初版は lottery_end_date だけ見ていたので
        #   **受付前153枠を「開始日が無い」と判断して落としていた**。
        #   券種名は `front_text` が空でも **`ref_name`（「映像倉庫会員枠」など）に入っている**。
        def dt(key):
            v = t.get(key) or {}
            return {'date': v.get('date_string'), 'time': v.get('time_string'), 'iso': v.get('iso')}
        led, lsd = dt('lottery_end_date'), dt('lottery_start_date')
        osf, osu = dt('on_sale_from'), dt('on_sale_until')
        # 抽選なら抽選の期間、先着なら on_sale の期間を「その券種の受付期間」とする
        start = lsd if t.get('is_lottery') and lsd['date'] else (osf if osf['date'] else lsd)
        end = led if t.get('is_lottery') and led['date'] else (osu if osu['date'] else led)
        out['tickets'].append({
            'id': t.get('id'),
            # 🚨**ref_name が本当の券種名**（「前売券/ADVANCE」「ODYSSEY 3days PASS」）。
            #   `front_text` は**注意書き・説明文**（「20歳未満の方、公共機関が発行する…」）で、
            #   券種名として使うと画面に説明文が並ぶ（2026-09-21 エージェントの指摘で判明）。
            'name': t.get('ref_name') or '',
            'front_text': t.get('front_text') or '',
            'price': t.get('display_price'),
            'is_lottery': t.get('is_lottery'),
            'is_sale_started': t.get('is_sale_started'),
            'is_sale_ended': t.get('is_sale_ended'),
            'is_sold_out': t.get('is_sold_out'),
            'is_stream': t.get('is_stream'),
            'can_apply': t.get('can_do_lottery_application'),
            'start_date': start['date'], 'start_time': start['time'],
            'end_date': end['date'], 'end_time': end['time'], 'end_iso': end['iso'],
            'buy_url': t.get('url') or '',
            # 🚨**券種ごとの公演日時の上書き**。1ページに複数公演を詰めるページがあり
            #   （ダウ9000は4公演／新しい学校のリーダーズは5会場）、これを読まないと
            #   全部イベントの初日で並んで**書いていない日付を書く**ことになる（2026-09-21）。
            'perf_dt': ((t.get('override_datetime_period') or {}).get('datetime_string') or ''),
        })
    return out


def known_urls():
    """index.html に既にある ZAIKO のURL（イベント単位）。"""
    h = io.open('index.html', encoding='utf-8', newline='').read()
    return set(re.findall(r'https://[a-z0-9-]+\.zaiko\.io/ja/e/[A-Za-z0-9_-]+', h))


def harvest(out_path, with_detail, cats, sleep):
    have = known_urls()
    rows, misses = [], []
    for slug in cats:
        n0 = len(rows)
        got, ms = sweep_category(slug, sleep=sleep)
        rows += got
        misses += [(slug, p) for p in ms]
        print('  %-26s %4d件（%s）' % (slug, len(rows) - n0, CATS.get(slug, slug)))
    # URLで重複を外す（同じ公演が複数カテゴリに出る）
    uniq = {}
    for r in rows:
        uniq.setdefault(r['url'], r)
    rows = list(uniq.values())
    newrows = [r for r in rows if r['url'] not in have]
    print('一覧 %d件（ユニーク）／既に登録 %d件／未登録 %d件'
          % (len(rows), len(rows) - len(newrows), len(newrows)))

    details, derr = {}, []
    if with_detail:
        for i, r in enumerate(newrows, 1):
            d = parse_event(fetch(r['url']), r['url'])
            if d is None:
                derr.append(r['url'])
            else:
                details[r['url']] = d
            if i % 50 == 0:
                print('    個別 %d/%d件' % (i, len(newrows)))
            time.sleep(sleep)
        print('  個別ページ %d件（読めなかった %d件）' % (len(details), len(derr)))

    data = {
        'source': 'zaiko',
        'fetched_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'list': rows,
        'new_urls': [r['url'] for r in newrows],
        'details': details,
        'missed_pages': misses,
        'detail_errors': derr,
    }
    with io.open(out_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    print('→ %s' % out_path)
    if misses or derr:
        print('⚠️取れなかった＝一覧%dページ / 個別%d件（「無い」ではなく「確かめられていない」）'
              % (len(misses), len(derr)))
    return 0


def _selftest():
    ok = True
    # ① 一覧が読めて、必要な欄が揃うか
    html = fetch('%s/ja/events/category/concerts-live-music' % BASE)
    d = page_data(html)
    if not d:
        print('🚨一覧の data-page が読めない'); return 1
    props = d.get('props') or {}
    items = (props.get('group') or {}).get('items') or []
    print('selftest 一覧 %d件 / hasMore=%s' % (len(items), props.get('hasMore')))
    ok = ok and len(items) > 0
    if items:
        it = items[0]
        u = (it.get('action') or {}).get('url')
        iso, hm = iso_from_tags(it)
        venue, pref, when = detail_from_items(it)
        print('  1件目: %s / %s %s / %s（%s）' % ((it.get('title') or '')[:30], iso, hm, venue, pref))
        ok = ok and bool(u) and bool(iso)
        # ② 個別ページが読めて、券種の欄が揃うか
        ev = parse_event(fetch(u), u)
        if not ev:
            print('🚨個別ページが読めない: %s' % u); return 1
        print('  個別: %s @ %s（%s）券種%d / 出演%d'
              % (ev['name'][:26], ev['venue_name'], ev['venue_location'],
                 len(ev['tickets']), len(ev['performers'])))
        need = ('price', 'is_sold_out', 'is_sale_ended', 'is_sale_started', 'is_lottery')
        if ev['tickets']:
            miss = [k for k in need if k not in ev['tickets'][0]]
            print('  券種の欠けた欄: %s' % (miss or 'なし'))
            ok = ok and not miss
        else:
            print('  ⚠️券種0（この公演だけかもしれない）')
    print('selftest %s' % ('OK' if ok else 'NG'))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=None)
    ap.add_argument('--detail', action='store_true', help='未登録の個別ページも引く')
    ap.add_argument('--cats', default='', help='カテゴリを絞る（カンマ区切り）')
    ap.add_argument('--sleep', type=float, default=0.7)
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    cats = [c for c in a.cats.split(',') if c.strip()] or list(CATS)
    out = a.out or ('tmp/zaiko_%s.json' % datetime.date.today().strftime('%m%d'))
    return harvest(out, a.detail, cats, a.sleep)


if __name__ == '__main__':
    sys.exit(main())
