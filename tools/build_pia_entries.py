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
import json, re, sys, io, time, urllib.request, urllib.parse, html as _html, datetime, unicodedata
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ぴあHTMLは全角ローマ字/数字(ＡＳＨ／ＲＩＺＩＮ．５４)をそのまま返す。サイトの既存891件は半角
# なので、出口で半角に正規化する(2026-06-25・全角混入でレビューが進まない事故の恒久対策)。
# （）／〜～は意味のある記号(バッジ/ツアー列挙/期間)なのでNFKCで壊さないよう退避して保護する。
_FW_PROT = {'（': '', '）': '', '／': '', '〜': '', '～': ''}
_FW_UNPROT = {v: k for k, v in _FW_PROT.items()}
def norm_fw(s):
    if not isinstance(s, str) or not s:
        return s
    for k, v in _FW_PROT.items():
        s = s.replace(k, v)
    s = unicodedata.normalize('NFKC', s)
    for k, v in _FW_UNPROT.items():
        s = s.replace(k, v)
    return s

# 「最新CD」リンク(links.amazon)を自動付与する音楽系ジャンル。フェス/sports/engeki/owarai/
# dento/kids/musical等は付けない(汎用グッズボタンに任せる)。memory: reference_amazon_affiliate
MUSIC_GENRES = {'jpop', 'rock', 'idol', 'kpop', 'hiphop', 'classic', 'anime', 'seiyuu', 'vtuber', 'youtuber', 'enka', 'jazz'}
def amazon_cd(name):
    """アーティスト名からAmazon音楽カテゴリ検索リンクを作る。イベント名の尻尾は落とす。"""
    kw = re.sub(r'＜.*?＞', '', name); kw = re.sub(r'（.*?）', '', kw)
    kw = re.split(r'\s+(?:トーク|コンサート|ツアー|ＬＩＶＥ|LIVE|Ｌｉｖｅ|ライブ|リサイタル|ギター|シネマ|２０[０-９]{2}|20\d\d|ｉｎ|周年)', kw)[0].strip('　 ').strip()
    if not kw:
        return None
    return 'https://www.amazon.co.jp/s?k=' + urllib.parse.quote(kw + ' CD') + '&i=specialty-aps&srs=26200021051&tag=oshinavi0a-22'

# 「買えると判定したのに取り込めなかったカード」を貯める(無言ドロップ撲滅・2026-06-23)。
# build後に__main__が大声で報告し、1件でもあれば非ゼロ終了でゲートする。
_DROPPED = []

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

def is_preflist(place):
    """place が「県名の羅列」だけ(実会場名でない)か。全国ツアーのバンドル行は
    __place に「東京／大阪／愛知」の形で県が入る。"""
    if not place:
        return False
    return not PREF_RE.sub('', place).replace('／', '').replace('・', '').replace('　', '').strip()

def prefs_for(region, place):
    """券種カードの都道府県を決める。

    【最重要】実会場名から県名を拾ってはいけない。会場名に他県の名が入っていると誤検出し、
    複数県扱い → prefecture が「全国」に化ける（2026-07-14 ANN WILSON＝会場「東京建物
    Brillia HALL 箕面 大ホール」は"大阪"の劇場なのに、会場名の"東京"を拾って大阪・東京の
    2県と読み全国になっていた）。ぴあが出す __region が正。
    会場名を見るのは ①place が県名の羅列(=複数県ツアー行) ②region が空 の時だけ。"""
    if is_preflist(place):
        return extract_prefs(region, place)
    prefs = extract_prefs(region)
    if not prefs:
        prefs = extract_prefs(place)   # regionが取れない時だけ会場名から推測
    return prefs
def normalize_pia_url(u):
    """ticketInformation.do?...&rlsCd=XXX は『特定リリース専用ページ』で、そのリリースが
    終了すると買える枠ゼロを返す（イベント全体ではまだ受付中でも）。誤って販売中エントリを
    削除候補化する事故の元なので、必ず event.do（イベント全体）に正規化してから取得する。
    （2026-06-26 美川憲一/コロッケ誤削除候補化の恒久対策）"""
    if not u or 'ticketInformation.do' not in u:
        return u
    mb = re.search(r'eventBundleCd=(\w+)', u)
    if mb:
        return 'https://t.pia.jp/pia/event/event.do?eventBundleCd=' + mb.group(1)
    me = re.search(r'eventCd=(\w+)', u)
    if me:
        return 'https://t.pia.jp/pia/event/event.do?eventCd=' + me.group(1)
    return u

def fetch(u):
    u = normalize_pia_url(u)
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')

def is_error_page(h):
    """ぴあのエラー/確認ページ判定。eventCdが無効化/削除/差し替えされるとイベント本文でなく
    「ご確認ください」(error-container)が返る。0カードと区別できず無言で枠を失う原因なので
    明示検出する(2026-06-30 風輪のeventCd 2623808が朝有効→夜無効化=ご確認ください の取りこぼし)。"""
    return bool(h) and ('<title>ご確認ください' in h or 'class="error-container"' in h)

class WpiaFormPage(Exception):
    """【誤削除の罠】ぴあが券種を w.pia.jp/t/xxx（WEB直販ページ）で出すイベントは、t.pia.jp 側に
    ticketSalesCard-2024 の券種カードを1枚も持たない。パーサは0カード→「買える枠ゼロ」と読み、
    販売中のエントリを削除候補に出してしまう（2026-07-15 nobinobi 2026＝当日12:00発売開始の
    フェスを危うく削除するところだった）。カード0かつw.pia.jpリンク有り＝機械照合の対象外なので、
    Noneを返さず例外で止める。呼び出し側は削除候補にせず人間の目視へ回すこと。"""

def wpia_only(h):
    """券種カードが1枚も無く、w.pia.jp の購入リンクがある＝WEB直販形式のページ。"""
    if not h:
        return False
    return 'ticketSalesList-2024__item' not in h and 'https://w.pia.jp/t/' in h
def txt(s): return _html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s or ''))).strip()
def wd(iso):
    y, m, d = map(int, iso.split('-')); return WD[datetime.date(y, m, d).weekday()]
def jp(iso):
    y, m, d = map(int, iso.split('-')); return f"{y}年{m}月{d}日({wd(iso)})"
def prefshort(p): return p if p == '北海道' else re.sub(r'(都|道|府|県)$', '', p)
def md(iso): _, m, d = iso.split('-'); return f"{int(m)}/{int(d)}"
def era(iso):
    """公演年が当年(today基準)より先なら令和略記「R{N}年 」(2027→R9年/2028→R10年)。当年以下は空。
    旧md()は年を捨てており2027公演のR9年表記が毎回抜けていた恒久対策(2026-06-28・feedback_r9_year_notation)。"""
    y = int(iso[:4]); base = datetime.date.today().year
    return f"R{y - 2018}年 " if y > base else ''
def mdbadge(start, end):
    """公演日バッジ。単日=R{N}年付M/D。範囲=同年(同era)なら先頭だけ・異年は両端にera。
    ※異年で開始側のeraを落とすバグがあった(2027→2028ツアーでstart=2027のR9年が消えた=2026-06-30
    Vaundy 2027-2028で発覚)。es='' なら自然に省略されるので両端付けが正しい。"""
    s_md = f"{int(start[5:7])}/{int(start[8:10])}"; e_md = f"{int(end[5:7])}/{int(end[8:10])}"
    es, ee = era(start), era(end)
    if start == end: return f"{es}{s_md}"
    if es == ee: return f"{es}{s_md}〜{e_md}"
    return f"{es}{s_md}〜{ee}{e_md}"
def ecd_url(u):
    mm = re.search(r'eventCd=(\w+)', u or ''); return 'https://t.pia.jp/pia/event/event.do?eventCd=' + mm.group(1) if mm else None

def src_event_url(u):
    """候補の元URL(eventCd or eventBundleCd)から、その公演ページの event.do URL を作る。
    抽選券(lotRlsCd hrefでeventCd無し)に「由来ページ」のurlを付けてボタン誤誘導を防ぐため。"""
    mb = re.search(r'eventBundleCd=(\w+)', u or '')
    if mb: return 'https://t.pia.jp/pia/event/event.do?eventBundleCd=' + mb.group(1)
    return ecd_url(u)

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
        elif cls == 'is-active' or re.search(r'(販売期間中|受付中|発売中|販売中|発売初日|本日発売)', stt):
            # ※「本日発売初日」はクラスがis-beforeでも“今日から販売中”＝受付中扱い。
            #   発売前(これから)と取り違えると parse_when が終了日のみ「～7/23」を解析できず脱落する
            #   (2026-06-23 めざましWANGANフェス8/5 New Beginning Fesがドロップした反省)。
            state = '受付中'
        elif cls == 'is-before' or '発売前' in stt or 'まもなく' in stt:
            state = '発売前'
        else:
            state = '受付終了'
        place = txt(g(r'__place"[^>]*>(.*?)</span>'))
        region = txt(g(r'__region">(.*?)</span>'))
        prefs = prefs_for(region, place)   # 実会場名からは県を拾わない(全国化バグの恒久対策)
        rows.append({
            'perfdate': dts[0] if dts else '', 'perf_end': dts[-1] if dts else '',
            'venue': '' if is_preflist(place) else place, 'prefs': prefs,
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

def drop_labels_in_name(type_str, name):
    """券種名の【ラベル】が公演名にも入っているなら冗長なので落とす。
    例: 公演名「【かわさきジャズ2026】しんゆりJAZZストリーム」の枠が
        「一般発売【かわさきジャズ2026】」になるとバッジが二重に名乗って読みにくい。
    「【学生限定LIVE】」「【サイン会付き】」のように公演名に無いものは券種の区別なので残す。"""
    n = norm_fw(name or '')
    def _f(m):
        return '' if norm_fw(m.group(1)) in n else m.group(0)
    return re.sub(r'【(.*?)】', _f, type_str)

def kenshu(title):
    labels = []
    base = _kenshu_base(title, labels)
    # 説明ラベル(【11月平日限定】【サイン会付き】【座席券】等)は券種名に戻す。落とすと特典違い・
    # 席種違いの枠が同じバッジ文字列になり「同じバッジが2つ」に見える(2026-07-15 ミルキー☆サブウェイ展
    # のサイン会付き券／特別展「生きものたちの性」の11月平日限定券で発覚)。
    return base + ''.join(f'【{x}】' for x in labels)

def _kenshu_base(title, labels):
    # ＜...＞【...】〔...〕［...］の囲み(公演日/区分指定)を全部除去。中の全角／を区切りと誤認して
    # 「一般発売（９」「一般発売【６」等に化けるのを防ぐ(2026-06-23 JUJU・KAWAII LABで発覚)。
    def _brace(m):
        inner = m.group(1).strip()
        # 落とすのは①券種語の装飾囲み(【一般発売】【先行】)②公演日の囲み(【６／２７公演】)。
        # それ以外＝券種を区別する説明ラベル(【11月平日限定】【座席券】)は labels に退避して残す。
        if re.search(r'(発売|販売|先行|受付|プリセール|プレリザーブ|抽選|当日|公演)', inner):
            return ''
        if re.search(r'[0-9０-９]{1,2}\s*[／/]\s*[0-9０-９]{1,2}', inner):
            return ''
        if inner:
            labels.append(inner)
        return ''
    # ＜…＞も同じ扱い。＜６／２４公演＞は落とすが、＜学生限定LIVE＞＜2DAY通し券＞は券種を分ける
    # 情報なので残す（落とすと学生限定券と通常券が同じ「一般発売」バッジになり1枠に潰れる。
    # 2026-07-15 KAWAII LAB. MATESで発覚）。
    t = re.sub(r'＜(.*?)＞', _brace, title)
    t = re.sub(r'【(.*?)】', _brace, t)
    t = re.sub(r'〔.*?〕', '', t)
    t = re.sub(r'［.*?］', '', t)
    # ◎K-1.CLUB◎一般発売 のように【同じ記号で囲んだ装飾ラベル】を先頭に付ける表記がある。
    # 先頭/末尾stripでは内側の記号が残る（2026-07-13 K-1 WORLD MAXで発覚）。囲みごと落とす。
    t = re.sub(r'^([●○◎★☆■◆])[^●○◎★☆■◆]*\1', '', t).strip()
    # （９／２２公演）等の丸カッコ公演日も除去。type側で（県 M/D公演）を付け直すので不要。
    t = re.sub(r'（[^（）]*(?:公演|／)[^（）]*）', '', t)
    # 「９／１８（金）一般発売」のように公演日を券種名の頭に付ける表記がある。この／を下の
    # 「券種／公演名」区切りと誤認すると券種名が「9」だけになる（2026-07-14 巨人×中日で発覚）。
    t = re.sub(r'^[0-9０-９]{1,2}\s*[／/]\s*[0-9０-９]{1,2}\s*(?:（[^（）]*）|\([^()]*\))?\s*', '', t).strip()
    KW = (r'(プレイガイド最速先行|最速先行|オフィシャル先行|\d次プレリザーブ|プレリザーブ\d次|'
          r'プレリザーブ|\d次受付|プリセール|一般発売|一般販売|当日引換券|当日券|先行)')
    if '／' in t:
        # 先頭/末尾の飾り記号(●○★@※等)はぴあ表記の装飾。バッジに出さない(2026-07-10)。
        head = t.split('／')[0].strip('　 .・●○◎◆◇■□★☆@＠※〇▼▲').strip()
        # ぴあは「券種 ／ 公演名」が基本だが、公演名そのものに／を含み「公演名★2次受付〔東京〕」と
        # 出す枠がある。この場合 head は公演名の断片＝券種でない（2026-07-14『いきなり本読み!』で発覚）。
        # head に券種語が無ければ、元の文字列から券種語を拾い直す。
        if head and not re.search(r'(発売|販売|先行|受付|プリセール|プレリザーブ|当日|抽選)', head):
            m = re.search(KW, t)
            if m:
                return m.group(1)
        return head or '一般発売'
    m = re.search(KW, t)
    return m.group(1) if m else '先行'

def parse_when(state, when):
    if state == '発売前':
        m = re.search(r'(\d{4})/(\d{1,2})/(\d{1,2})\([^)]*\)\s*[^\d:：～]*(\d{1,2}:\d{2})?\s*より発売', when)
        if m:
            iso = f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"; t = m.group(4)
            return (f"{int(m.group(2))}/{int(m.group(3))} {t}発売" if t else f"{int(m.group(2))}/{int(m.group(3))}発売"), iso, iso
        # プレリザーブ/抽選受付など「START(日 時) ～ END」レンジ形。
        # 例: "2026/6/20(土) 11:00 ～ 2026/6/28(日) 23:59"
        # START=発売日→startDate(カウントダウン先)、END=販売終了日→date(発売時刻後の「〜締切」表示)。
        # 2026-07-09修正: 従来ENDを捨てdate=STARTにしていたため、発売時刻を過ぎると「販売中〜発売日」に
        # 壊れて表示された(ユーザー指摘・倉敷歌謡コンサート等16件)。ENDを取り込み date=END/startDate=START に。
        m2 = re.search(r'(\d{4})/(\d{1,2})/(\d{1,2})\([^)]*\)\s*[^\d:：～]*(\d{1,2}:\d{2})?\s*～\s*(?:(\d{4})/(\d{1,2})/(\d{1,2}))?', when)
        if m2:
            iso = f"{m2.group(1)}-{int(m2.group(2)):02d}-{int(m2.group(3)):02d}"; t = m2.group(4)
            end = f"{m2.group(5)}-{int(m2.group(6)):02d}-{int(m2.group(7)):02d}" if m2.group(5) else iso
            return (f"{int(m2.group(2))}/{int(m2.group(3))} {t}発売" if t else f"{int(m2.group(2))}/{int(m2.group(3))}発売"), end, iso
        # 終了日だけの形「～ END」で来る先行(本日発売初日の前日等)→ENDを採り販売中形で拾う。
        # 開始日が読めずNoneで無言ドロップしていた(2026-06-24 琉球フェスFM沖縄先着先行の反省)。
        m3 = re.search(r'～\s*(\d{4})/(\d{1,2})/(\d{1,2})\([^)]*\)\s*[^\d:：～]*(\d{1,2}:\d{2})?', when)
        if m3:
            iso = f"{m3.group(1)}-{int(m3.group(2)):02d}-{int(m3.group(3)):02d}"; t = m3.group(4)
            return (f"〜{int(m3.group(2))}/{int(m3.group(3))} {t}" if t else f"〜{int(m3.group(2))}/{int(m3.group(3))}"), iso, None
        # 時刻だけの「HH:MMより発売」(日付なし) = 本日発売。ぴあは“当日に発売開始する枠”を日付省略で
        # 時刻だけ書く(将来発売は必ずYYYY/M/D形で書く)。日付が読めずNoneで無言ドロップしていた当日引換券/
        # 本日発売を today で拾う。2026-06-30 飯田洋輔の当日引換券「18:00より発売」=本日(6/30)発売の取り
        # こぼしが真因(FRUITS ZIPPER 115/NXMERCY/LANAも同型)。実HTML確認: is-before「本日発売初日」に
        # 切替わる前の発売前表示が時刻のみだった。
        m4 = re.search(r'(\d{1,2}:\d{2})\s*より発売', when)
        if m4 and not re.search(r'\d{4}/\d', when):
            td = datetime.date.today()
            return f"{td.month}/{td.day} {m4.group(1)}発売", td.isoformat(), td.isoformat()
    else:
        m = re.search(r'～\s*(\d{4})/(\d{1,2})/(\d{1,2})\([^)]*\)\s*[^\d:：～]*(\d{1,2}:\d{2})?', when)
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
# トップカテゴリ単位のフォールバック（サブカテゴリがMAP未収載の時）
PIA_CAT_FALLBACK = {'スポーツ': ('sports', None), 'クラシック': ('classic', None)}

def pia_subcat(h):
    """HTMLの<title>から (カテゴリ, サブカテゴリ) を抽出。bundleページ等で取れなければ None。"""
    m = re.search(r'<title>([^<]*)</title>', h or '')
    if not m: return None
    title = _html.unescape(m.group(1))
    mc = re.search(r'\[([^\]\s]+)\s+(.+?)のチケット', title)
    return (mc.group(1), mc.group(2)) if mc else None

# 邦楽(和楽器)を示す語。ぴあの「演歌・邦楽」は演歌(enka)と邦楽(和楽器=dento)を1カテゴリに
# まとめているので、名前にこれらが含まれれば dento、無ければ enka に分ける(2026-06-23ユーザー指摘)。
HOGAKU_RE = re.compile(r'和太鼓|太鼓|三味線|津軽|琴|箏|筝|尺八|雅楽|民謡|和楽器|邦楽|篠笛|笙|能楽|長唄|常磐津')
def genre_from_subcat(cat, sub, name=''):
    """ (カテゴリ,サブ,名前) → (主ジャンル, 追加ジャンル or None)。判定不能なら None。"""
    if sub and '邦楽' in sub:   # 「演歌・邦楽」→ 和楽器系はdento、それ以外は演歌(enka)
        return ('dento', None) if HOGAKU_RE.search(name or '') else ('enka', None)
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
            cards = parse_cards(h)
            su = src_event_url(u)
            for c in cards:
                c['_src'] = su          # このカードが載っていた公演ページ(eventCd/bundle)を記録
            allrows += cards; time.sleep(0.25)
        except Exception as ex:
            # フェッチ/パース失敗を無言で握り潰さない（買える枠を黙って失う原因）
            _DROPPED.append((cand.get('newid'), 'FETCH-ERR', str(ex)[:80], u))
    buy = [r for r in allrows if r['state'] in ('受付中', '発売前')]
    seen, rows = set(), []
    for r in buy:
        k = (r['perfdate'], r['perf_end'], r['venue'], r['title'], r['state'])
        if k in seen: continue
        seen.add(k); rows.append(r)
    if not rows:
        # 【誤削除の罠】買える枠ゼロに見えても、ページがw.pia.jp直販形式なら「券種カードが無い」
        # だけで実際は販売中のことがある。Noneを返すと呼び出し側が削除候補にするので例外で止める。
        if any(wpia_only(h) for h in htmls):
            raise WpiaFormPage(f"w.pia.jp直販形式(券種カード0)＝機械照合できない。実ページを目視で確認: {cand['urls']}")
        return None
    venues = list(dict.fromkeys(r['venue'] for r in rows if r['venue']))
    prefs = list(dict.fromkeys(p for r in rows for p in r['prefs']))
    starts = sorted(r['perfdate'] for r in rows if r['perfdate'])
    ends = sorted((r.get('perf_end') or r['perfdate']) for r in rows if r['perfdate'])
    # multi=「買える券種が複数の公演ページ(eventCd/bundle)由来」。この時だけ各ticketに会場別url
    # を付ける(=下のベンダーボタンを自動非表示にして1会場誤誘導を防ぐ)。単一ページ由来なら
    # links.pia=その1ページが全券種を載せるのでボタンはそのまま正しく機能する。
    srcs = set(r.get('_src') for r in rows if r.get('_src'))
    multi = len(srcs) > 1
    tickets = []
    for r in rows:
        suf, iso, sd = parse_when(r['state'], r['when'])
        if not iso:
            # 【最重要】買えると判定したカードの日付が解析できない＝取りこぼし。
            # 黙ってcontinueすると枠が無言で消える(2026-06-23の全取りこぼしの真因)。
            # 必ず記録して build 後に大声で報告する。新しいぴあ表記が来たら即バレる。
            _DROPPED.append((cand.get('newid'), r.get('state'), r.get('when', ''), r.get('title', '')[:40]))
            continue
        pe = r.get('perf_end') or r['perfdate']
        mdr = mdbadge(r['perfdate'], pe)   # 2027公演は自動でR9年付与(年が抜けない)
        _pf = '・'.join(r['prefs']) if r['prefs'] else '全国'   # 複数県は全部載せる(字は小さめ表示)。県名取れなければ全国
        ks = drop_labels_in_name(kenshu(r['title']), cand.get('artist'))
        t = {'type': f"{ks}（{_pf} {mdr}公演）{suf}", 'date': iso}
        if sd: t['startDate'] = sd
        # 抽選券(先行/プレリザーブ)はhrefがlotRlsCdでeventCd無し→由来ページ(_src)のurlで補完。
        # これで複数会場エントリの全ticketにurlが付き、ボタン誤誘導が消える(2026-06-23恒久修正)。
        if multi:
            tu = ecd_url(r['url']) or r.get('_src')
            if tu: t['url'] = tu
        tickets.append(t)
    tickets.sort(key=lambda t: t['date'])
    # 全会場を列挙する（[:4]で打切ると大規模ツアーの大半の会場が消える＝2026-07-01発覚
    # ディズニー・オン・クラシック18県中4会場しか出ず「アクトシティ浜松が抜けてる」）。
    venue = venues[0] if len(venues) == 1 else '全国ツアー（' + '／'.join(venues) + '）'
    pref = prefs[0] if len(prefs) == 1 else '全国'
    # 同一公演日の枠が2つ以上あると starts が ['8/3','8/3'] になり、len==1 を満たさず範囲形に落ちて
    # 「2026年8月3日(月)〜2026年8月3日(月)」と冗長表示になっていた(2026-07-15 KAWAII LAB.等4件)。
    # 判定は件数でなく「最早の開始日==最遅の終了日」＝実質単日か、で行う。
    if starts and ends[-1] == starts[0]:
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
        if sc and genre_from_subcat(*sc, cand['artist']):
            pg, sub_used = genre_from_subcat(*sc, cand['artist']), f"{sc[0]}/{sc[1]}"; break
    if not pg:  # bundleページはサブカテゴリ無し → 個別eventCdページを1つ引いて再試行
        for r in rows:
            eu = ecd_url(r.get('url'))
            if not eu: continue
            try:
                sc = pia_subcat(fetch(eu)); time.sleep(0.2)
            except Exception:
                sc = None
            if sc and genre_from_subcat(*sc, cand['artist']):
                pg, sub_used = genre_from_subcat(*sc, cand['artist']), f"{sc[0]}/{sc[1]}"; break
    main_genre, extra = pg if pg else (genre_of(cand['artist']), None)
    links = {'rakuten': None, 'lawson': None, 'pia': pia, 'eplus': None}
    # 音楽系の単独/グループ名義は「最新CD」リンクを自動付与(合同公演／×は除外＝レビューで判断)。
    if main_genre in MUSIC_GENRES and not re.search(r'／|×', cand['artist']):
        amz = amazon_cd(cand['artist'])
        if amz:
            links['amazon'] = amz
    # 出口で全角ローマ字/数字を半角化（表示フィールドのみ。URL/日付/_piaSubは触らない）。
    for t in tickets:
        t['type'] = norm_fw(t['type'])
    return {'id': cand['newid'], 'artist': norm_fw(cand['artist']), 'name': norm_fw(cand['artist']), 'date': ends[-1],
            'dateLabel': norm_fw(dl), 'venue': norm_fw(venue), 'prefecture': pref, 'genre': 'new',
            '_genre': main_genre, '_extraGenres': [extra] if extra else [], '_piaSub': sub_used,
            'price': None, 'links': links,
            'tickets': tickets, 'verified': True, 'verifiedAt': datetime.date.today().isoformat()}

def _selftest():
    """過去の取りこぼし/化けバグの回帰防止テスト(2026-06-23)。`python tools/build_pia_entries.py --selftest`"""
    # ① 時刻プレフィックスは列挙せず「数字/コロン以外は何でも飛ばす」robust方式。
    #    昼/夜/朝/午前/午後/正午/未知語/プレフィックス無し すべてで脱落しない。
    # (state, when, exp_date, exp_startDate, exp_suffix)
    # 発売前レンジ「START ～ END」: date=END(締切) / startDate=START(発売日) / badge=発売日
    cases = [
        ('発売前', '2026/6/28(日) 昼12:00 ～ 2026/7/12(日) 23:59', '2026-07-12', '2026-06-28', '6/28 12:00発売'),
        ('発売前', '2026/6/28(日) 夜18:00 ～ 2026/7/12(日) 23:59', '2026-07-12', '2026-06-28', '6/28 18:00発売'),
        ('発売前', '2026/6/28(日) 午前10:00 ～ 2026/7/1(火) 23:59', '2026-07-01', '2026-06-28', '6/28 10:00発売'),
        ('発売前', '2026/6/28(日) 13:00 ～ 2026/7/1(火) 23:59', '2026-07-01', '2026-06-28', '6/28 13:00発売'),  # プレフィックス無し
        ('発売前', '2026/6/24(水) 11:00 ～ 2026/6/30(火) 11:00', '2026-06-30', '2026-06-24', '6/24 11:00発売'),
        # 「より発売」単日形(END無し)→ date=startDate=発売日(従来通り)
        ('発売前', '2026/7/25(土) 昼12:00より発売', '2026-07-25', '2026-07-25', '7/25 12:00発売'),
        ('発売前', '2026/7/25(土) 14:00より発売', '2026-07-25', '2026-07-25', '7/25 14:00発売'),
        ('発売前', '2026/7/25(土) 10:00より発売', '2026-07-25', '2026-07-25', '7/25 10:00発売'),
        ('受付中', '～ 2026/10/21(水) 夜23:59', '2026-10-21', None, '〜10/21 23:59'),
        ('受付中', '～ 2026/10/21(水) 13:00', '2026-10-21', None, '〜10/21 13:00'),
        ('発売前', '～ 2026/6/24(水) 23:59', '2026-06-24', None, '〜6/24 23:59'),  # 終了日だけの先行(琉球フェスFM沖縄)→無言ドロップ防止
    ]
    for st, w, exp_iso, exp_sd, exp_suf in cases:
        suf, iso, sd = parse_when(st, w)
        assert iso == exp_iso and sd == exp_sd and suf == exp_suf, (w, '→', suf, iso, sd)
    # 時刻だけの「HH:MMより発売」(日付なし)= 本日発売 → today を採る(無言ドロップ根絶。2026-06-30飯田の
    # 当日引換券「18:00より発売」=本日発売の取りこぼし対策)。todayは可変なので動的に照合。
    _td = datetime.date.today()
    for w, hhmm in [('18:00より発売', '18:00'), ('当日引換券 10:00より発売', '10:00')]:
        suf, iso, sd = parse_when('発売前', w)
        assert iso == _td.isoformat() and sd == _td.isoformat(), ('本日発売', w, suf, iso, sd)
        assert suf == f"{_td.month}/{_td.day} {hhmm}発売", ('本日発売suf', w, suf)
    # 将来発売(YYYY/M/D形)は today に化けない(m4が誤爆しない)
    suf, iso, sd = parse_when('発売前', '2026/9/9(水) 18:00より発売')
    assert iso == '2026-09-09', ('将来発売がm4誤爆', suf, iso)
    # ② 全角カッコ/角カッコ/山カッコの公演日「（９／２２公演）」「【６／２７公演】」でkenshuが化けない
    assert kenshu('一般発売（９／２２公演） ／ ＪＵＪＵ') == '一般発売', kenshu('一般発売（９／２２公演） ／ ＪＵＪＵ')
    assert kenshu('一般発売＜６／２４公演＞ ／ ＪＵＪＵ') == '一般発売', kenshu('一般発売＜６／２４公演＞ ／ ＪＵＪＵ')
    assert kenshu('一般発売【６／２７公演】 ／ ＫＡＷＡＩＩ ＬＡＢ') == '一般発売', kenshu('一般発売【６／２７公演】 ／ ＫＡＷＡＩＩ ＬＡＢ')
    assert kenshu('「奥華子」プレリザーブ') == 'プレリザーブ', kenshu('「奥華子」プレリザーブ')
    # ②' ぴあ表記の飾り記号(●○★@※)はバッジに出さない(2026-07-10 さだまさし「●一般発売」で発覚)
    assert kenshu('●一般発売 ／ さだまさし') == '一般発売', kenshu('●一般発売 ／ さだまさし')
    assert kenshu('☆一般発売 ／ ディズニー・オン・クラシック') == '一般発売'
    assert kenshu('@プリセール ／ さだまさし') == 'プリセール'
    # ②'' ◎…◎ の囲み装飾ラベル（2026-07-13 K-1 WORLD MAX）
    assert kenshu('◎K-1.CLUB◎一般発売 ／ Ｋ－１ ＷＯＲＬＤ ＭＡＸ') == '一般発売', kenshu('◎K-1.CLUB◎一般発売 ／ Ｋ－１ ＷＯＲＬＤ ＭＡＸ')
    assert kenshu('◎K-1.CLUB 限定◎有料会員先行発売 ／ Ｋ－１') == '有料会員先行発売', kenshu('◎K-1.CLUB 限定◎有料会員先行発売 ／ Ｋ－１')
    # ②'' 券種名の頭に付く公演日「９／１８（金）一般発売」（2026-07-14 読売ジャイアンツ対中日）
    #     この／を「券種／公演名」の区切りと誤読すると券種名が「9」だけになる
    assert kenshu('９／１８（金）一般発売 ／ 読売ジャイアンツ対中日ドラゴンズ 公式戦') == '一般発売', \
        kenshu('９／１８（金）一般発売 ／ 読売ジャイアンツ対中日ドラゴンズ 公式戦')
    assert kenshu('9/19 一般発売 ／ 巨人戦') == '一般発売', kenshu('9/19 一般発売 ／ 巨人戦')
    # ②''' 公演名そのものに／が入り「公演名★2次受付〔県〕」形で出る枠（2026-07-14『いきなり本読み!』）
    assert kenshu('『いきなり本読み！In IMM／いきなり本読み！サテライト』★2次受付〔東京〕') == '2次受付', \
        kenshu('『いきなり本読み！In IMM／いきなり本読み！サテライト』★2次受付〔東京〕')
    # ③ 「本日発売初日」(is-beforeだが今日から販売中)は受付中扱いで終了日のみ「～7/23」を拾える
    suf, iso, sd = parse_when('受付中', '～ 2026/7/23(木) 23:59')
    assert iso == '2026-07-23' and sd is None, ('本日発売初日(受付中)', suf, iso, sd)
    # ④ 「演歌・邦楽」カテゴリ: 和楽器名はdento、演歌歌手はenka(邦楽≠演歌・2026-06-23ユーザー指摘)
    assert genre_from_subcat('音楽', '演歌・邦楽', '徳永ゆうき') == ('enka', None)
    assert genre_from_subcat('音楽', '演歌・邦楽', 'ＴＡＯの夏フェス 和太鼓') == ('dento', None)
    assert genre_from_subcat('音楽', '演歌・邦楽', '津軽三味線コンサート') == ('dento', None)
    # ⑤ R9年(令和9年=2027)自動付与: 当年(today)より先の公演年は略記が付く・範囲は端点別
    assert era('2026-12-27') == '' and era('2027-01-09').strip() == 'R9年', '当年=空/翌年=R9年'
    assert mdbadge('2027-01-30', '2027-01-30') == 'R9年 1/30', '単日2027'
    assert mdbadge('2026-11-08', '2026-11-08') == '11/8', '単日2026'
    assert mdbadge('2027-01-09', '2027-01-11') == 'R9年 1/9〜1/11', '範囲同年(2027)は先頭だけ'
    assert mdbadge('2026-12-03', '2027-01-08') == '12/3〜R9年 1/8', '範囲異年は終了側にR9年'
    assert mdbadge('2026-11-07', '2026-11-08') == '11/7〜11/8', '範囲同年(2026)は素'
    # 両端とも将来年の異年範囲(2027→2028)は開始側のeraも残す(Vaundy 2027-2028でR9年が落ちた反省)
    assert mdbadge('2027-08-14', '2028-02-27') == 'R9年 8/14〜R10年 2/27', '異年2027→2028は両端era'
    assert mdbadge('2028-02-27', '2028-02-27') == 'R10年 2/27', '単日2028=R10年'
    # ⑥ w.pia.jp直販形式の検出（2026-07-15 nobinobi 2026を誤って削除候補にした事故の回帰テスト）
    #    券種カード0＋w.pia.jpリンク有り=販売中でも0枠に見える → 削除候補にしてはいけない
    assert wpia_only('<div>チケット情報<a href="https://w.pia.jp/t/nobinobi26-2days/">チケット購入</a></div>') is True
    assert wpia_only('<li class="ticketSalesList-2024__item"><p class="ticketSalesCard-2024__status is-active">受付中</p></li>') is False
    assert wpia_only('<html><body>券種の無い普通のページ</body></html>') is False
    # 券種カードとw.pia.jpが同居するページは通常パースできるので罠ではない
    assert wpia_only('<li class="ticketSalesList-2024__item">…</li><a href="https://w.pia.jp/t/x/">購入</a>') is False
    # ⑦ 都道府県は__regionが正・実会場名から拾わない（2026-07-14 ANN WILSONの「全国」化バグ）
    assert prefs_for('大阪', '東京建物 Brillia HALL 箕面 大ホール') == ['大阪'], prefs_for('大阪', '東京建物 Brillia HALL 箕面 大ホール')
    assert prefs_for('北海道', 'Zepp Sapporo') == ['北海道']
    assert prefs_for('東京', '東京／大阪／愛知') == ['東京', '大阪', '愛知'], '県名の羅列(複数県ツアー行)は会場名側も拾う'
    assert prefs_for('', '東京建物 Brillia HALL') == ['東京'], 'regionが空の時だけ会場名から推測'
    assert is_preflist('東京／大阪') is True and is_preflist('Zepp Sapporo') is False
    # ⑧ 【…】は装飾なら落とし、券種を区別する説明ラベルは残す
    #    (2026-07-15 サイン会付き券・11月平日限定券が「一般発売」に潰れ同一バッジ化した回帰テスト)
    assert kenshu('一般発売【亀山陽平監督 サイン会付き】 ／ 銀河特急 ミルキー☆サブウェイ') == '一般発売【亀山陽平監督 サイン会付き】', \
        kenshu('一般発売【亀山陽平監督 サイン会付き】 ／ 銀河特急 ミルキー☆サブウェイ')
    assert kenshu('【１１月平日限定】超早割チケット ／ 特別展「生きものたちの性」') == '超早割チケット【１１月平日限定】', \
        kenshu('【１１月平日限定】超早割チケット ／ 特別展「生きものたちの性」')
    assert kenshu('【一般発売】 ／ 工藤静香') == '一般発売', kenshu('【一般発売】 ／ 工藤静香')   # 装飾囲みは落とす
    assert kenshu('一般発売 ／ ＺＩＧＧＹ') == '一般発売'
    # ＜…＞も同様：公演日囲みは落とし、券種を分ける説明は残す（学生限定LIVE券が通常券と同一バッジに潰れた）
    assert kenshu('一般発売 ／ ＫＡＷＡＩＩ ＬＡＢ． ＭＡＴＥＳ＜学生限定ＬＩＶＥ＞') == '一般発売【学生限定ＬＩＶＥ】', \
        kenshu('一般発売 ／ ＫＡＷＡＩＩ ＬＡＢ． ＭＡＴＥＳ＜学生限定ＬＩＶＥ＞')
    # ⑨ 公演名に既にあるラベルはバッジで二重に名乗らない（かわさきジャズ2026）／無いものは残す
    assert drop_labels_in_name('一般発売【かわさきジャズ2026】', '【かわさきジャズ2026】しんゆりJAZZストリーム DAY1') == '一般発売'
    assert drop_labels_in_name('一般発売【学生限定LIVE】', 'KAWAII LAB. MATES／KAWAII LAB. SOUTH') == '一般発売【学生限定LIVE】'
    assert drop_labels_in_name('超早割チケット【11月平日限定】', '特別展「生きものたちの性」') == '超早割チケット【11月平日限定】'
    print('selftest OK: parse_when/kenshu/R9年(mdbadge)/wpia_only/prefs_for/labels 回帰なし')

if __name__ == '__main__':
    if '--selftest' in sys.argv:
        _selftest(); sys.exit(0)
    cands = json.load(open(sys.argv[1], encoding='utf-8'))
    out, skip = [], []
    for c in cands:
        e = build(c)
        (out.append(e) if e else skip.append(c['newid']))
        sys.stderr.write(f"  {c['newid']} {'OK' if e else 'skip(売切)'}\n")
    print(json.dumps(out, ensure_ascii=False, indent=1))
    sys.stderr.write(f"構築 {len(out)} 件 / skip {skip}\n")
    # 【最重要ゲート】買えると判定したのに取り込めなかったカードを大声で報告。
    # 1件でもあれば新しいぴあ表記を取りこぼしている＝parse_when/kenshu/状態判定を直す合図。
    if _DROPPED:
        sys.stderr.write("\n" + "!" * 60 + "\n")
        sys.stderr.write(f"⚠️ 取りこぼし {len(_DROPPED)}件（買える枠なのに取り込めなかった＝要対応）:\n")
        for nid, st, when, title in _DROPPED:
            sys.stderr.write(f"   id{nid} [{st}] when={when!r} | {title}\n")
        sys.stderr.write("→ parse_when/kenshu/状態判定にこの表記を足してから再構築すること。\n")
        sys.stderr.write("!" * 60 + "\n")
        sys.exit(3)   # 非ゼロ終了でパイプライン(投入前)を止める
