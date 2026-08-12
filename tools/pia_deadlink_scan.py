#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""登録中のぴあURLを全部叩いて「消えたページ」を洗い出す（恒久ツール）。

なぜ必要か:
  ぴあは単独公演の eventCd を消してツアーの eventBundleCd に作り直すことがある。
  その時 links.pia は HTTP 200 のまま「ご指定の公演情報が見つかりませんでした」を返すので、
  サイトの購入ボタンが無言で死ぬ（2026-08-12 に ザ・シスターズハイ / PompadollS で実害）。
  reconcile_pia は「0枠」として出すが、全エントリには掛けていないので取りこぼす。

判定:
  DEAD  … 公演情報が見つからない旨のエラーページ
  429   … レート制限（判定不能。時間を置いて再実行する。DEADと混ぜない）
  ERR   … 通信/HTTPエラー
  OK    … 正常なイベントページ

使い方:
  python tools/pia_deadlink_scan.py                 # 表示中エントリのみ（既定）
  python tools/pia_deadlink_scan.py --all           # 非表示エントリも含める
  python tools/pia_deadlink_scan.py --limit 200     # 先頭N件だけ
  python tools/pia_deadlink_scan.py --sleep 1.2
"""
import datetime
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_expired import extract_events_array

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

OUT = 'tmp/pia_deadlink.json'
DEAD_MARKS = (
    'ご指定の公演情報が見つかりませんでした',
    '公演情報が見つかりませんでした',
    'アーティスト情報が存在しません',
    'ご指定のページは存在しません',
)
TODAY = datetime.date.today().isoformat()


def opt(name, cast=str, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        if i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith('--'):
            return cast(sys.argv[i + 1])
    return default


def visible(ev):
    """index.html renderCard の非表示判定と同じ＝表示される枠が1つでもあるか。"""
    for t in ev.get('tickets') or []:
        sd, d = t.get('startDate'), t.get('date')
        if (not sd or sd <= TODAY) and (d or '9999') < TODAY:
            continue
        return True
    return False


def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req, timeout=timeout).read().decode('utf-8', 'replace')


def main():
    only_all = '--all' in sys.argv
    limit = opt('--limit', int)
    sleep = opt('--sleep', float, 1.0)

    events = extract_events_array('index.html')
    # URL -> それを使っているエントリ（id, 名前）
    users = {}
    for e in events:
        if not only_all and not visible(e):
            continue
        seen = set()
        p = (e.get('links') or {}).get('pia')
        if p:
            seen.add(p)
        for t in e.get('tickets') or []:
            u = t.get('url')
            if u and 'pia' in u:
                seen.add(u)
        for u in seen:
            users.setdefault(u, []).append((e.get('id'), e.get('name')))

    urls = sorted(users)
    if limit:
        urls = urls[:limit]
    print('対象URL %d 本 / 対象エントリ %d 件（%s）'
          % (len(urls), len({i for v in users.values() for i, _ in v}),
             '全部' if only_all else '表示中のみ'))

    rows = []
    counts = {'OK': 0, 'DEAD': 0, '429': 0, 'ERR': 0}
    for n, u in enumerate(urls, 1):
        st, note = 'OK', ''
        try:
            h = fetch(u)
            if any(mk in h for mk in DEAD_MARKS):
                st = 'DEAD'
        except urllib.error.HTTPError as ex:
            st, note = ('429' if ex.code == 429 else 'ERR'), 'HTTP %s' % ex.code
        except Exception as ex:
            st, note = 'ERR', str(ex)[:60]
        counts[st] += 1
        if st != 'OK':
            for i, nm in users[u]:
                print('  [%s] id=%s %s\n        %s %s' % (st, i, (nm or '')[:40], u, note))
        rows.append({'url': u, 'status': st, 'note': note,
                     'entries': [{'id': i, 'name': nm} for i, nm in users[u]]})
        if n % 100 == 0:
            print('  … %d/%d  OK%d DEAD%d 429:%d ERR%d'
                  % (n, len(urls), counts['OK'], counts['DEAD'], counts['429'], counts['ERR']))
        time.sleep(sleep)

    json.dump(rows, io.open(OUT, 'w', encoding='utf-8', newline='\n'),
              ensure_ascii=False, indent=1)
    print('\n=== OK %d / 🚨DEAD %d / 429 %d / ERR %d → %s ==='
          % (counts['OK'], counts['DEAD'], counts['429'], counts['ERR'], OUT))
    if counts['429']:
        print('⚠️ 429が出た＝その分は判定不能。時間を置いて再実行して（DEADと混ぜない）。')


if __name__ == '__main__':
    main()
