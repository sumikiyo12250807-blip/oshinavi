# -*- coding: utf-8 -*-
"""楽天チケット ハーベスタ（2026-07-25 新設・ユーザー「楽天チケットもちゃんと見てね」）。

使い方:
  python tools/rakuten_harvest.py                # 既定=直近60日更新のページを走査
  python tools/rakuten_harvest.py --days 30 --out tmp/rakuten_cand.json
  python tools/rakuten_harvest.py --selftest     # パーサの回帰テスト

【入口】ぴあと違い一覧APIが無いが、**sitemap.xml に全公演URL(約26,000件)が載っている**。
  sitemap.xml → post-sitemap*.xml / static_event-sitemap.xml → <loc>+<lastmod>
  lastmod が新しいものだけ辿れば「今動いている公演」に絞れる（古いものは2019年で止まる）。

【1ページから機械で取れるもの】※全部 静的HTML
  - 公演名     : og:title の「｜楽天チケット」より前
  - ジャンル   : パンくず「Top » 音楽 » Jポップ・ロック » アイドル »」＝ぴあカテゴリ相当の下ごしらえ
  - 各公演     : performances-body 内の「YYYY年 MM月 DD日 (曜) / 公演時間 / エリア:都道府県 / 会場:」
  - 販売枠     : <script> var salesDisplayStatus = {...} の sales_group(枠名)/timming(期間)/sales_status
                 ※枠が1つだけのページは salesDisplayStatus=false → 本文「販売期間: <枠名> 開始 〜 終了」を読む
  - 販売状態   : 各公演カードの「販売終了」「受付中」等のラベル

【重要】楽天の個別ページを WebFetch で読むと販売中でも「販売終了」と誤読される
  （[[feedback_rakuten_webfetch_soldout]]）。だからこのツールは**生HTMLを自分でパースする**。
"""
import argparse
import datetime
import gzip
import html
import json
import os
import re
import sys
import unicodedata
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')

TODAY = datetime.date.today()
HDR = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Accept-Language': 'ja'}
SITEMAP = 'https://ticket.rakuten.co.jp/sitemap.xml'

# URLパス(楽天カテゴリ) → OSHINAVIジャンルの下書き。パンくずより確実（/music/fes/rtxxxx/ 等）。
PATH_GENRE = [
    ('/music/jpop/idle/', 'idol'), ('/music/jpop/jrock/', 'rock'), ('/music/jpop/', 'jpop'),
    ('/music/fes/', 'fes'), ('/music/classic/', 'classic'), ('/music/jazz/', 'jazz'),
    ('/music/anime/', 'anime'), ('/music/kpop/', 'kpop'), ('/music/enka/', 'enka'),
    ('/music/western/', 'yougaku'), ('/music/', 'jpop'),
    ('/stage/comedy/', 'owarai'), ('/stage/musical/', 'musical'), ('/stage/classic-art/', 'dento'),
    ('/stage/performance/', 'engeki'), ('/stage/', 'engeki'),
    ('/event/matsuri/', 'hanabi'), ('/event/museum/', 'art'), ('/event/exhibition/', 'art'),
    ('/event/circus/', 'kids'), ('/event/themepark/', 'kids'), ('/event/show/', 'engeki'),
    ('/sports/', 'sports'),
]

# パンくず(楽天カテゴリ) → OSHINAVIジャンルの下書き。ぴあのPIA_GENRE_MAPと同じ役割。
GENRE_MAP = {
    'アイドル': 'idol', 'Jポップ・ロック': 'jpop', 'ジャズ': 'jazz', 'クラシック': 'classic',
    '音楽フェスティバル': 'fes', 'アニメ・ゲーム': 'anime', '演歌・歌謡曲': 'enka',
    '洋楽': 'yougaku', 'ヒップホップ': 'hiphop', 'K-POP': 'kpop',
    'ミュージカル': 'musical', 'お笑い・演芸': 'owarai', '演劇': 'engeki', '演劇（その他）': 'engeki',
    '古典芸能': 'dento', '歌舞伎': 'dento', 'バレエ・ダンス': 'classic',
    'スポーツ': 'sports', '美術館・博物館': 'art', '展覧会': 'art',
    '祭り・花火': 'hanabi', 'サーカス': 'kids', 'ショー': 'engeki',
}


def fetch(u, timeout=40):
    req = urllib.request.Request(u, headers=HDR)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
        if 'gzip' in r.headers.get('Content-Encoding', ''):
            raw = gzip.decompress(raw)
        return raw.decode('utf-8', 'replace')


def strip_tags(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s or ''))).strip()


def norm_name(s):
    """重複判定用の正規化キー（全角/半角・記号・空白を潰す）。

    🚨 楽天は「さだまさし［大阪・兵庫・京都］」のように**会場/エリアの角括弧を名前に付ける**。
    既存DBは「さだまさし」なので、括弧を落とさないと同じ公演を新規と誤判定する（二重登録）。
    """
    s = unicodedata.normalize('NFKC', s or '')
    s = re.sub(r'[\[［【(（][^\]］】)）]{0,20}[\]］】)）]\s*$', '', s.strip())
    s = s.lower()
    return re.sub(r"[\s　\-‐―ー–—~〜･・、。,.!！?？'\"「」『』()（）\[\]【】/／:：;；]", '', s)


def iso(y, m, d):
    return '%04d-%02d-%02d' % (int(y), int(m), int(d))


CARD = re.compile(
    r"<div class='performance(?P<state>[^']*)' data-date='(?P<dd>\{[^']*\})'>(?P<body>.*?)</div>\s*</div>",
    re.S)
COL = re.compile(r"<div class='column-(?P<n>\d)'[^>]*>(?P<v>.*?)</div>", re.S)


def parse_perfs(body):
    """公演カード(<div class='performance active' data-date='{...}'>)を列単位で読む。

    列は固定＝ column-1 券種/公演名 / column-6 公演日 / column-2 公演時間 / column-3 エリア / column-4 会場。
    data-date に **その公演の販売期間** が ISO で入っている（min_start_on / max_end_on）＝締切が機械で取れる。
    class に 'active' が無いカードは販売終了（画面でも隠れている）。

    🚨 平文を正規表現で舐める方式は会場名に後続のJS（var specifedDate…）を巻き込んだ（2026-07-25）。
       列で取れば混入しない。
    """
    out = []
    for m in CARD.finditer(body):
        cols = {int(c.group('n')): strip_tags(c.group('v')) for c in COL.finditer(m.group('body'))}
        d = cols.get(6, '')
        dm = re.search(r'(20\d{2})年\s*(\d{1,2})月\s*(\d{1,2})日', d)
        if not dm:
            continue
        d2 = re.search(r'〜\s*(?:(20\d{2})年\s*)?(\d{1,2})月\s*(\d{1,2})日', d)
        try:
            dd = json.loads(m.group('dd'))
        except Exception:
            dd = {}
        open_t = re.search(r'開演\s*(\d{1,2}:\d{2})', cols.get(2, ''))
        out.append({
            'date': iso(*dm.groups()),
            'end': iso(d2.group(1) or dm.group(1), d2.group(2), d2.group(3)) if d2 else '',
            'time': open_t.group(1) if open_t else '',
            'pref': cols.get(3, ''),
            'venue': cols.get(4, ''),
            'ticket_name': cols.get(1, ''),
            'sale_start': (dd.get('min_start_on') or '').replace('T', ' ')[:16],
            'sale_end': (dd.get('max_end_on') or '').replace('T', ' ')[:16],
            'status': '受付中' if 'active' in (m.group('state') or '') else '販売終了',
        })
    # 同じ公演が PC/モバイルで2回出るので重複除去
    uniq, seen = [], set()
    for p in out:
        k = (p['date'], p['end'], p['time'], p['venue'], p['ticket_name'])
        if k in seen:
            continue
        seen.add(k)
        uniq.append(p)
    if not uniq or not any(p['venue'] for p in uniq):
        # カードが無い/会場列が空のページは平文側で拾い直す（会場空のまま載せない）
        alt = parse_perfs_text(body)
        if alt and any(p['venue'] for p in alt):
            # 平文側は販売期間を持たないので、カード側の期間を引き継ぐ
            if uniq:
                for a in alt:
                    for c in uniq:
                        if c['date'] == a['date']:
                            a['sale_start'], a['sale_end'] = c['sale_start'], c['sale_end']
                            break
            return alt
    return uniq


def parse_perfs_text(body):
    """フォールバック＝平文から拾う（カード構造が違うページ用）。

    「2026年 07月 19日 (日) 公演時間 : … エリア : 東京都 会場 : 白金高輪 SELENE b2 販売終了」
    会場は後続のJSを巻き込みやすいので **長さで打ち切り＋ゴミ語で切る**。
    """
    seg = body
    i = seg.find('performances-body')
    if i >= 0:
        seg = seg[i:i + 60000]
    txt = strip_tags(seg)
    out = []
    pat = re.compile(
        r'(?P<y>20\d{2})年\s*(?P<m>\d{1,2})月\s*(?P<d>\d{1,2})日\s*\([^)]*\)'
        r'(?:\s*〜\s*(?:(?P<y2>20\d{2})年\s*)?(?P<m2>\d{1,2})月\s*(?P<d2>\d{1,2})日\s*\([^)]*\))?'
        r'\s*公演時間\s*[:：]\s*(?P<time>.{0,60}?)\s*'
        r'エリア\s*[:：]\s*(?P<pref>\S{2,6}?)\s*会場\s*[:：]\s*(?P<venue>.{1,60}?)\s*'
        r'(?P<status>販売終了|受付終了|完売|予定枚数終了|販売前|受付中|購入する|申込)')
    for m in pat.finditer(txt):
        venue = re.split(r'\s*(?:var |jQuery|\(function|/\*|＜|<)', m.group('venue'))[0].strip()
        open_t = re.search(r'開演\s*(\d{1,2}:\d{2})', m.group('time') or '')
        out.append({
            'date': iso(m.group('y'), m.group('m'), m.group('d')),
            'end': iso(m.group('y2') or m.group('y'), m.group('m2'), m.group('d2')) if m.group('m2') else '',
            'time': open_t.group(1) if open_t else '',
            'pref': m.group('pref'), 'venue': venue, 'ticket_name': '',
            'sale_start': '', 'sale_end': '',
            'status': m.group('status'),
        })
    uniq, seen = [], set()
    for p in out:
        k = (p['date'], p['end'], p['time'], p['venue'])
        if k in seen:
            continue
        seen.add(k)
        uniq.append(p)
    return uniq


def parse_windows(body):
    """販売枠。salesDisplayStatus(JSON)優先・無ければ本文の「販売期間:」行。"""
    wins = []
    m = re.search(r'var salesDisplayStatus = (\{.*?\});', body, re.S)
    if m:
        try:
            js = json.loads(m.group(1))
        except Exception:
            js = {}
        for k, v in js.items():
            grp = (v.get('sales_group') or '').replace('販売期間:', '').strip()
            wins.append({
                'type': grp,
                'timming': (v.get('timming') or '').strip(),
                'status': str(v.get('sales_status')),
                'start': (v.get('sales_start_date') or '')[:16],
            })
    if not wins:
        txt = strip_tags(body)
        for mm in re.finditer(r'販売期間\s*[:：]\s*(?P<type>[^0-9]{0,20}?)\s*'
                              r'(?P<from>20\d{2}/\d{2}/\d{2}\s*\([^)]*\)\s*\d{1,2}:\d{2})\s*〜\s*'
                              r'(?P<to>20\d{2}/\d{2}/\d{2}\s*\([^)]*\)\s*\d{1,2}:\d{2})?', txt):
            wins.append({
                'type': (mm.group('type') or '一般発売').strip() or '一般発売',
                'timming': '%s 〜 %s' % (mm.group('from'), mm.group('to') or ''),
                'status': '', 'start': '',
            })
    # 重複除去
    uniq, seen = [], set()
    for w in wins:
        k = (w['type'], w['timming'])
        if k in seen:
            continue
        seen.add(k)
        uniq.append(w)
    return uniq


def win_dates(timming):
    """'2026/07/25(土) 10:00 〜 2026/08/01 (土) 23:59' → (開始iso時刻, 終了iso時刻 or None)

    🚨 楽天は**終了側だけ日付と曜日カッコの間にスペースを入れる**（「2026/06/23 (火) 23:59」）。
    旧regexは `(\\d{2})\\(` でスペースを許さず終了日を取りこぼし、reconcile_rakuten の
    page_end に締切が入らないまま「締切がページに無い」と誤検知していた。
    同じ穴が build_rakuten_entries.win_end_iso にもあり、そちらは**嘘の締切を作っていた**
    （2026-07-30 発見・[[reference_rakuten_harvest]]）。両方で `\\s*` を許す。
    """
    ds = re.findall(r'(20\d{2})/(\d{2})/(\d{2})\s*\([^)]*\)\s*(\d{1,2}:\d{2})', timming or '')
    if not ds:
        return None, None
    f = '%s-%s-%s %s' % (ds[0][0], ds[0][1], ds[0][2], ds[0][3])
    t = None
    if len(ds) > 1:
        t = '%s-%s-%s %s' % (ds[1][0], ds[1][1], ds[1][2], ds[1][3])
    return f, t


def parse_page(url, body):
    og = re.search(r'<meta[^>]+property="og:title"[^>]+content="([^"]+)"', body)
    name = html.unescape(og.group(1)) if og else ''
    if not name:
        # og:title が無いページがある（THE ORCHESTRA TOKYO / FUJI ROCK 等）→ <title> で拾う
        t = re.search(r'<title[^>]*>(.*?)</title>', body, re.S)
        name = strip_tags(t.group(1)) if t else ''
        name = re.split(r'[–—-]\s*チケット情報', name)[0]
    name = re.sub(r'\s*[｜|]\s*楽天チケット\s*$', '', name).strip()
    name = re.sub(r'\s*[｜|]\s*$', '', name).strip()

    crumb = re.search(r'Top\s*»(.*?)»\s*' + re.escape(name[:12]), strip_tags(body))
    cats = [c.strip() for c in crumb.group(1).split('»')] if crumb else []
    genre = ''
    for c in reversed(cats):
        if c in GENRE_MAP:
            genre = GENRE_MAP[c]
            break
    if not genre:
        # パンくずが拾えないページが多い→URLのカテゴリパスで決める（こちらが本命）
        for pat, g in PATH_GENRE:
            if pat in url:
                genre = g
                break

    perfs = parse_perfs(body)
    wins = parse_windows(body)
    return {'url': url, 'name': name, 'cats': cats, '_genre': genre,
            'perfs': perfs, 'windows': wins}


def alive(rec, min_days=2):
    """買える枠があるか＝(a)公演が未来 かつ (b)受付中 or 発売前の販売枠がある。

    min_days: 公演までの最低日数。今日/明日の公演は載せてもすぐ期限切れ＝価値が薄いので拾わない
              （[[feedback_harvest_source_order_and_far_deadline]] 締切/公演が遠いものを優先）。
    """
    limit = (TODAY + datetime.timedelta(days=min_days)).isoformat()
    future = [p for p in rec['perfs'] if (p.get('end') or p['date']) >= limit]
    if not future:
        return False, '公演が過去 or 直近すぎ'
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    # ① カードが active（画面で買える表示）＋販売終了が未来
    for p in future:
        if p.get('status') == '受付中' and (not p.get('sale_end') or p['sale_end'] >= now):
            return True, ''
    # ② 販売枠(salesDisplayStatus)に締切未到来のものがある
    for w in rec['windows']:
        f, t = win_dates(w['timming'])
        if not f:
            continue
        if t and t < now:
            continue                      # 締切済み
        return True, ''
    return False, '買える販売枠なし'


def deeplink(u):
    import urllib.parse
    return ('https://click.linksynergy.com/deeplink?id=z9x6HLNpWco&mid=53531&murl='
            + urllib.parse.quote(u, safe=''))


def collect_urls(days):
    idx = fetch(SITEMAP)
    maps = re.findall(r'<loc>([^<]+)</loc>', idx)
    limit = (TODAY - datetime.timedelta(days=days)).isoformat()
    urls = []
    for mu in maps:
        if 'post-sitemap' not in mu and 'static_event' not in mu:
            continue
        try:
            body = fetch(mu)
        except Exception as ex:
            sys.stderr.write('sitemap取得失敗 %s %s\n' % (mu, ex))
            continue
        for loc, mod in re.findall(r'<loc>(https://ticket\.rakuten\.co\.jp/[^<]+)</loc>\s*<lastmod>([^<]+)</lastmod>', body):
            if not re.search(r'/rt[a-z0-9]{5,}/?$', loc):
                continue
            if mod[:10] >= limit:
                urls.append((loc, mod[:10]))
    urls.sort(key=lambda x: x[1], reverse=True)
    return urls


def _selftest():
    body = ('<meta property="og:title" content="テスト公演｜楽天チケット" />'
            'Top » 音楽 » Jポップ・ロック » アイドル » テスト公演'
            "<div class='performance active' data-date='{\"min_start_on\":\"2026-07-25T10:00:00\","
            "\"max_end_on\":\"2026-09-18T23:59:59\"}'>"
            "<div class='column-1'>テスト公演</div>"
            "<div class='column-6'>2026年 09月 19日 (日)</div>"
            "<div class='column-2'>開場 13:30 / 開演 14:00</div>"
            "<div class='column-3'>東京都</div>"
            "<div class='column-4'>白金高輪 SELENE b2</div>"
            "<div class='column-5 performance_btn perf_1'>x</div></div>"
            'var salesDisplayStatus = {"1":{"sales_group":"\\u8ca9\\u58f2\\u671f\\u9593: \\u4e00\\u822c\\u767a\\u58f2",'
            '"timming":"2026/07/25(\\u571f) 10:00 \\u301c 2026/09/18(\\u91d1) 23:59","sales_status":"1",'
            '"sales_start_date":"2026-07-25 10:00:00"}};')
    r = parse_page('https://ticket.rakuten.co.jp/music/jpop/idle/rtxxxxx/', body)
    assert r['name'] == 'テスト公演', r['name']
    assert r['_genre'] == 'idol', r['cats']
    assert len(r['perfs']) == 1 and r['perfs'][0]['date'] == '2026-09-19', r['perfs']
    # 期間公演（4/28〜7/5形）＝千秋楽をendに入れる／og:title無しは<title>で拾う
    body2 = ('<title>展覧会テスト｜楽天チケット</title>'
             "<div class='performance active' data-date='{\"min_start_on\":\"2026-06-23T10:00:00\","
             "\"max_end_on\":\"2026-09-22T23:59:59\"}'>"
             "<div class='column-1'>展覧会テスト【前売】</div>"
             "<div class='column-6'>2026年 09月 28日 (月) 〜 11月 05日 (木)</div>"
             "<div class='column-2'>-</div><div class='column-3'>東京都</div>"
             "<div class='column-4'>東京都美術館</div>"
             "<div class='column-5 performance_btn perf_1'>x</div></div>")
    r2 = parse_page('https://ticket.rakuten.co.jp/event/museum/rtyyyyy/', body2)
    assert r2['name'] == '展覧会テスト', r2['name']
    assert len(r2['perfs']) == 1, r2['perfs']
    assert r2['perfs'][0]['date'] == '2026-09-28' and r2['perfs'][0]['end'] == '2026-11-05', r2['perfs']
    assert r2['perfs'][0]['venue'] == '東京都美術館', r2['perfs']
    assert r2['perfs'][0]['sale_end'] == '2026-09-22 23:59', r2['perfs']
    assert r['perfs'][0]['pref'] == '東京都', r['perfs']
    assert r['perfs'][0]['venue'] == '白金高輪 SELENE b2', r['perfs']   # 会場にJS等が混入しない
    assert r['perfs'][0]['sale_start'] == '2026-07-25 10:00', r['perfs']
    assert r['perfs'][0]['sale_end'] == '2026-09-18 23:59', r['perfs']  # 締切がカードから取れる
    assert r['perfs'][0]['time'] == '14:00', r['perfs']
    assert len(r['windows']) == 1 and r['windows'][0]['type'] == '一般発売', r['windows']
    assert win_dates(r['windows'][0]['timming']) == ('2026-07-25 10:00', '2026-09-18 23:59')
    # 🚨終了側に**スペースが入る**のが楽天の実形式。ここを取りこぼすと
    # reconcile が「締切がページに無い」と誤検知し、builderは嘘の締切を作る（2026-07-30の回帰ケース）
    assert win_dates('2026/06/20(土) 10:00 〜 2026/06/23 (火) 23:59') == ('2026-06-20 10:00', '2026-06-23 23:59')
    assert win_dates('2026/06/20(土) 10:00 〜 2026/06/23(火) 23:59') == ('2026-06-20 10:00', '2026-06-23 23:59')
    assert win_dates('2026/07/25(土) 10:00 〜 ') == ('2026-07-25 10:00', None)
    assert deeplink('https://ticket.rakuten.co.jp/a/').startswith('https://click.linksynergy.com/deeplink?id=z9x6HLNpWco&mid=53531&murl=https%3A%2F%2F')
    print('selftest OK: og:title/パンくずジャンル/公演カード/販売枠JSON/deeplink 回帰なし')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--days', type=int, default=60, help='sitemapのlastmodが何日以内のページを見るか')
    ap.add_argument('--limit', type=int, default=0, help='取得ページ数の上限(0=全部)')
    ap.add_argument('--out', default='tmp/rakuten_cand.json')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args()
    if args.selftest:
        _selftest()
        return 0

    src = open('index.html', encoding='utf-8').read()
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
    EV = json.loads(m.group(2))
    have_key = {norm_name(e.get('name')) for e in EV} | {norm_name(e.get('artist')) for e in EV}

    urls = collect_urls(args.days)
    print('sitemapの候補URL(直近%d日更新): %d件' % (args.days, len(urls)))
    if args.limit:
        urls = urls[:args.limit]

    out, skipped = [], {'既存': 0, '死': 0, '解析不能': 0, '取得失敗': 0}
    for i, (u, mod) in enumerate(urls, 1):
        try:
            body = fetch(u)
        except Exception as ex:
            skipped['取得失敗'] += 1
            sys.stderr.write('  [%d/%d] 取得失敗 %s %s\n' % (i, len(urls), u, ex))
            continue
        rec = parse_page(u, body)
        rec['lastmod'] = mod
        if not rec['name'] or not rec['perfs']:
            skipped['解析不能'] += 1
            sys.stderr.write('  [%d/%d] 解析不能 %s\n' % (i, len(urls), u))
            continue
        if norm_name(rec['name']) in have_key:
            skipped['既存'] += 1
            continue
        ok, why = alive(rec)
        if not ok:
            skipped['死'] += 1
            continue
        rec['rakuten_deeplink'] = deeplink(u)
        out.append(rec)
        sys.stderr.write('  [%d/%d] NEW %s (%d公演/%d枠)\n' % (i, len(urls), rec['name'][:34], len(rec['perfs']), len(rec['windows'])))

    os.makedirs('tmp', exist_ok=True)
    json.dump(out, open(args.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('\n=== 新着候補 %d件 → %s ===' % (len(out), args.out))
    print('   除外: %s' % skipped)
    return 0


if __name__ == '__main__':
    sys.exit(main())
