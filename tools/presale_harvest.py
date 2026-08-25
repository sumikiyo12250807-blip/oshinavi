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
# ★★🚨2026-08-24 修正＝終端判定を「新規URLが増えない」から「前ページと中身が同じ」に変えた。
#   受付中(rlsStatus=0101)の一覧は**同じ公演が券種ごとに何行も並ぶ**ので、
#   10行×2ページが丸ごと既知URLになることが普通に起きる。旧判定だとそこで終端と誤読して
#   打ち切っていた＝音楽0101が448ページ中32ページ(7.1%)で停止していた。
#   発売前(rlsIn=03)は在庫が小さく重複が少ないので表に出なかった。
#   新しい終端＝「そのページのURL並びが前ページと完全に同一」が2回連続（＝ぴあが最後のページを
#   返し続けている状態）。合わせて total から計算した想定ページ数までは必ず回る。
#   memory: feedback_newpool_presale_ratio_gate（頭文字の若いものだけ拾う事故）
# ★★🚨2026-08-25 再修正＝終端判定を「URLの並び」から**件数表記の位置**に変えた。
#   8/24版の「前ページと中身が同じ＝終端」は、**1ページに1本しかリンクが無いページが
#   続く**と誤爆する。原因は大型ツアー＝同じ eventCd の行が何十行も並ぶことで、
#   実測(音楽 rlsIn=03)では 37〜40ページが「同じ1本」だけになり、**62ページ中39ページで
#   打ち切られていた**（取得273/619件）。頭文字の若い側だけ拾う事故と同じ型。
#   ✅ぴあは各ページに「全619件中 391～400件」と**現在位置**を出す。範囲外を要求すると
#     最後のページを返し続ける＝この位置が進まなくなる。**位置が進まない＝終端**が正しい判定。
#   位置表記が取れない時だけ、従来のURL並び比較にフォールバックする。
POS_RE = re.compile(r'全[0-9,]+件中\s*([0-9,]+)\s*[~〜～\-–]\s*([0-9,]+)\s*件')

def page_pos(h):
    m = POS_RE.search(h or '')
    return (int(m.group(1).replace(',', '')), int(m.group(2).replace(',', ''))) if m else None

items, seen = [], set()
p, same = 1, 0
prev_sig = None
prev_pos = None
h = h1
LAST = min(400, max(pages, 1))
while p <= LAST:
    try:
        pi = parse_page(h)
    except Exception as e:
        print('page', p, 'err', e); pi = []
    pos = page_pos(h)
    sig = tuple(x['url'] for x in pi)
    stalled = (pos is not None and pos == prev_pos) if pos is not None else (sig == prev_sig)
    if not pi or stalled:
        time.sleep(1.0)                      # ゆらぎ対策の1回リトライ
        try:
            h = fetch(p); pi = parse_page(h)
        except Exception:
            pi = []
        pos = page_pos(h)
        sig = tuple(x['url'] for x in pi)
        stalled = (pos is not None and pos == prev_pos) if pos is not None else (sig == prev_sig)
    if not pi or stalled:
        same += 1
        if same >= 2:       # 現在位置が進まないページが2回続く = 終端(折り返し)
            break
    else:
        same = 0
    prev_pos = pos
    for x in pi:
        if x['url'] not in seen:
            seen.add(x['url'])
            items.append(x)
    prev_sig = sig
    p += 1
    time.sleep(0.15)
    try:
        h = fetch(p)
    except Exception as e:
        print('page', p, 'fetch err', e); break
print('parsed items:', len(items), '(fetched up to page %d)' % p)

# dedup vs existing index.html
# 🚨2026-08-17 修正: 未掲載判定を「アーティスト名の一致」→「eventCd がDBに在るか」に変更。
#   旧実装は norm(artist) が index.html の artist/name に一部一致しただけで捨てていた。
#   そのため **DBに1エントリでもある人の別公演・別ツアーが永久に拾えない**（発売前・音楽で
#   在庫393件中「未掲載」が13件しか出ず、新着50件が「もう売ってる」で埋まる原因になった）。
#   ユーザー 2026-08-17「新着がもう売ってるのだらけ／これから売るやつを重点的に集めて」。
#   名前一致は捨てずに name_in_db フラグで残す＝投入時に「既存エントリへ統合するか」を判断する材料
#   （[[feedback_harvest_name_dedup_blindspot]] / [[feedback_tour_consolidate]]）。
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

ex_cds = set(re.findall(r'event(?:Bundle)?Cd=(\w+)', idx))

def eventcd(u):
    m = re.search(r'event(?:Bundle)?Cd=(\w+)', u or '')
    return m.group(1) if m else ''

new, n_name_only = [], 0
for it in items:
    key = norm(it['artist'])
    # 印は「完全一致」だけ。旧実装の部分一致(en in key / key in en)は当たりすぎて
    # 393件中380件が消えるほど乱暴だった＝統合検討の目印としても使い物にならない。
    name_hit = bool(key) and key in ex_names
    cd_hit = eventcd(it['url']) in ex_cds
    it['in_db'] = cd_hit                 # ★判定はeventCdのみ
    it['name_in_db'] = name_hit          # 参考＝既存エントリへの統合を検討する印
    if not cd_hit:
        new.append(it)
        if name_hit:
            n_name_only += 1

print('already in DB (eventCd一致):', len(items) - len(new), '| NOT in DB (new candidates):', len(new))
print('  うち %d件は同名の既存エントリあり＝投入時に統合を検討（旧実装はここを丸ごと捨てていた）' % n_name_only)
# ★pages(想定)と fetched_pages(実際に見たページ)を必ず残す。
#   parsed < total は取りこぼしではない（ぴあは1公演=1行なので同じeventCdが複数行に出る＝
#   URL重複を潰すと当然減る）。**打ち切りを検知できる指標はページ数のほう**。
#   2026-08-17に受付中スイープが音楽4318件中204件＝「あ行」だけで打ち切られていたのを
#   件数比で見つけた反省（[[feedback_newpool_presale_ratio_gate]]）。
json.dump({'lg': LG, 'total': total, 'pages': pages, 'fetched_pages': p,
           'parsed': len(items), 'new_name_in_db': n_name_only, 'new': new},
          open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('written', OUT)
# print first 25 new
for it in new[:25]:
    print(' NEW |', it['rlsdate'], '|', it['artist'][:24], '|', it['perfdate'][:22], '|', it['pref'])
