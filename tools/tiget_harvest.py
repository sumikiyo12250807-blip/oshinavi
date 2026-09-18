# -*- coding: utf-8 -*-
"""TIGET（チゲット）のイベントを取る。YouTuber／VTuber から始める（2026-09-18 ユーザー決定）。

  python tools/tiget_harvest.py                 … 既定カテゴリ 81(YouTuber),84(VTuber)
  python tools/tiget_harvest.py --cats 81,84    … カテゴリ指定
  python tools/tiget_harvest.py --selftest      … パーサーの回帰テスト

## なぜ TIGET か（2026-09-18 に実測して決めた）

ユーザー「YouTuberのイベント、別々でチケット売ってる感じ／ぴあであまり見ない／載せていきたい」。
調べたら TIGET は**基本利用無料で個人でも売れる**仕組みで、**カテゴリに「YouTuber」(81)と
「VTuber」(84)が正式にある**＝ぴあに出てこない小さなイベントの本場。

🚨うちが要るものが全部ページに載っている（実測＝events/516046「最」ライブツアー2026 in 大阪）：
  ・券種名＋価格（優先入場 5,500円 / 一般 3,500円）
  ・公演日＋開場時刻（2026年10月18日(日) 12:00開場）
  ・会場＋都道府県（J．Bridgeビル(大阪府)）
  ・**受付期間**（カード決済 2026.09.13 21:00 ~ 2026.10.17 23:59／コンビニ決済 ~ 10.14 23:59）
    ＝OSHINAVIのカウントダウンがそのまま作れる
  ・完売／一部完売／残りわずか の状態

## ページの形（実測）

一覧  : https://tiget.net/events?categories=<cat>&sort=new_arrivals[&page=N]
        1ページ24件・ページ送りは href に page= が出る（最後のページ番号も出る）
個別  : https://tiget.net/events/<id>
        <div class="pg-event__ordering__program">           … 公演（日時）ごとの塊
          <div class="...__program__datetime">▼ 2026年10月18日(日)　12:00開場</div>
          <div class="c-ordering-btn is-available">          … 券種ごと
            <div class="c-ordering-btn__content__name">優先入場<br><div class="play-date-label">…</div>5,500円</div>
            <div class="purchase-period__label">カード決済</div>
            <div class="purchase-period__value">:2026.09.13 21:00 ~ 2026.10.17 23:59</div>
"""
import argparse
import gzip
import io
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = 'https://tiget.net'
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) OSHINAVI-harvest'}
CAT_NAME = {'81': 'YouTuber', '84': 'VTuber', '79': '歌い手', '80': 'ボカロ',
            '29': 'アイドル', '45': 'ショー／ファンイベント', '46': 'トークショー／講演会',
            '41': 'アニメ／ゲーム／声優'}
PREF47 = ('北海道 青森県 岩手県 宮城県 秋田県 山形県 福島県 茨城県 栃木県 群馬県 埼玉県 千葉県 東京都 '
          '神奈川県 新潟県 富山県 石川県 福井県 山梨県 長野県 岐阜県 静岡県 愛知県 三重県 滋賀県 京都府 '
          '大阪府 兵庫県 奈良県 和歌山県 鳥取県 島根県 岡山県 広島県 山口県 徳島県 香川県 愛媛県 高知県 '
          '福岡県 佐賀県 長崎県 熊本県 大分県 宮崎県 鹿児島県 沖縄県').split()


def fetch(url, tries=3):
    for i in range(tries):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40)
            raw = r.read()
            if r.headers.get('Content-Encoding') == 'gzip':
                raw = gzip.decompress(raw)
            return raw.decode('utf-8', 'replace')
        except Exception as e:
            if i == tries - 1:
                raise
            time.sleep(2.5 * (i + 1))


def strip_tags(s):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s or '')).strip()


def unesc(s):
    import html as _h
    return _h.unescape(s or '')


def pref_of(text):
    """「J．Bridgeビル(大阪府)」→「大阪」。47都道府県の名前しか県として認めない。"""
    for p in PREF47:
        if p in (text or ''):
            return p[:-1] if p != '北海道' else p
    return None


def parse_jp_date(s):
    """「2026年10月18日(日)」→ 2026-10-18"""
    m = re.search(r'(\d{4})年\s*(\d{1,2})月\s*(\d{1,2})日', s or '')
    return '%04d-%02d-%02d' % (int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else None


def parse_period(s):
    """「:2026.09.13 21:00 ~ 2026.10.17 23:59」→ (開始iso, 開始時刻, 終了iso, 終了時刻)"""
    m = re.search(r'(\d{4})\.(\d{2})\.(\d{2})\s*(\d{1,2}:\d{2})?\s*[~〜]\s*(\d{4})\.(\d{2})\.(\d{2})\s*(\d{1,2}:\d{2})?',
                  s or '')
    if not m:
        return None
    return ('%s-%s-%s' % (m.group(1), m.group(2), m.group(3)), m.group(4) or '',
            '%s-%s-%s' % (m.group(5), m.group(6), m.group(7)), m.group(8) or '')


def parse_list_meta(html):
    """一覧ページのカードから「場所：<都道府県>」「開催：<日付>」「あとN日/完売」を取る。
    🚨個別ページのJSON-LDに住所が無いイベントがある（「大阪心斎橋某所」「船橋ダートフィールド」など
       11件が県なしだった＝2026-09-18）。**一覧の event-area は TIGET自身が持っている都道府県**なので、
       これを県の正とする（会場名から市名を推測して県を当てるのは推測になるのでやらない）。"""
    meta = {}
    for cm in re.finditer(r'<div class="event-title"><a href="/events/(\d+)">(.*?)</a></div>(.*?)(?=<div class="col-xs-12|$)',
                          html, re.S):
        eid, blk = cm.group(1), cm.group(3)
        am = re.search(r'class="event-area">\s*場所：([^<]+)</div>', blk)
        pd = re.search(r'class="play-date">\s*開催：([^<]+)</div>', blk)
        st = re.search(r"class='c-statusbox__tag'>([^<]+)<", blk)
        cur = meta.setdefault(eid, {})
        if am and not cur.get('area'):
            cur['area'] = unesc(am.group(1)).strip()
        if pd and not cur.get('play_date'):
            cur['play_date'] = unesc(pd.group(1)).strip()
        if st and not cur.get('status_tag'):
            cur['status_tag'] = unesc(st.group(1)).strip()
    return meta


def parse_list_page(html):
    """一覧ページから イベントid と 最大ページ番号 を取る。"""
    ids = []
    for m in re.finditer(r'href="/events/(\d+)"', html):
        if m.group(1) not in ids:
            ids.append(m.group(1))
    # 🚨 href は `&amp;page=2` の形で出る＝`[?&]page=` では当たらない（`;` が直前に来る）。
    #    2026-09-18 にこれで「1ページしかない」と読み違えた。unescape してから探す。
    pages = {int(x) for x in re.findall(r'[?&]page=(\d+)', unesc(html))} | {1}
    return ids, max(pages)


def parse_event(html, eid):
    """個別ページから公演・券種を取る。"""
    out = {'id': eid, 'url': f'{BASE}/events/{eid}', 'name': None, 'venue': None,
           'prefecture': None, 'performers': [], 'programs': [], 'statuses': []}
    m = re.search(r'<title>(.*?)</title>', html, re.S)
    if m:
        t = unesc(strip_tags(m.group(1)))
        out['name'] = re.sub(r'\s*のチケット購入・予約は TIGET から\s*$', '', t)
    # 「イベント詳細」は <dl><dt>見出し</dt><dd>中身</dd></dl> の形（JSON-LDは住所が NaN のことがある）
    sec = {}
    for dm in re.finditer(r'<dt class="pg-event__detail__title">(.*?)</dt>\s*<dd class="pg-event__detail__contents">(.*?)</dd>',
                          html, re.S):
        sec[unesc(strip_tags(dm.group(1)))] = dm.group(2)
    out['detail_date'] = parse_jp_date(unesc(strip_tags(sec.get('開催日', ''))))
    ven = unesc(strip_tags(sec.get('会場', '')))
    out['venue'] = re.sub(r'\((?:[^()]*)\)\s*$', '', ven).strip() or None
    # 🚨会場名に県が入っていないことがある（船橋ダートフィールド／WISH BASE大阪スカイビル前店）。
    #    JSON-LD の addressRegion を控えの県として持つ（2026-09-18＝バッジが「（会場 11/21公演）」になった）。
    rm = re.search(r'"addressRegion":\s*"([^"]+)"', html)
    out['ld_region'] = rm.group(1) if rm else None
    out['prefecture'] = pref_of(ven) or pref_of(out['ld_region'] or '')
    # 出演者は <a href="/performers/…">名前</a> だけを取る（説明文を巻き込まないため）
    out['performers'] = [unesc(strip_tags(x)) for x in
                         re.findall(r'<a href="/performers/\d+">(.*?)</a>', sec.get('出演者', ''), re.S)][:10]
    # 🚨JSON-LD の offers に **販売開始時刻（validFrom）** が入っている。
    #    「当日支払い」の券種はHTMLに受付期間の欄が出ないので、発売日はここからしか取れない
    #    （2026-09-18＝36件がこの形だった。推測で日付を作らないための命綱）。
    #    ※このJSON-LDは `//コメント` 入りで json.loads できないので正規表現で読む。
    ldm = re.search(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', html, re.S)
    offers = []
    if ldm:
        for om in re.finditer(r'"@type":\s*"Offer"(.*?)(?=\{\s*"@type"|\]|\}\s*,\s*"performer)', ldm.group(1), re.S):
            blk = om.group(1)
            pm = re.search(r'"price":\s*"?([0-9]+)', blk)
            vm = re.search(r'"validFrom":\s*"(\d{4})-(\d{2})-(\d{2})T(\d{1,2}:\d{2})', blk)
            am = re.search(r'"availability":\s*"[^"]*?/(\w+)"', blk)
            offers.append({'price': int(pm.group(1)) if pm else None,
                           'valid_from': f'{vm.group(1)}-{vm.group(2)}-{vm.group(3)}' if vm else None,
                           'valid_from_time': vm.group(4) if vm else None,
                           'availability': am.group(1) if am else None})
    out['ld_offers'] = offers
    # 公演（日時）ごとの塊
    for pm in re.finditer(r'<div class="pg-event__ordering__program">(.*?)(?=<div class="pg-event__ordering__program">|<div class="pg-event__ordering__caption">)',
                          html, re.S):
        blk = pm.group(1)
        dt = strip_tags(re.search(r'__program__datetime">(.*?)</div>', blk, re.S).group(1)) if re.search(r'__program__datetime">', blk) else ''
        dt = unesc(dt).replace('▼', '').strip()
        prog = {'datetime_text': dt, 'date': parse_jp_date(dt), 'tickets': []}
        # 🚨券種の塊は「次の c-ordering-btn まで」で切る。閉じタグの並びで切ると
        #   2つめの受付期間（コンビニ決済）を落とす（2026-09-18 に実測で気づいた）。
        parts = re.split(r'<div class="c-ordering-btn ([^"]*)">', blk)
        for k in range(1, len(parts) - 1, 2):
            cls, tb = parts[k].strip(), parts[k + 1]
            out['statuses'].append(cls)
            nm = re.search(r'__content__name">(.*?)</div>\s*<div class="c-ordering-btn__content__status', tb, re.S)
            raw = nm.group(1) if nm else ''
            name = unesc(strip_tags(re.sub(r'<div class="play-date-label">.*?</div>', ' ', raw, flags=re.S)))
            price = None
            pm2 = re.search(r'([0-9,]+)\s*円', name)
            if pm2:
                price = int(pm2.group(1).replace(',', ''))
                name = name.replace(pm2.group(0), '').strip()
            periods = []
            for lm, vm in zip(re.finditer(r'purchase-period__label">(.*?)</div>', tb, re.S),
                              re.finditer(r'purchase-period__value">(.*?)</div>', tb, re.S)):
                periods.append({'pay': unesc(strip_tags(lm.group(1))),
                                'text': unesc(strip_tags(vm.group(1))),
                                'parsed': parse_period(strip_tags(vm.group(1)))})
            prog['tickets'].append({'name': name, 'price': price, 'class': cls, 'periods': periods})
        out['programs'].append(prog)
    return out


def _selftest():
    assert parse_jp_date('2026年10月18日(日)') == '2026-10-18'
    assert parse_period(':2026.09.13 21:00 ~ 2026.10.17 23:59') == ('2026-09-13', '21:00', '2026-10-17', '23:59')
    assert parse_period('なし') is None
    assert pref_of('J．Bridgeビル(大阪府)') == '大阪'
    assert pref_of('札幌の店(北海道)') == '北海道'
    assert pref_of('どこかの箱') is None
    ids, mx = parse_list_page('<a href="/events/1"></a><a href="/events/2"></a><a href="/events?categories=81&amp;page=3">')
    assert ids == ['1', '2'] and mx == 3, (ids, mx)
    lm = parse_list_meta('<div class="event-title"><a href="/events/9">名</a></div>'
                         '<div class="play-date">開催：2026年11月21日(土)</div>'
                         '<div class="event-area">場所：東京都</div>')
    assert lm['9']['area'] == '東京都' and lm['9']['play_date'] == '2026年11月21日(土)', lm
    print('selftest OK: parse_jp_date/parse_period/pref_of/parse_list_page/parse_list_meta')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cats', default='81,84')
    ap.add_argument('--out', default='tmp/tiget_harvest.json')
    ap.add_argument('--sleep', type=float, default=1.0)
    ap.add_argument('--limit', type=int, default=0)
    a = ap.parse_args([x for x in sys.argv[1:] if x != '--selftest'])

    events, order = {}, []
    for cat in a.cats.split(','):
        page, last = 1, 1
        while page <= last:
            u = f'{BASE}/events?categories={cat}&sort=new_arrivals' + (f'&page={page}' if page > 1 else '')
            html = fetch(u)
            ids, mx = parse_list_page(html)
            last = max(last, mx)
            lm = parse_list_meta(html)
            for i in ids:
                if i not in events:
                    events[i] = {'cats': [], 'list': {}}
                    order.append(i)
                if cat not in events[i]['cats']:
                    events[i]['cats'].append(cat)
                events[i]['list'].update(lm.get(i) or {})
            print(f'  一覧 cat={cat}({CAT_NAME.get(cat, cat)}) page={page}/{last} … {len(ids)}件 / 累計{len(order)}件')
            page += 1
            time.sleep(a.sleep)

    rows, errs = [], []
    todo = order[:a.limit] if a.limit else order
    for n, eid in enumerate(todo, 1):
        try:
            d = parse_event(fetch(f'{BASE}/events/{eid}'), eid)
            d['cats'] = events[eid]['cats']
            d['cat_names'] = [CAT_NAME.get(c, c) for c in d['cats']]
            d['list'] = events[eid].get('list') or {}
            # 県は「一覧の 場所：」が正（TIGET自身が持っている値）。無いときだけ会場名/JSON-LDから
            d['prefecture'] = pref_of(d['list'].get('area') or '') or d['prefecture']
            rows.append(d)
            slots = sum(len(p['tickets']) for p in d['programs'])
            print(f'  [{n}/{len(todo)}] {eid} {(d["name"] or "")[:34]} 公演{len(d["programs"])}/券種{slots}')
        except Exception as e:
            errs.append({'id': eid, 'error': str(e)[:120]})
            print(f'  [{n}/{len(todo)}] {eid} ERR {str(e)[:60]}')
        time.sleep(a.sleep)

    json.dump({'cats': a.cats, 'events': rows, 'errors': errs},
              io.open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    cls = {}
    for r in rows:
        for c in r['statuses']:
            cls[c] = cls.get(c, 0) + 1
    print(f'\n=== イベント {len(rows)}件 / 読めなかった {len(errs)}件 → {a.out} ===')
    print('券種のクラス（売り状態）:', sorted(cls.items(), key=lambda x: -x[1]))


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        _selftest()
        sys.exit(0)
    main()
