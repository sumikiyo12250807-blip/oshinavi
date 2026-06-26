# -*- coding: utf-8 -*-
"""ぴあ発売前ハーベスタ: rlsInfo.do から発売前(30日以内発売)を全件取得しパース。
使い方: python tools/presale_harvest.py <lg> [out.json]
  lg: 01音楽 02演劇 03スポーツ 04映画 05アート 06イベント 07クラシック
既存 index.html と名前照合し、未掲載候補のみ抽出して出力。"""
import re, io, sys, json, time, html, urllib.request, unicodedata

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

def fetch(page):
    url = 'https://t.pia.jp/pia/rlsInfo.do?lg=%s&%s&page=%d' % (LG, FILTER, page)
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
#   空ページが2回連続するまで回す(safety cap 400ページ)。
items = parse_page(h1)
p, empty = 2, 0
while p <= 400:
    try:
        pi = parse_page(fetch(p))
    except Exception as e:
        print('page', p, 'err', e); pi = []
    if pi:
        items += pi; empty = 0
    else:
        empty += 1
        if empty >= 2:
            break
    p += 1
    time.sleep(0.15)
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
