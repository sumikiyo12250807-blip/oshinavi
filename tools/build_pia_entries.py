# -*- coding: utf-8 -*-
"""ぴあ候補リストから OSHINAVI エントリ(T-SQUARE形)を【決定論的に】構築する。
WebFetch要約に一切頼らず、HTMLを機械パースして全券種・全公演期間・時刻を拾う。
（取りこぼし根絶。memory: reference_pia_tickets_tool / feedback_capture_all_deadlines_on_add）

入力: 候補JSON = [{"newid":int, "artist":str, "urls":[url,...]}, ...]
  例: python tools/build_pia_entries.py tmp/candidates.json > tmp/entries.json
出力: genre:"new"・verified:true・_genre(下書き) 付きのエントリ配列(JSON)。
  そのまま inject すれば新着投入できる。投入前に必ず tools/check_badges.py を回す。

取り込む券種: 受付中(販売期間中/受付中) と 発売前 のみ。受付終了/予定枚数終了/結果発表前は除外。
公演日: datetimeペア(初日,千秋楽)を範囲で取得。複数日は「M/D〜M/D公演」。
"""
import json, re, sys, io, time, urllib.request, html as _html, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

WD = '月火水木金土日'
PREFS = '北海道青森岩手宮城秋田山形福島茨城栃木群馬埼玉千葉東京神奈川新潟富山石川福井山梨長野岐阜静岡愛知三重滋賀京都大阪兵庫奈良和歌山鳥取島根岡山広島山口徳島香川愛媛高知福岡佐賀長崎熊本大分宮崎鹿児島沖縄'
PREF_RE = re.compile('(' + '|'.join(['北海道','神奈川','和歌山','鹿児島'] + [p for p in ['青森','岩手','宮城','秋田','山形','福島','茨城','栃木','群馬','埼玉','千葉','東京','新潟','富山','石川','福井','山梨','長野','岐阜','静岡','愛知','三重','滋賀','京都','大阪','兵庫','奈良','鳥取','島根','岡山','広島','山口','徳島','香川','愛媛','高知','福岡','佐賀','長崎','熊本','大分','宮崎','沖縄']]) + ')(?:都|道|府|県)?')
def extract_prefs(*texts):
    seen, out = set(), []
    for t in texts:
        for m in PREF_RE.findall(t or ''):
            if m not in seen:
                seen.add(m); out.append(m)
    return out
def fetch(u):
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')
def txt(s): return _html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s or ''))).strip()
def wd(iso):
    y, m, d = map(int, iso.split('-')); return WD[datetime.date(y, m, d).weekday()]
def jp(iso):
    y, m, d = map(int, iso.split('-')); return f"{y}年{m}月{d}日({wd(iso)})"
def prefshort(p): return p if p == '北海道' else re.sub(r'(都|道|府|県)$', '', p)
def md(iso): _, m, d = iso.split('-'); return f"{int(m)}/{int(d)}"
def ecd_url(u):
    mm = re.search(r'eventCd=(\w+)', u or ''); return 'https://t.pia.jp/pia/event/event.do?eventCd=' + mm.group(1) if mm else None

def parse_cards(h):
    rows = []
    for it in re.split(r'(?=<li class="ticketSalesList-2024__item)', h):
        if 'ticketSalesCard-2024__status' not in it: continue
        g = lambda p: (re.search(p, it, re.S).group(1) if re.search(p, it, re.S) else '')
        dts = re.findall(r'datetime="(\d{4}-\d{2}-\d{2})', it)
        stat = re.search(r'__status (is-[\w-]+)">(.*?)(?:<br|</p>)', it, re.S)
        cls = stat.group(1) if stat else ''
        stt = txt(stat.group(2)) if stat else ''
        # ステータスは【HTMLクラス】基準で判定（文言ゆれに強い）。
        # is-active=受付中 / is-before=発売前(「まもなく抽選受付」等の先行も拾う) / それ以外=対象外。
        # ただし売切・終了・結果発表は文言でも明示除外（クラスがactive/beforeでも保険）。
        # ※2026-06-20: 「まもなく抽選受付」(is-before)を受付終了と誤判定しプレリザーブ3枠ドロップした反省。
        if re.search(r'(予定枚数|完売|売り?切|受付は?終了|販売終了|終了しました|結果発表)', stt):
            state = '受付終了'
        elif cls == 'is-active' or re.search(r'(販売期間中|受付中)', stt):
            state = '受付中'
        elif cls == 'is-before' or '発売前' in stt or 'まもなく' in stt:
            state = '発売前'
        else:
            state = '受付終了'
        place = txt(g(r'__place"[^>]*>(.*?)</span>'))
        region = txt(g(r'__region">(.*?)</span>'))
        prefs = extract_prefs(region, place)   # 複数県は __place に「県／県／…」で入る
        # place が県名の羅列だけ(実会場名でない)なら venue 扱いしない
        is_preflist = place and not PREF_RE.sub('', place).replace('／', '').replace('・', '').replace('　', '').strip()
        rows.append({
            'perfdate': dts[0] if dts else '', 'perf_end': dts[-1] if dts else '',
            'venue': '' if is_preflist else place, 'prefs': prefs,
            'title': txt(g(r'__title">(.*?)</p>')), 'state': state,
            'when': txt(g(r'__status[^>]*>.*?<br>\s*<span[^>]*>(.*?)</span>')),
            'url': g(r'href="(https://t\.pia\.jp/pia/ticketInformation\.do\?[^"]+)"'),
        })
    seen, u = set(), []
    for r in rows:
        k = (r['perfdate'], r['perf_end'], r['venue'], r['title'], r['state'], r['when'])
        if k in seen: continue
        seen.add(k); u.append(r)
    return u

def kenshu(title):
    t = re.sub(r'＜.*?＞', '', title)  # ＜...＞内に／がある場合があるので先に除去
    if '／' in t:
        return t.split('／')[0].strip('　 ').strip() or '一般発売'
    m = re.search(r'(プレイガイド最速先行|最速先行|オフィシャル先行|\d次プレリザーブ|プレリザーブ\d次|プレリザーブ|\d次受付|プリセール|一般発売|当日引換券|当日券|先行)', t)
    return m.group(1) if m else '先行'

def parse_when(state, when):
    if state == '発売前':
        m = re.search(r'(\d{4})/(\d{1,2})/(\d{1,2})\([^)]*\)\s*(?:昼|夜|朝|午前|午後)?(\d{1,2}:\d{2})?\s*より発売', when)
        if m:
            iso = f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"; t = m.group(4)
            return (f"{int(m.group(2))}/{int(m.group(3))} {t}発売" if t else f"{int(m.group(2))}/{int(m.group(3))}発売"), iso, iso
        # プレリザーブ/抽選受付など「START(日 時) ～ END」レンジ形 → STARTを受付開始(発売)日に
        # 例: "2026/6/20(土) 11:00 ～ 2026/6/28(日) 23:59"
        m2 = re.search(r'(\d{4})/(\d{1,2})/(\d{1,2})\([^)]*\)\s*(\d{1,2}:\d{2})?\s*～', when)
        if m2:
            iso = f"{m2.group(1)}-{int(m2.group(2)):02d}-{int(m2.group(3)):02d}"; t = m2.group(4)
            return (f"{int(m2.group(2))}/{int(m2.group(3))} {t}発売" if t else f"{int(m2.group(2))}/{int(m2.group(3))}発売"), iso, iso
    else:
        m = re.search(r'～\s*(\d{4})/(\d{1,2})/(\d{1,2})\([^)]*\)\s*(?:昼|夜|朝|午前|午後)?(\d{1,2}:\d{2})?', when)
        if m:
            iso = f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"; t = m.group(4)
            return (f"〜{int(m.group(2))}/{int(m.group(3))} {t}" if t else f"〜{int(m.group(2))}/{int(m.group(3))}"), iso, None
    return None, None, None

def genre_of(n):
    """名前ベースのジャンル推測（bundleページ等でぴあカテゴリが取れない時のフォールバック）。"""
    if re.search(r'落語|寄席|独演会|二人会|お笑い|漫才|ものまね|コント|新喜劇|喜劇|講談|演芸', n): return 'owarai'
    if re.search(r'狂言|能楽|文楽|歌舞伎|雅楽|邦楽', n): return 'dento'
    if re.search(r'バレエ|オペラ|クラシック|交響|管弦|フィル', n): return 'classic'
    if re.search(r'ミュージカル', n): return 'musical'
    return 'engeki'

# ぴあ個別公演ページの <title> 末尾 [カテゴリ サブカテゴリ] → OSHINAVIジャンル(主, 追加)
# 2026-06-20 演劇50件で実証・ユーザー確定。memory: project_vendor_genre_autoassign
PIA_GENRE_MAP = {
    # 演劇カテゴリ
    '寄席・お笑い': ('owarai', None),
    '歌舞伎・古典芸能': ('dento', None),
    'バレエ・ダンス': ('classic', 'engeki'),   # バレエ=classic+engeki両方方式
    '人形劇・キャラクター': ('kids', None),
    'ミュージカル・ショー': ('musical', None),
    '朗読・リーディング': ('engeki', None),
    '演劇': ('engeki', None),
    '演劇その他': ('engeki', None),
    # 音楽カテゴリ（粒度はぴあ依存・J-POP・ROCKは粗いので人が最終判断）
    'ジャズ・フュージョン': ('jazz', None),
    '演歌・邦楽': ('enka', None),
    'クラシック': ('classic', None),
    'J-POP・ROCK': ('jpop', None),
    '音楽その他': ('fes', None),
}
# トップカテゴリ単位のフォールバック
PIA_CAT_FALLBACK = {'スポーツ': ('sports', None)}

def pia_subcat(h):
    """HTMLの<title>から (カテゴリ, サブカテゴリ) を抽出。bundleページ等で取れなければ None。"""
    m = re.search(r'<title>([^<]*)</title>', h or '')
    if not m: return None
    title = _html.unescape(m.group(1))
    mc = re.search(r'\[([^\]\s]+)\s+(.+?)のチケット', title)
    return (mc.group(1), mc.group(2)) if mc else None

def genre_from_subcat(cat, sub):
    """ (カテゴリ,サブ) → (主ジャンル, 追加ジャンル or None)。判定不能なら None。"""
    if sub and sub in PIA_GENRE_MAP: return PIA_GENRE_MAP[sub]
    if sub:
        for k, v in PIA_GENRE_MAP.items():
            if k in sub or sub in k: return v
    return PIA_CAT_FALLBACK.get(cat)

def build(cand):
    allrows, htmls = [], []
    for u in cand['urls']:
        try:
            h = fetch(u); htmls.append(h)
            allrows += parse_cards(h); time.sleep(0.25)
        except Exception:
            pass
    buy = [r for r in allrows if r['state'] in ('受付中', '発売前')]
    seen, rows = set(), []
    for r in buy:
        k = (r['perfdate'], r['perf_end'], r['venue'], r['title'], r['state'])
        if k in seen: continue
        seen.add(k); rows.append(r)
    if not rows: return None
    venues = list(dict.fromkeys(r['venue'] for r in rows if r['venue']))
    prefs = list(dict.fromkeys(p for r in rows for p in r['prefs']))
    starts = sorted(r['perfdate'] for r in rows if r['perfdate'])
    ends = sorted((r.get('perf_end') or r['perfdate']) for r in rows if r['perfdate'])
    ecds = set(re.search(r'eventCd=(\w+)', r['url']).group(1) for r in rows if r.get('url') and re.search(r'eventCd=(\w+)', r['url']))
    multi = len(ecds) > 1
    tickets = []
    for r in rows:
        suf, iso, sd = parse_when(r['state'], r['when'])
        if not iso: continue
        pe = r.get('perf_end') or r['perfdate']
        mdr = md(r['perfdate']) if pe == r['perfdate'] else f"{md(r['perfdate'])}〜{md(pe)}"
        _pf = '・'.join(r['prefs']) if r['prefs'] else '全国'   # 複数県は全部載せる(字は小さめ表示)。県名取れなければ全国
        t = {'type': f"{kenshu(r['title'])}（{_pf} {mdr}公演）{suf}", 'date': iso}
        if sd: t['startDate'] = sd
        if multi and ecd_url(r['url']): t['url'] = ecd_url(r['url'])
        tickets.append(t)
    tickets.sort(key=lambda t: t['date'])
    venue = venues[0] if len(venues) == 1 else '全国ツアー（' + '／'.join(venues[:4]) + '）'
    pref = prefs[0] if len(prefs) == 1 else '全国'
    if len(starts) == 1 and ends[-1] == starts[0]:
        dl = f"{jp(starts[0])} {pref} {venues[0] if venues else ''}".strip()
    else:
        tail = '全国ツアー' if pref == '全国' else (pref + ' ' + (venues[0] if len(venues) == 1 else '')).strip()
        dl = f"{jp(starts[0])}〜{jp(ends[-1])} {tail}".strip()
    u0 = cand['urls'][0]
    pia = ('https://t.pia.jp/pia/event/event.do?eventBundleCd=' + re.search(r'eventBundleCd=(\w+)', u0).group(1)) if 'eventBundleCd' in u0 else ecd_url(u0)
    # ジャンル下ごしらえ: ぴあカテゴリ優先 → 取れなければ個別ページを1つ引く → それでも無ければ名前ベース
    pg, sub_used = None, ''
    for h in htmls:
        sc = pia_subcat(h)
        if sc and genre_from_subcat(*sc):
            pg, sub_used = genre_from_subcat(*sc), f"{sc[0]}/{sc[1]}"; break
    if not pg:  # bundleページはサブカテゴリ無し → 個別eventCdページを1つ引いて再試行
        for r in rows:
            eu = ecd_url(r.get('url'))
            if not eu: continue
            try:
                sc = pia_subcat(fetch(eu)); time.sleep(0.2)
            except Exception:
                sc = None
            if sc and genre_from_subcat(*sc):
                pg, sub_used = genre_from_subcat(*sc), f"{sc[0]}/{sc[1]}"; break
    main_genre, extra = pg if pg else (genre_of(cand['artist']), None)
    return {'id': cand['newid'], 'artist': cand['artist'], 'name': cand['artist'], 'date': ends[-1],
            'dateLabel': dl, 'venue': venue, 'prefecture': pref, 'genre': 'new',
            '_genre': main_genre, '_extraGenres': [extra] if extra else [], '_piaSub': sub_used,
            'price': None, 'links': {'rakuten': None, 'lawson': None, 'pia': pia, 'eplus': None},
            'tickets': tickets, 'verified': True, 'verifiedAt': datetime.date.today().isoformat()}

if __name__ == '__main__':
    cands = json.load(open(sys.argv[1], encoding='utf-8'))
    out, skip = [], []
    for c in cands:
        e = build(c)
        (out.append(e) if e else skip.append(c['newid']))
        sys.stderr.write(f"  {c['newid']} {'OK' if e else 'skip(売切)'}\n")
    print(json.dumps(out, ensure_ascii=False, indent=1))
    sys.stderr.write(f"構築 {len(out)} 件 / skip {skip}\n")
