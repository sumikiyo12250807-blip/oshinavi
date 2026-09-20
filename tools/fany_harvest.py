# -*- coding: utf-8 -*-
"""FANYチケット（吉本興業の売り場 ticket.fany.lol）のハーベスタ。

  python tools/fany_harvest.py --from 2026-09-21 --to 2026-12-31 --out tmp/fany_0921.json
  python tools/fany_harvest.py --selftest

## 入口（2026-09-21 に実測して割った）

検索結果の1ページ目はHTMLに入っているが、**2ページ目以降はJSONのAPIで来る**：

    GET /search/event_more?<検索と同じクエリ>&offset=N     → {"performances":[...10件...], "load_count":10}

offset=0 から10刻みで回せば**全件JSONで取れる**（HTMLを1行も読まなくていい）。
総件数はHTMLの `loadMore()` の中の `newOffset >= N` の N。

## JSONに入っているもの（1公演＝1レコード）

  id(公演id) / event_id(イベントid＝詳細ページ) / name / venue_name / performance_date
  class '01'=単日公演・それ以外は valid_period_start_date〜finish_date の期間もの
  open_start_time_text（開場・開演）/ performer_detail（出演）
  performance_sales[] ＝**販売枠**。1枠ごとに
      sales_name（券種名）/ sales_start_datetime_raw / sales_end_datetime_raw（YYYYMMDDhhmmss）
      display_sales_status（「先着発売中」「抽選受付終了」など）/ display_sales_style（アイコン）
      prefecture_code（都道府県コード！）/ destination_url（申込の飛び先）

🚨**都道府県は販売枠の prefecture_code に入っている**＝会場名からの推定は要らない。

## ジャンル

検索の genre パラメータ（30お笑い/31音楽/32演劇ステージ/33スポーツ/34アニメ/35ゲーム/
36映画LV/37アートイベント/38劇場以外）でもう一周して、**公演id→ジャンル**の対応を作る。
1公演が複数ジャンルに出る（お笑い＋劇場以外など）ので集合で持つ。
ジャンルは**売り場の言う通りに写す**（[[feedback_genre_pia_asis_and_other]]）。
"""
import argparse
import datetime
import io
import json
import re
import sys
import time
import urllib.parse
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = 'https://ticket.fany.lol'
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36')
PAGE = 10  # load_count（実測）

FANY_GENRES = {
    '30': 'お笑い',
    '31': '音楽',
    '32': '演劇/ステージ',
    '33': 'スポーツ',
    '34': 'アニメ',
    '35': 'ゲーム',
    '36': '映画/ライブビューイング',
    '37': 'アート/イベント',
    '38': '劇場以外',
}


def fetch(url, tries=4, sleep=1.0):
    """本文を文字列で返す。取れなければ None（**嘘の空配列を返さない**）。"""
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


def total_count(qs):
    """そのクエリの総件数（HTMLの loadMore の上限値）。取れなければ -1。"""
    html = fetch(BASE + '/search/event?' + qs)
    if html is None:
        return -1
    m = re.search(r'newOffset\s*>=\s*(\d+)', html)
    if m:
        return int(m.group(1))
    # 「もっと見る」が出ない＝1ページで収まっている。カードの数を数える
    if 'fany_performanceListBox__header' in html:
        return len(re.findall(r'fany_performanceListBox__header', html))
    return 0


def sweep(qs, total, label, sleep=0.6):
    """offset を回して公演を全部集める。戻り＝(公演のlist, 取れなかったoffsetのlist)"""
    got, misses = {}, []
    off = 0
    while off < max(total, 1):
        url = BASE + '/search/event_more?' + qs + '&offset=%d' % off
        body = fetch(url)
        if body is None:
            misses.append(off)
            off += PAGE
            continue
        try:
            d = json.loads(body)
        except Exception:  # noqa: BLE001
            misses.append(off)
            off += PAGE
            continue
        perfs = d.get('performances') or []
        for p in perfs:
            got[p.get('id')] = p
        n = d.get('load_count') or len(perfs)
        if not perfs:
            break
        off += max(n, PAGE)
        if off % 200 == 0:
            print('    %s  %d/%d件' % (label, len(got), total))
        time.sleep(sleep)
    return list(got.values()), misses


def harvest(frm, to, out_path, with_genre=True):
    qs_all = urllib.parse.urlencode({'from': frm, 'to': to})
    total = total_count(qs_all)
    print('FANY %s〜%s  総件数 %d件' % (frm, to, total))
    if total < 0:
        print('🚨 件数ページが取れなかった＝中断（嘘のデータを作らない）')
        return 1
    perfs, misses = sweep(qs_all, total, '全体')
    print('  引けた公演 %d件 / 目標 %d件  取れなかったoffset %d個'
          % (len(perfs), total, len(misses)))

    genre_map, genre_counts = {}, {}
    if with_genre:
        for g in sorted(FANY_GENRES):
            qs = urllib.parse.urlencode({'from': frm, 'to': to, 'genre': g})
            n = total_count(qs)
            if n <= 0:
                genre_counts[g] = 0
                continue
            gp, gm = sweep(qs, n, 'genre=%s' % g)
            genre_counts[g] = len(gp)
            for p in gp:
                genre_map.setdefault(str(p.get('id')), []).append(g)
                if p.get('id') not in {x.get('id') for x in perfs}:
                    perfs.append(p)  # 全体クエリから漏れた分を足す
            print('  genre=%s %-10s %d件（目標%d）' % (g, FANY_GENRES[g], len(gp), n))
            if gm:
                misses.extend(gm)

    data = {
        'source': 'fany',
        'fetched_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'range': {'from': frm, 'to': to},
        'total_reported': total,
        'performances': perfs,
        'genre_map': genre_map,
        'genre_counts': genre_counts,
        'missed_offsets': misses,
    }
    with io.open(out_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    print('→ %s  公演 %d件 / 販売枠 %d枠'
          % (out_path, len(perfs), sum(len(p.get('performance_sales') or []) for p in perfs)))
    if misses:
        print('⚠️ 取れなかった要求 %d件＝この分は「無い」ではなく「確かめられていない」' % len(misses))
    return 0


def selftest():
    ok = True
    # ① 件数が読めるか
    today = datetime.date.today()
    qs = urllib.parse.urlencode({
        'from': (today + datetime.timedelta(days=1)).isoformat(),
        'to': (today + datetime.timedelta(days=14)).isoformat(),
        'genre': '30',  # お笑い＝吉本の本業なので常に在庫がある
    })
    n = total_count(qs)
    print('selftest 件数(お笑い 明日〜2週間) = %s' % n)
    if n < 0:
        ok = False
    # ② JSONが読めて、必要な欄が揃っているか
    body = fetch(BASE + '/search/event_more?' + qs + '&offset=0')
    if not body:
        print('🚨 event_more が取れない'); return 1
    d = json.loads(body)
    perfs = d.get('performances') or []
    print('selftest 1ページ目 %d件 / load_count=%s' % (len(perfs), d.get('load_count')))
    need_p = ('id', 'event_id', 'name', 'venue_name', 'performance_date', 'class',
              'performance_sales')
    need_s = ('sales_name', 'sales_start_datetime_raw', 'sales_end_datetime_raw',
              'display_sales_status', 'prefecture_code', 'destination_url')
    if perfs:
        p = perfs[0]
        miss = [k for k in need_p if k not in p]
        print('  公演の欠けた欄: %s' % (miss or 'なし'))
        ok = ok and not miss
        sales = p.get('performance_sales') or []
        if sales:
            miss2 = [k for k in need_s if k not in sales[0]]
            print('  販売枠の欠けた欄: %s' % (miss2 or 'なし'))
            ok = ok and not miss2
        else:
            print('  ⚠️ 販売枠が0（この公演だけかもしれない）')
    else:
        ok = False
    print('selftest %s' % ('OK' if ok else 'NG'))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--from', dest='frm', default=None)
    ap.add_argument('--to', dest='to', default=None)
    ap.add_argument('--out', default=None)
    ap.add_argument('--no-genre', action='store_true')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    frm = a.frm or datetime.date.today().isoformat()
    to = a.to or (datetime.date.today() + datetime.timedelta(days=120)).isoformat()
    out = a.out or ('tmp/fany_%s.json' % datetime.date.today().strftime('%m%d'))
    return harvest(frm, to, out, with_genre=not a.no_genre)


if __name__ == '__main__':
    sys.exit(main())
