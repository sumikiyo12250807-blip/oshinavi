# -*- coding: utf-8 -*-
"""ぴあ発売前ハーベスタ: rlsInfo.do から発売前(30日以内発売)を全件取得しパース。
使い方: python tools/presale_harvest.py <lg> [out.json]
  lg: 01音楽 02演劇 03スポーツ 04映画 05アート 06イベント 07クラシック
既存 index.html と名前照合し、未掲載候補のみ抽出して出力。"""
import re, io, sys, json, time, html, urllib.request, unicodedata, http.client

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
LG = sys.argv[1] if len(sys.argv) > 1 else '01'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'tmp/presale_%s.json' % LG
# 第3引数=フィルタ式(key=value)。既定は発売前の rlsIn=03。
#   発売前: rlsIn=03(30日以内) / rlsIn=04(それ以外)
#   買える今: rlsStatus=0101(発売中・先着3792件) / rlsStatus=0201(受付中・抽選712件)
#   ※rlsStatus指定だと受付終了は自動除外され「今買える」だけ返る(2026-06-26発見)。
FILTER = sys.argv[3] if len(sys.argv) > 3 else 'rlsIn=03'
if '=' not in FILTER:           # 後方互換: '03' だけ渡されたら rlsIn=03 とみなす
    FILTER = 'rlsIn=' + FILTER

_conn = None

def fetch(page):
    """t.pia.jp への接続を keep-alive で使い回す。1ページ毎に TCP+TLS を張り直すと
    1ページ約5秒かかり、音楽(57ページ)で接続確立に大半の時間を費やしていた(2026-07-10計測)。
    失敗したら接続を捨てて urllib にフォールバック。"""
    global _conn
    path = '/pia/rlsInfo.do?lg=%s&%s&page=%d' % (LG, FILTER, page)
    for attempt in (1, 2):
        try:
            if _conn is None:
                _conn = http.client.HTTPSConnection('t.pia.jp', timeout=30)
            _conn.request('GET', path, headers={
                'User-Agent': 'Mozilla/5.0', 'Connection': 'keep-alive',
                'Accept-Encoding': 'identity'})
            r = _conn.getresponse()
            body = r.read()
            if r.status != 200:
                raise OSError('status %d' % r.status)
            return body.decode('utf-8', 'replace')
        except Exception:
            try:
                _conn.close()
            except Exception:
                pass
            _conn = None
            if attempt == 2:
                url = 'https://t.pia.jp' + path
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                return urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')

def strip(s):
    return html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s))).strip()

def parse_page(h):
    out = []
    # split into per-event chunks at each title_list li
    chunks = re.split(r'(?=<li class="listWrp_title_list clearfix">)', h)
    for body in chunks:
        am = re.search(r'<a href="([^"]*event\.do\?event(?:Bundle)?Cd=\w+)"[^>]*>(.*?)</a>', body, re.S)
        if not am:
            continue
        url = am.group(1).replace('http://', 'https://')
        artist = strip(am.group(2))
        def span(cls):
            m = re.search(r'<span class="%s">(.*?)</span>\s*(?=<span class="list_|<span class="add_alert|</li>)' % cls, body, re.S)
            return strip(m.group(1)) if m else ''
        saletype = ''
        st = re.search(r'status_icon_text[^>]*>(.*?)</span>', body, re.S)
        if st:
            saletype = strip(st.group(1))
        rlsdate = ''
        rm = re.search(r'発売前\s*(\d{4}/\d{1,2}/\d{1,2})', body)
        if rm:
            rlsdate = rm.group(1)
        elif '本日発売初日' in body:
            rlsdate = 'TODAY'
        perfdate = span('list_03')
        venue = span('list_04')
        pref = ''
        pm = re.findall(r'\(([^()]*?[都道府県])\)', venue)
        if pm:
            pref = '／'.join(dict.fromkeys(pm))
        out.append({
            'url': url, 'artist': artist, 'saletype': saletype,
            'rlsdate': rlsdate, 'perfdate': perfdate, 'venue': venue, 'pref': pref,
        })
    return out

# total count
h1 = fetch(1)
mt = re.search(r'全([0-9,]+)件中', h1)
total = int(mt.group(1).replace(',', '')) if mt else 0
pages = (total + 9) // 10
print('lg=%s total=%d pages=%d' % (LG, total, pages))

# ★1ページの件数は固定でない(5〜10件・末尾は1件等)。total÷10で打ち切ると後半ページを
#   丸ごと取りこぼす(2026-06-26発覚＝音楽で71ページ以降の約175件を未取得だった)。
# ★★ぴあは範囲外のページを要求されても「最後のページ」を返す(空を返さない)。そのため
#   「空ページ2回で終了」の条件に永久に当たらず毎回400ページ空回りしていた(2026-07-10発覚)。
#   art05では同じ1件を399回も拾い、在庫件数まで水増しされていた。
#   → 新規URLが1件も増えないページに当たったら終端とみなす。
#   ※フェッチにはゆらぎがあり、実在ページが一度だけ空/前ページと同一で返ることがある
#     (2026-07-10 art05で1回目9件・2回目15件)。1回リトライし、新規ゼロが2回続いたら終端。
items, seen = [], set()
p, empty = 1, 0
h = h1
while p <= 400:
    try:
        pi = parse_page(h)
    except Exception as e:
        print('page', p, 'err', e); pi = []
    fresh = [x for x in pi if x['url'] not in seen]
    if not fresh:
        time.sleep(1.0)                      # ゆらぎ対策の1回リトライ
        try:
            pi = parse_page(fetch(p))
        except Exception:
            pi = []
        fresh = [x for x in pi if x['url'] not in seen]
    if fresh:
        for x in fresh:
            seen.add(x['url'])
        items += fresh
        empty = 0
    else:
        empty += 1
        if empty >= 2:      # 新規ゼロが2ページ連続 = 終端(折り返し)
            break
    p += 1
    time.sleep(0.15)
    try:
        h = fetch(p)
    except Exception as e:
        print('page', p, 'fetch err', e); break
print('parsed items:', len(items), '(fetched up to page %d)' % p)

# dedup vs existing index.html (artist + name text)
idx = open('index.html', encoding='utf-8').read()
existing = idx.lower()
def norm(s):
    # NFKC で全角→半角を正規化（ＫＥＮＮＹ Ｇ→KENNY G 等）。これが無いと
    # ぴあの全角名が既存DBの半角名とマッチせず重複を取りこぼす（2026-06-16に16件混入）
    s = unicodedata.normalize('NFKC', s)
    return re.sub(r'[\s　・／/＜＞<>「」『』（）()【】’\'"!！\-—]', '', s).lower()
# build set of existing artist/name tokens
ex_names = set()
for m in re.finditer(r'"(?:artist|name)"\s*:\s*"([^"]+)"', idx):
    ex_names.add(norm(m.group(1)))

new = []
for it in items:
    key = norm(it['artist'])
    hit = key and (key in ex_names or any(key in en or en in key for en in ex_names if len(en) > 3 and len(key) > 3))
    it['in_db'] = bool(hit)
    if not hit:
        new.append(it)

print('already in DB:', len(items) - len(new), '| NOT in DB (new candidates):', len(new))
json.dump({'lg': LG, 'total': total, 'parsed': len(items), 'new': new},
          open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('written', OUT)
# print first 25 new
for it in new[:25]:
    print(' NEW |', it['rlsdate'], '|', it['artist'][:24], '|', it['perfdate'][:22], '|', it['pref'])
