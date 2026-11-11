# -*- coding: utf-8 -*-
"""TicketDive（チケットダイブ・ticketdive.com＝地下アイドル中心）の公演を集める。

  python tools/ticketdive_harvest.py --out tmp/ticketdive_harvest.json           … 毎朝（登録済みは個別ページを引かない）
  python tools/ticketdive_harvest.py --max-events 100 --out tmp/x1112/ticketdive/harvest.json
  python tools/ticketdive_harvest.py --urls GAOMANZAI2026,CoC_firstyear          … 公演を名指しで引く
  python tools/ticketdive_harvest.py --selftest

## 規約・robots（2026-11-12 に読んだ）
- robots.txt＝`User-agent: * / Allow: /`（全部許可）。
- 利用規約（購入者）＝営利目的の利用の禁止・転載の許諾制・無断転載禁止の条文は無い。
  第10条の禁止事項に「自動入力を行うソフトウェアやいわゆるBOT等の技術的手段…により本サービスを利用する行為」がある
  （買う側のBOTを止める条文と読める）。**申込・ログインは一切しない・1回ごとに数秒あける**。
  第9条＝情報の知的財産は当社か第三者＝**紹介文・画像は写さない**（公演名・日時・会場・受付期間・値段の事実だけ）。

## 一覧が無い売り場（2026-09-27・11-12 実測）
- 全件一覧・新着順・ページ送りが無い。sitemap.xml は LP の2ページだけ（公演0件）。
- 入口は3つ＝①トップ `entryNow`（受付中12件）＋`carousel` ②検索 `/search?q=語`（1語20件まで）
  ③アーティスト `/artist/{id}` の `artistRelatedEntryNow`（その出演者の公演）。
  → ①②で種をまき、**公演の出演者 → その出演者の公演 → また出演者…と芋づるでたどる**（③が取りこぼしを減らす本命）。
  どの入口で何件見つけたかを毎回数える（`sources`）。
- 中身は Next.js の `/_next/data/{buildId}/…json`。buildId は作り直しのたびに変わる＝毎回トップから読む（404なら読み直す）。

## 公演の JSON（`pageProps.__superjsonProps.json.eventDetail`）
- event.name / event.url / event.detail（紹介文＝会場の住所だけ読む・写さない）
- stages[]：startStage（開演・UTC）・openVenue（開場・UTC）・venue.name・venue.address（空が多い）・artists[].name
- ticketInfoList[]（受付ごと）：name（受付名）・release（受付が画面に出る時刻）・startApply/endApply（UTC）・
  receptionType（first＝先着／lottery＝抽選）・status・isFc・ticketTypes[]（name・price・stageIds・remainingRate・status）
- 🚨県の項目が無い＝組み立て側（build_ticketdive_entries）で住所の文字からだけ決める。
"""
import argparse
import datetime
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = 'https://ticketdive.com'
# 🚨UA にメールアドレス・個人の情報を入れない（2026-11-11 Wikimedia の件）
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) OSHINAVI-harvest',
      'Accept-Language': 'ja,en;q=0.8'}
JST = datetime.timezone(datetime.timedelta(hours=9))

# 検索の種（1語20件まで・ページ送りなし）。地下アイドルの公演名に出る語＋地名＋月。
DEFAULT_TERMS = (
    'ライブ 定期公演 生誕 生誕祭 対バン ワンマン 主催 撮影会 チェキ リリイベ アイドル フェス 周年 単独 '
    '2部制 1部 2部 昼公演 夜公演 vol LIVE presents ツアー 公演 イベント 朗読 舞台 漫才 お笑い '
    '東京 大阪 名古屋 福岡 札幌 仙台 渋谷 新宿 池袋 秋葉原 下北沢 高田馬場 浅草 中野 恵比寿 原宿 '
    '五反田 吉祥寺 横浜 心斎橋 梅田 なんば '
    '11月 12月 1月 2月 3月 クリスマス Xmas カウントダウン 年越し 2027'
).split()


def now_jst():
    return datetime.datetime.now(JST)


def fetch(url, tries=3, sleep=3.0):
    """1回ごとに sleep 秒あける（叩きすぎない）。404 はそのまま上に投げる（buildId の読み直しに使う）。"""
    last = None
    for i in range(tries):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40)
            body = r.read().decode('utf-8', 'replace')
            time.sleep(sleep)
            return body
        except urllib.error.HTTPError as e:
            if e.code in (404, 403):
                time.sleep(sleep)
                raise
            last = e
        except Exception as e:
            last = e
        time.sleep(sleep * (i + 2))
    raise last


def next_data(html):
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    return json.loads(m.group(1)) if m else None


def sj(d):
    """pageProps.__superjsonProps.json を返す（無ければ pageProps）。"""
    pp = (d or {}).get('pageProps') or ((d or {}).get('props') or {}).get('pageProps') or {}
    return (pp.get('__superjsonProps') or {}).get('json') or pp


def list_item(x):
    """一覧の1件（トップ・検索・アーティスト共通）を薄くする。"""
    return {'url': x.get('url'), 'id': x.get('id'), 'title': x.get('title'),
            'start': x.get('startEventDate'), 'end': x.get('endEventDate'),
            'stage': x.get('displayStageDate'), 'venue': x.get('venueName'),
            'salesStatus': x.get('salesStatus')}


def list_is_future(it, today):
    """一覧の公演日（end か start か stage のいちばん遅いもの・JST）が今日以降か。日付が無ければ引く（捨てない）。"""
    ds = [to_jst(it.get(k)) for k in ('end', 'start', 'stage')]
    ds = [d for d in ds if d]
    if not ds:
        return True
    return max(d[0] for d in ds) >= today


def to_jst(iso):
    """'2026-11-26T10:30:00.000Z' → ('2026-11-26', '19:30')（JST）。読めなければ None。"""
    if not iso or not isinstance(iso, str):
        return None
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})(?::(\d{2}))?', iso)
    if not m:
        return None
    dt = datetime.datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)),
                           int(m.group(4)), int(m.group(5)), int(m.group(6) or 0), tzinfo=datetime.timezone.utc)
    if iso.endswith('Z') is False and not re.search(r'[+-]\d{2}:?\d{2}$', iso):
        pass   # superjson の Date は必ず Z 付き（実測）。Z が無い形は UTC とみなす
    j = dt.astimezone(JST)
    return (j.strftime('%Y-%m-%d'), '%d:%02d' % (j.hour, j.minute))


EMAIL_RE = re.compile(r'[\w.+-]+@[\w-]+(?:\.[\w-]+)+')
TEL_RE = re.compile(r'0\d{1,4}-\d{1,4}-\d{3,4}')


def scrub(s):
    """紹介文からメールアドレス・電話番号を落とす（tmp/ は公開される＝個人の連絡先を残さない）。"""
    return TEL_RE.sub('', EMAIL_RE.sub('', s or ''))


# 紹介文から拾う語（ジャンルの札を決める語だけ。build_ticketdive_entries.GENRE_WORDS と揃える）
DETAIL_VOCAB = re.compile(r'アイドル|特典会|チェキ会|チェキ撮影|チェキ|生誕祭|定期公演|漫才|お笑い|コント|芸人|'
                          r'朗読劇|舞台|演劇|劇団|公演台本')


def detail_bits(detail, venues):
    """🚨紹介文は**写さない**（第9条＝情報の知的財産は当社か第三者／tmp/ は公開される）。
    残すのは ①会場名か「会場・住所・〒・場所・所在地」を含む行（県を読むため・連絡先は消す・1行120字まで）
    ②ジャンルの札を決める語（DETAIL_VOCAB に当たった語だけ）。"""
    keys = [re.sub(r'\s+', '', v) for v in venues if v and len(re.sub(r'\s+', '', v)) >= 3]
    lines = []
    for ln in (detail or '').splitlines():
        l2 = re.sub(r'\s+', '', ln)
        if any(k in l2 for k in keys) or re.search(r'会場|住所|〒|場所|所在地', ln):
            s = scrub(ln).strip()[:120]
            if s and s not in lines:
                lines.append(s)
    words = sorted(set(DETAIL_VOCAB.findall(detail or '')))
    return lines[:20], words


def slim_event(ed, url):
    """eventDetail から使う欄だけ残す。紹介文は住所の行と札の語だけ（detail_bits）。"""
    ev = ed.get('event') or {}
    stages = []
    for s in (ed.get('stages') or []) + (ed.get('multiDaysStages') or []):
        v = s.get('venue') or {}
        stages.append({'id': s.get('id'), 'name': s.get('stageName'), 'start': s.get('startStage'),
                       'open': s.get('openVenue'), 'venue': v.get('name') or s.get('stageName'),
                       'address': v.get('address') or '',
                       'artists': [{'id': a.get('id'), 'name': a.get('name')} for a in (s.get('artists') or [])],
                       'multi': s in (ed.get('multiDaysStages') or [])})
    infos = []
    for ti in ed.get('ticketInfoList') or []:
        infos.append({'id': ti.get('id'), 'name': ti.get('name'), 'release': ti.get('release'),
                      'startApply': ti.get('startApply'), 'endApply': ti.get('endApply'),
                      'receptionType': ti.get('receptionType'), 'status': ti.get('status'),
                      'isFc': bool(ti.get('isFc')),
                      'types': [{'id': t.get('id'), 'name': t.get('name'), 'price': t.get('price'),
                                 'stageIds': t.get('stageIds') or [], 'remainingRate': t.get('remainingRate'),
                                 'status': t.get('status'), 'receptionType': t.get('receptionType')}
                                for t in (ti.get('ticketTypes') or [])]})
    lines, words = detail_bits(ev.get('detail') or '', [s['venue'] for s in stages])
    return {'url': url, 'page': f'{BASE}/event/{url}', 'id': ev.get('id'), 'name': ev.get('name'),
            'status': ev.get('status'), 'release': ev.get('release'),
            'detail_lines': lines, 'detail_words': words,
            'stages': stages, 'infos': infos}


class Site:
    def __init__(self, sleep):
        self.sleep = sleep
        self.bid = None
        self.calls = 0

    def get(self, url):
        self.calls += 1
        return fetch(url, sleep=self.sleep)

    def top(self):
        nd = next_data(self.get(BASE + '/'))
        self.bid = nd['buildId']
        j = sj(nd['props'])
        items = [list_item(x) for x in (j.get('entryNow') or [])]
        items += [list_item(x) for x in (j.get('carousel') or []) if x.get('url')]
        return items

    def data(self, path, query):
        """/_next/data/{buildId}/{path}.json?{query}。buildId が古くて 404 なら読み直して1回だけやり直す。"""
        for k in range(2):
            if not self.bid:
                self.top()
            u = f'{BASE}/_next/data/{self.bid}/{path}.json?{query}'
            try:
                return json.loads(self.get(u))
            except urllib.error.HTTPError as e:
                if e.code == 404 and k == 0:
                    old = self.bid
                    self.top()
                    if self.bid != old:
                        continue
                raise

    def search(self, q):
        j = sj(self.data('search', 'q=' + urllib.parse.quote(q)))
        return ([list_item(x) for x in (j.get('eventList') or [])],
                [a.get('id') for a in (j.get('artists') or []) if a.get('id')])

    def artist(self, aid):
        j = sj(self.data('artist/' + urllib.parse.quote(aid), 'id=' + urllib.parse.quote(aid)))
        return [list_item(x) for x in (j.get('artistRelatedEntryNow') or [])]

    def event(self, url):
        j = sj(self.data('event/' + urllib.parse.quote(url), 'id=' + urllib.parse.quote(url)))
        ed = j.get('eventDetail')
        if not ed:
            raise ValueError('eventDetail が無い')
        return slim_event(ed, url)


def known_urls(index_path):
    try:
        h = io.open(index_path, encoding='utf-8', newline='').read()
    except Exception:
        return set()
    return set(re.findall(r'ticketdive\.com/event/([A-Za-z0-9_\-.%]+)', h))


def harvest(site, a, today, log=print):
    known = known_urls(a.index) if a.skip_known else set()
    if known:
        log(f'  登録済みのTicketDive公演 {len(known)}件（個別ページは引かない・出演者はたどる）')
    found, src_first, src_any = {}, {}, {}   # url → list_item / 最初に見つけた入口 / 見つけた入口の集合
    ev_q, art_q, art_seen = [], [], set()

    def add(items, src):
        n = 0
        for it in items:
            u = it.get('url')
            if not u:
                continue
            src_any.setdefault(u, set()).add(src.split(':')[0])
            if u in found:
                continue
            found[u] = it
            src_first[u] = src.split(':')[0]
            n += 1
            if list_is_future(it, today):
                ev_q.append(u)
        return n

    def add_artists(ids):
        for i in ids:
            if i and i not in art_seen:
                art_seen.add(i)
                art_q.append(i)

    if a.urls:
        for u in a.urls.split(','):
            add([{'url': u.strip()}], 'urls')
    else:
        try:
            n = add(site.top(), 'top')
            log(f'  トップ（受付中・カルーセル） 新しく{n}件')
        except Exception as e:
            log(f'  ⚠️トップが読めない: {str(e)[:80]}')
        for q in ([] if a.no_search else (a.terms.split(',') if a.terms else DEFAULT_TERMS)):
            try:
                items, arts = site.search(q)
            except Exception as e:
                log(f'  ⚠️検索「{q}」読めない: {str(e)[:60]}')
                continue
            n = add(items, 'search:' + q)
            add_artists(arts)
            log(f'  検索「{q}」 {len(items)}件（新しく{n}件）' + ('  ⚠️20件で打ち切り＝取りこぼしあり' if len(items) >= 20 else ''))

    rows, errs, fetched = [], [], 0
    art_fetched = 0
    # 公演を引く → 出演者を積む → 出演者のページで公演を足す …（芋づる）
    while True:
        if ev_q and (not a.max_events or fetched < a.max_events):
            u = ev_q.pop(0)
            if u in known:
                # 登録済み＝個別ページは引かない（heal/gate が見る）。出演者は分からないので芋づるは止まる
                continue
            fetched += 1
            try:
                d = site.event(u)
            except Exception as e:
                errs.append({'url': u, 'error': str(e)[:120]})
                log(f'  [{fetched}] {u} ERR {str(e)[:60]}')
                continue
            d['found_by'] = src_first.get(u)
            d['found_by_all'] = sorted(src_any.get(u) or [])
            d['list'] = found.get(u) or {}
            rows.append(d)
            if not a.no_artists:
                add_artists([x['id'] for s in d['stages'] for x in s['artists']])
            log(f'  [{fetched}] {u} {(d["name"] or "")[:30]} 公演{len(d["stages"])}/受付{len(d["infos"])}（{d["found_by"]}）')
            continue
        if art_q and not a.no_artists and (not a.max_artists or art_fetched < a.max_artists) \
                and (not a.max_events or fetched < a.max_events):
            aid = art_q.pop(0)
            art_fetched += 1
            try:
                n = add(site.artist(aid), 'artist:' + aid)
            except Exception as e:
                log(f'  ⚠️出演者 {aid} 読めない: {str(e)[:60]}')
                continue
            if n:
                log(f'  出演者 {aid} → 新しく{n}件')
            continue
        break
    stats = {
        'found_total': len(found),
        'found_future': sum(1 for u, it in found.items() if list_is_future(it, today)),
        'by_first_source': {k: sum(1 for v in src_first.values() if v == k) for k in sorted(set(src_first.values()))},
        'fetched_events': fetched, 'artists_seen': len(art_seen), 'artists_fetched': art_fetched,
        'artists_left': len(art_q), 'events_left_in_queue': len([u for u in ev_q if u not in known]),
        'http_calls': site.calls, 'skipped_known': len([u for u in found if u in known]),
    }
    stats['rows_by_first_source'] = {}
    for r in rows:
        stats['rows_by_first_source'][r['found_by']] = stats['rows_by_first_source'].get(r['found_by'], 0) + 1
    return rows, errs, stats


def _selftest():
    assert to_jst('2026-11-26T10:30:00.000Z') == ('2026-11-26', '19:30')
    assert to_jst('2026-10-29T14:59:59.999Z') == ('2026-10-29', '23:59')
    assert to_jst('2026-12-31T15:00:00.000Z') == ('2027-01-01', '0:00')     # 年をまたぐ
    assert to_jst(None) is None and to_jst('') is None
    assert list_is_future({'start': '2026-11-11T10:00:00.000Z', 'end': None}, '2026-11-12') is False
    assert list_is_future({'start': '2026-09-21T02:30:00.000Z', 'end': '2026-11-14T02:30:00.000Z'}, '2026-11-12') is True
    assert list_is_future({}, '2026-11-12') is True                              # 日付が無ければ捨てない
    assert scrub('問い合わせ 和田（warayaki.production@gmail.com）TEL 03-1234-5678') == '問い合わせ 和田（）TEL '
    html = '<script id="__NEXT_DATA__" type="application/json">{"buildId":"abc","props":{"pageProps":{"__superjsonProps":{"json":{"entryNow":[{"url":"x","title":"t"}]}}}}}</script>'
    nd = next_data(html)
    assert nd['buildId'] == 'abc' and sj(nd['props'])['entryNow'][0]['url'] == 'x'
    ed = {'event': {'id': 'E', 'name': '名', 'url': 'u', 'detail': 'mail a@b.cc', 'inquiry': '秘密@x.jp'},
          'stages': [{'id': 'S1', 'stageName': '箱', 'startStage': 'x', 'openVenue': 'y',
                      'venue': {'name': '箱', 'address': ''}, 'artists': [{'id': 'A', 'name': 'あ'}]}],
          'multiDaysStages': [],
          'ticketInfoList': [{'id': 'T', 'name': '一般', 'startApply': 's', 'endApply': 'e', 'status': 'applied',
                              'ticketTypes': [{'id': 'K', 'name': '前売', 'price': 3000, 'stageIds': ['S1'],
                                               'remainingRate': 1, 'status': 'applied'}]}]}
    ed['event']['detail'] = ('アイドルの定期公演です。長い紹介文…\n【会場】下北沢SHELTER（東京都世田谷区北沢2-6-10）\n'
                             '問い合わせ a@b.cc\n箱 で待ってます')
    s = slim_event(ed, 'u')
    assert 'inquiry' not in json.dumps(s, ensure_ascii=False) and 'detail' not in s, s
    assert s['detail_lines'] == ['【会場】下北沢SHELTER（東京都世田谷区北沢2-6-10）'], s['detail_lines']   # 「箱」は2字＝行を拾わない
    assert s['detail_words'] == ['アイドル', '定期公演'] and '@' not in json.dumps(s), s
    assert s['infos'][0]['types'][0]['stageIds'] == ['S1'] and s['stages'][0]['artists'][0]['name'] == 'あ'
    print('selftest OK: to_jst/list_is_future/scrub/next_data/slim_event（連絡先を残さない）')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='tmp/ticketdive_harvest.json')
    ap.add_argument('--sleep', type=float, default=3.0, help='1回ごとの間（秒）')
    ap.add_argument('--max-events', type=int, default=0, help='個別ページを引く上限（0＝無制限）')
    ap.add_argument('--max-artists', type=int, default=0, help='出演者ページを引く上限（0＝無制限）')
    ap.add_argument('--terms', default='', help='検索語（カンマ区切り）。既定は DEFAULT_TERMS')
    ap.add_argument('--no-search', action='store_true')
    ap.add_argument('--no-artists', action='store_true')
    ap.add_argument('--urls', default='', help='公演の url（/event/<url>）を名指し・カンマ区切り')
    ap.add_argument('--skip-known', action='store_true', default=True)
    ap.add_argument('--all', dest='skip_known', action='store_false', help='登録済みも個別ページを引く')
    ap.add_argument('--index', default='index.html')
    ap.add_argument('--today', default=now_jst().date().isoformat())
    a = ap.parse_args([x for x in sys.argv[1:] if x != '--selftest'])
    site = Site(a.sleep)
    rows, errs, stats = harvest(site, a, a.today)
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    json.dump({'today': a.today, 'buildId': site.bid, 'stats': stats, 'events': rows, 'errors': errs},
              io.open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'\n=== 公演 {len(rows)}件 / 読めなかった {len(errs)}件 → {a.out} ===')
    print('入口ごと（最初に見つけた入口・個別ページを引いた分）:', stats['rows_by_first_source'])
    print('統計:', json.dumps(stats, ensure_ascii=False))


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        _selftest()
        sys.exit(0)
    main()
