# -*- coding: utf-8 -*-
"""B.LEAGUE チケット（https://ticket.bleague.jp/）の試合を取る（2026-11-20 新設）。

  python tools/bleague_harvest.py --out tmp/x1120/newv/bleague/harvest.json        … 全クラブの試合を全部
  python tools/bleague_harvest.py --clubs lh,se --out tmp/x.json                     … クラブ指定
  python tools/bleague_harvest.py --limit 20 --out tmp/x.json                        … 試合の詳細は先頭20件だけ
  python tools/bleague_harvest.py --selftest

## 規約・robots（2026-11-20 に読んだ）
- robots.txt＝`User-Agent: * / Allow: /`（全部許可）
- 規約（Bリーグチケットサービス利用規約）はボットの条文なし（依頼者が確認済み）。
  ＝**買う画面（purchase-process・reserve-*）には触らない／ログインしない／1回ごとに3秒あける**。

## 売り場の形（2026-11-20 実測）
2026年7月に新しくなった Next.js の画面。画面の JS は公開の JSON の API `https://api.ticket.bleague.jp` を呼ぶ。
- クラブの並び：トップ `https://ticket.bleague.jp/` の `<a href="/clubs/<コード>/events">`（2026-11-20 は55クラブ）
- 一覧：`GET /event-summaries:grouped-by-tenant/<コード>` … そのクラブの**ホームとアウェイ**の試合
  （同じ試合が両方のクラブに出る＝eventId で1つにまとめる）
- 取りこぼしの確かめ：`GET /event-calendar/<YYYY-MM>`（日ごとの試合数）と突き合わせ、足りない日は
  `GET /event-summaries:grouped-by-date/<YYYY-MM-DD>` で足す（リーグ主催の特別試合など）
- 試合の詳細：`GET /tenants/<主催コード>/events/<eventId>` … チーム名（正式）・会場名・住所・販売スケジュール・販売終了
- 残り枚数：`GET /tenants/<主催コード>/events/<eventId>/general-sales-package-stocks` … {remaining, total}
- 試合のページ（人が開く所）：`https://ticket.bleague.jp/clubs/<主催コード>/events/<eventId>`
- 時刻は UTC（…Z）。日本時間は +9時間。

## 画面の状態の決まり（画面の JS 2o42zr262i0va.js から読んだ・ログインしていない人の見え方）
- canNavigateToDetail が false → 「準備中」
- salesStatus：SUSPENDED → 準備中／SALE_ENDED → 販売終了／EVENT_CANCELED → 中止／BEFORE_SALE・ON_SALE → 下へ
- 買える販売スケジュール＝条件（condition＝ファンクラブの会員ランク等）が**無い**もの
  - そのどれかが始まっている：残り0（total>0）→ 売り切れ、残りあり → 購入できる
  - どれも始まっていない → いちばん早い開始日時で「発売前」
  - 条件の無いスケジュールが1つも無い → 一般の人は買えない（先行だけ）

## 守ること
- User-Agent に個人の情報を入れない／1回ごとに既定3秒あける（--sleep）
- 読めなかった欄は空のまま残す（推測で埋めない）＝組み立て側が報告に出す
"""
import argparse
import datetime
import io
import json
import re
import sys
import time
import urllib.error
import urllib.request

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

SITE = 'https://ticket.bleague.jp'
API = 'https://api.ticket.bleague.jp'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
JST = datetime.timezone(datetime.timedelta(hours=9))


class Site:
    def __init__(self, sleep=3.0):
        self.sleep = sleep
        self.last = 0.0
        self.calls = 0

    def get(self, url, tries=3, as_json=True):
        last = None
        for i in range(tries):
            wait = self.sleep - (time.time() - self.last)
            if wait > 0:
                time.sleep(wait)
            self.last = time.time()
            self.calls += 1
            try:
                r = urllib.request.urlopen(urllib.request.Request(
                    url, headers={'User-Agent': UA, 'Accept-Language': 'ja',
                                  'Accept': 'application/json' if as_json else 'text/html'}), timeout=60)
                b = r.read().decode('utf-8', 'replace')
                return json.loads(b) if as_json else b
            except urllib.error.HTTPError as ex:
                if ex.code in (400, 403, 404, 410):
                    raise
                last = ex
            except Exception as ex:
                last = ex
            time.sleep(5 * (i + 1))
        raise last

    def clubs(self):
        t = self.get(SITE + '/', as_json=False)
        if 'captcha' in t.lower() or 'challenge' in t.lower() and 'cf-' in t.lower():
            raise RuntimeError('人間かどうかの確認画面が出た＝止める')
        return list(dict.fromkeys(re.findall(r'href="/clubs/([a-z0-9]+)/events"', t)))

    def club(self, code):
        return self.get('%s/clubs/%s' % (API, code))

    def by_tenant(self, code):
        return self.get('%s/event-summaries:grouped-by-tenant/%s' % (API, code)).get('eventSummaries') or []

    def calendar(self, ym):
        return self.get('%s/event-calendar/%s' % (API, ym)).get('eventCalendar') or []

    def by_date(self, d):
        return self.get('%s/event-summaries:grouped-by-date/%s' % (API, d)).get('eventSummaries') or []

    def detail(self, host, eid):
        return self.get('%s/tenants/%s/events/%s' % (API, host, eid))

    def stock(self, host, eid):
        return self.get('%s/tenants/%s/events/%s/general-sales-package-stocks' % (API, host, eid))


def utc_to_jst(s):
    """'2026-12-19T08:05:00Z' → datetime（日本時間・tz付き）。読めなければ None。"""
    if not s or not isinstance(s, str):
        return None
    m = re.match(r'(\d{4})-(\d\d)-(\d\d)T(\d\d):(\d\d)(?::(\d\d))?(?:\.\d+)?Z$', s)
    if not m:
        return None
    dt = datetime.datetime(*[int(x or 0) for x in m.groups()], tzinfo=datetime.timezone.utc)
    return dt.astimezone(JST)


def page_url(host, eid):
    return '%s/clubs/%s/events/%s' % (SITE, host, eid)


def months_between(a, b):
    y, m = int(a[:4]), int(a[5:7])
    out = []
    while '%04d-%02d' % (y, m) <= b[:7]:
        out.append('%04d-%02d' % (y, m))
        m += 1
        if m > 12:
            y, m = y + 1, 1
    return out


def harvest(site, today, clubs=None, limit=0, log=sys.stderr, partial=None):
    codes = clubs or site.clubs()
    log.write('クラブ %d\n' % len(codes))
    club_info, summaries, seen_in = {}, {}, {}
    for c in codes:
        try:
            club_info[c] = site.club(c)
        except Exception as ex:
            club_info[c] = {'error': str(ex)[:80]}
        try:
            for s in site.by_tenant(c):
                summaries.setdefault(s['eventId'], s)
                seen_in.setdefault(s['eventId'], []).append(c)
        except Exception as ex:
            log.write('  一覧が読めない %s: %s\n' % (c, ex))
    # 取りこぼしの確かめ＝カレンダーの日ごとの数と比べ、足りない日は日付の一覧で足す（クラブ指定の時はしない）
    cal_check = []
    if not clubs:
        last = max([s.get('eventStartDateJst') or today for s in summaries.values()] + [today])
        for ym in months_between(today, last):
            for row in site.calendar(ym):
                d, n = row.get('date'), row.get('eventsCount') or 0
                if not d or d < today:
                    continue
                have = sum(1 for s in summaries.values() if s.get('eventStartDateJst') == d)
                added = 0
                if have < n:
                    for s in site.by_date(d):
                        if s['eventId'] not in summaries:
                            summaries[s['eventId']] = s
                            seen_in.setdefault(s['eventId'], []).append('date:' + d)
                            added += 1
                cal_check.append({'date': d, 'calendar': n, 'had': have, 'added': added})
    ids = sorted((s for s in summaries.values() if (s.get('eventStartDateJst') or '') >= today),
                 key=lambda s: (s.get('eventStartDateJst') or '', s.get('eventStartTimeJst') or '', s['eventId']))
    if limit:
        ids = ids[:limit]
    events, errors = [], []
    for i, s in enumerate(ids):
        host, eid = s.get('hostTenantCode'), s['eventId']
        ev = {'id': eid, 'host': host, 'url': page_url(host, eid), 'summary': s, 'detail': None, 'stock': None,
              'listed_in': seen_in.get(eid) or []}
        if s.get('canNavigateToDetail'):
            try:
                ev['detail'] = site.detail(host, eid)
            except Exception as ex:
                errors.append({'id': eid, 'what': 'detail', 'why': str(ex)[:100]})
            if s.get('salesStatus') in ('ON_SALE', 'BEFORE_SALE'):
                try:
                    ev['stock'] = site.stock(host, eid)
                except Exception as ex:
                    errors.append({'id': eid, 'what': 'stock', 'why': str(ex)[:100]})
        events.append(ev)
        if i % 50 == 49:
            log.write('  %d/%d\n' % (i + 1, len(ids)))
            if partial:
                # 途中で止められても（2026-11-20 メモリ不足で900/1165で止まった）集めた分を残す
                json.dump({'partial': True, 'done': i + 1, 'of': len(ids), 'events': events, 'errors': errors,
                           'calendar_check': cal_check, 'listed_total': len(summaries)},
                          io.open(partial, 'w', encoding='utf-8'), ensure_ascii=False)
    return {'clubs': club_info, 'calendar_check': cal_check, 'listed_total': len(summaries),
            'events': events, 'errors': errors}


def _selftest():
    d = utc_to_jst('2026-12-19T08:05:00Z')
    assert d.strftime('%Y-%m-%d %H:%M') == '2026-12-19 17:05', d
    d = utc_to_jst('2026-10-30T15:30:00.000Z')
    assert d.strftime('%Y-%m-%d %H:%M') == '2026-10-31 00:30', d       # 日付がまたぐ
    assert utc_to_jst('$undefined') is None and utc_to_jst(None) is None
    assert months_between('2026-11-20', '2027-02-03') == ['2026-11', '2026-12', '2027-01', '2027-02']
    assert page_url('lh', 'abc') == 'https://ticket.bleague.jp/clubs/lh/events/abc'
    print('selftest OK（UTC→日本時間・日付またぎ・月の並び・試合ページのURL）')
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='tmp/bleague.json')
    ap.add_argument('--clubs', default='')
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--sleep', type=float, default=3.0)
    ap.add_argument('--today', default=datetime.datetime.now(JST).date().isoformat())
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        sys.exit(_selftest())
    site = Site(a.sleep)
    clubs = [x for x in re.split(r'[,\s]+', a.clubs) if x] or None
    d = harvest(site, a.today, clubs, a.limit, partial=a.out + '.partial')
    d['harvested_at'] = datetime.datetime.now(JST).strftime('%Y-%m-%d %H:%M')
    d['today'] = a.today
    json.dump(d, io.open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    short = sum(1 for c in d['calendar_check'] if c['had'] + c['added'] < c['calendar'])
    sys.stderr.write('bleague_harvest: clubs=%d listed=%d read=%d errors=%d calls=%d カレンダーより少ない日=%d -> %s\n'
                     % (len(d['clubs']), d['listed_total'], len(d['events']), len(d['errors']), site.calls, short, a.out))


if __name__ == '__main__':
    main()
