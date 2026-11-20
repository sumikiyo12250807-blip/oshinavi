# -*- coding: utf-8 -*-
"""チケットボード（https://ticket.tickebo.jp/）の公演を取る（2026-11-20 新設）。

  python tools/tickebo_harvest.py --out tmp/x1120/newv/tickebo/harvest.json
  python tools/tickebo_harvest.py --ids 16821,16900 --out tmp/x.json
  python tools/tickebo_harvest.py --selftest

## 規約・robots（2026-11-20 に読んだ）
- robots.txt＝空（0バイト＝禁止なし）。sitemap.xml は 503/504（使えない）。
- 規約はボットの条文なし（依頼者が確認済み）＝**申込みの画面（ticket_select・checklist・ログイン）には触らない**。

## 売り場の形（2026-11-20 実測・jQuery＋Vue の画面が JSON を読む）
- 一覧：`GET /web/api/top/ticket-board-top` … トップの「メイン」「新着」「ジャンル別（ライブ＆ミュージック／イベント＆レジャー／定価トレード）」
  🚨**検索・全件の一覧の API は無い**（画面にも検索が無い）＝トップに出ている公演だけが機械で辿れる全部。
  1件＝acceptanceNo（受付ページ番号）か externalUrl（`/show/event.html?info=<番号>`・`/sn/…` の特設ページ）
- 個別：`GET /web/api/evt/sales-list?acceptanceNo=<番号>` …
  eventGroup（題名・出演者・初日・最終日）／sales（受付＝salesNo・salesNmWeb・salesType 01抽選/03先着・tradeFlg 定価トレード）／
  events（公演＝eventOn・開場 openVenueTm・開演 openEventTm・venueNm・prefectureCd（JIS 01〜47）・openType 05＝公演終了・
          acceptanceStatuses［受付ごと before/during/after・その公演の受付開始/終了］・salesRemainNums［受付ごとの残り枚数］）
- 人が開くページ：`https://ticket.tickebo.jp/show/event.html?info=<番号>`
- 時刻は日本時間（Z なし）。

## 守ること
- User-Agent に個人の情報を入れない／1回ごとに既定3秒あける（--sleep）
- 読めなかった欄は空のまま残す（推測で埋めない）
"""
import argparse
import datetime
import io
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

BASE = 'https://ticket.tickebo.jp'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
JST = datetime.timezone(datetime.timedelta(hours=9))


class Site:
    def __init__(self, sleep=3.0):
        self.sleep = sleep
        self.last = 0.0
        self.calls = 0

    def get(self, path, tries=3):
        last = None
        for i in range(tries):
            w = self.sleep - (time.time() - self.last)
            if w > 0:
                time.sleep(w)
            self.last = time.time()
            self.calls += 1
            try:
                r = urllib.request.urlopen(urllib.request.Request(
                    BASE + path, headers={'User-Agent': UA, 'Accept-Language': 'ja', 'Accept': 'application/json'}), timeout=60)
                b = r.read().decode('utf-8', 'replace')
                if b.lstrip().startswith('<'):
                    if re.search(r'captcha|challenge', b, re.I):
                        raise RuntimeError('人間かどうかの確認画面が出た＝止める')
                    raise ValueError('JSON ではなく HTML が返った')
                return json.loads(b)
            except urllib.error.HTTPError as ex:
                if ex.code in (400, 403, 404, 410):
                    raise
                last = ex
            except (RuntimeError, ValueError):
                raise
            except Exception as ex:
                last = ex
            time.sleep(5 * (i + 1))
        raise last

    def top(self):
        return self.get('/web/api/top/ticket-board-top')

    def sales(self, no):
        return self.get('/web/api/evt/sales-list?' + urllib.parse.urlencode({'acceptanceNo': no}))


def top_items(d):
    """トップの JSON → {受付ページ番号: {'cats': [...], 'where': [...], 'title':, 'performers':}}, 公演ページ以外の行き先"""
    got, other = {}, []
    lists = [('メイン', d.get('mainVisuals') or []), ('新着', d.get('newEvents') or [])]
    for c in d.get('categories') or []:
        lists.append(('ジャンル:' + (c.get('categoryNm') or ''), c.get('categoryVisuals') or []))
    for where, items in lists:
        for it in items:
            no = it.get('acceptanceNo')
            if not no:
                m = re.search(r'tickebo\.jp/show/event\.html\?info=(\d+)', it.get('externalUrl') or '')
                no = m.group(1) if m else None
            if not no:
                other.append({'url': it.get('externalUrl'), 'title': it.get('eventGroupTitleWeb'), 'where': where})
                continue
            g = got.setdefault(str(no), {'cats': [], 'where': [], 'title': it.get('eventGroupTitleWeb'),
                                         'performers': it.get('performerNmWeb') or []})
            cats = it.get('categoryNm') or []
            if where.startswith('ジャンル:'):
                cats = cats or [where[5:]]
            for c in cats:
                if c and c not in g['cats']:
                    g['cats'].append(c)
            if where.startswith('ジャンル:') and where[5:] not in g['cats']:
                g['cats'].append(where[5:])
            if where not in g['where']:
                g['where'].append(where)
    return got, other


def harvest(site, ids=None):
    top = site.top()
    items, other = top_items(top)
    want = ids or sorted(items, key=int)
    events, errors = [], []
    for no in want:
        try:
            d = site.sales(no)
            if not isinstance(d, dict) or not d.get('eventGroup'):
                raise ValueError('eventGroup が無い（受付ページが閉じた疑い）')
            events.append({'id': int(no), 'url': '%s/show/event.html?info=%s' % (BASE, no),
                           'top': items.get(str(no)) or {}, 'data': {k: d.get(k) for k in ('eventGroup', 'sales', 'events')}})
        except RuntimeError:
            raise
        except Exception as ex:
            errors.append({'id': no, 'why': str(ex)[:120]})
    return {'listed_total': len(items), 'not_event_pages': other, 'events': events, 'errors': errors}


def _selftest():
    d = {'mainVisuals': [{'acceptanceNo': None, 'externalUrl': 'https://ticket.tickebo.jp/show/event.html?info=16821&tbtag=top',
                          'categoryNm': ['ライブ＆ミュージック'], 'eventGroupTitleWeb': 'A', 'performerNmWeb': ['NMIXX']}],
         'newEvents': [{'acceptanceNo': 16821, 'categoryNm': ['ライブ＆ミュージック']},
                       {'acceptanceNo': None, 'externalUrl': 'https://ticket.tickebo.jp/sn/x', 'eventGroupTitleWeb': 'B'}],
         'categories': [{'categoryNm': '定価トレード', 'categoryVisuals': [{'acceptanceNo': 17000}]}]}
    got, other = top_items(d)
    assert sorted(got) == ['16821', '17000'], got
    assert got['16821']['cats'] == ['ライブ＆ミュージック'] and got['16821']['where'] == ['メイン', '新着'], got
    assert got['17000']['cats'] == ['定価トレード'] and len(other) == 1, (got, other)
    print('selftest OK（トップの一覧の番号・ジャンル札・公演ページ以外の行き先）')
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='tmp/tickebo.json')
    ap.add_argument('--ids', default='')
    ap.add_argument('--sleep', type=float, default=3.0)
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        sys.exit(_selftest())
    site = Site(a.sleep)
    ids = re.findall(r'\d+', a.ids) or None
    d = harvest(site, ids)
    d['harvested_at'] = datetime.datetime.now(JST).strftime('%Y-%m-%d %H:%M')
    json.dump(d, io.open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    sys.stderr.write('tickebo_harvest: listed=%d read=%d errors=%d calls=%d -> %s\n'
                     % (d['listed_total'], len(d['events']), len(d['errors']), site.calls, a.out))


if __name__ == '__main__':
    main()
