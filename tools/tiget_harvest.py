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


# 🚨🚨2026-09-18 ユーザー決定＝**地名から県名を入れる**
#   「県名でお願い」。理由＝県が空だと**AREA（地方）の絞り込みから漏れる**
#   （絞り込みは券種名→prefecture→会場名の順に**県名そのもの**を探すので、
#    「仙台市青葉区」「池袋西口公園」「GOTANDA G6」では拾えない）。
#   ⚠️入れるのは**地名と県の対応が事実として決まっているものだけ**。
#     推測になる曖昧な地名（中野＝東京/長野、府中＝東京/広島 など）は**表に入れない**。
#   ⚠️「津」「堺」のような他の語に混ざる1文字地名も入れない（誤爆する）。
PLACE_PREF = {
    # 政令市・県庁所在地など（県名と違う書き方のもの）
    '札幌': '北海道', '函館': '北海道', '旭川': '北海道', '小樽': '北海道', '百合が原': '北海道',
    '仙台': '宮城', '盛岡': '岩手', '郡山': '福島', '会津': '福島',
    'さいたま': '埼玉', '大宮': '埼玉', '川越': '埼玉', '西川口': '埼玉', '川口': '埼玉',
    '横浜': '神奈川', '川崎': '神奈川', '相模原': '神奈川', '藤沢': '神奈川',
    '宇都宮': '栃木', '高崎': '群馬', '前橋': '群馬', '水戸': '茨城', 'つくば': '茨城',
    '甲府': '山梨', '松本': '長野', '金沢': '石川', '名古屋': '愛知', '豊橋': '愛知', '岡崎': '愛知',
    '浜松': '静岡', '沼津': '静岡', '四日市': '三重', '大津': '滋賀',
    '神戸': '兵庫', '姫路': '兵庫', '西宮': '兵庫', '尼崎': '兵庫',
    '北九州': '福岡', '博多': '福岡', '天神': '福岡', '小倉': '福岡',
    '那覇': '沖縄', '下関': '山口', '倉敷': '岡山', '福山': '広島',
    # 東京の地名（ライブハウスの所在地に出る形）
    '渋谷': '東京', '新宿': '東京', '池袋': '東京', '原宿': '東京', '秋葉原': '東京',
    '上野': '東京', '浅草': '東京', '品川': '東京', '五反田': '東京', 'GOTANDA': '東京',
    '高円寺': '東京', '吉祥寺': '東京', '下北沢': '東京', '恵比寿': '東京', '六本木': '東京',
    '赤坂': '東京', '銀座': '東京', '有楽町': '東京', '錦糸町': '東京', '北千住': '東京',
    '荻窪': '東京', '目黒': '東京', '大井町': '東京', '新木場': '東京', '豊洲': '東京',
    '立川': '東京', '八王子': '東京', '町田': '東京', '代官山': '東京', '青山': '東京',
    # 大阪の地名
    '梅田': '大阪', '難波': '大阪', 'なんば': '大阪', '心斎橋': '大阪', '天王寺': '大阪',
    '堺筋本町': '大阪', '日本橋': '大阪',   # ⚠️日本橋は東京にもあるが、TIGETのライブ会場は大阪側が多い
    # 京都
    '祇園': '京都', '河原町': '京都',
    # 追加（2026-09-18・ユーザーが調べる前に機械で潰せる分）
    '松江': '島根', '長堀橋': '大阪', '北参道': '東京', '鶴見': '神奈川', '大久保': '東京',
    '本八幡': '千葉', '柏': '千葉', '船橋': '千葉', '松戸': '千葉',
    '大分': '大分', '宇部': '山口', '今治': '愛媛', '米子': '鳥取',
    # 🚨「都内」は東京都内の意味＝これは事実（推測ではない）
    '都内': '東京',
    # 東京23区の区名（区名が書いてあれば東京で確定）
    '千代田区': '東京', '中央区東京': '東京', '港区': '東京', '新宿区': '東京', '文京区': '東京',
    '台東区': '東京', '墨田区': '東京', '江東区': '東京', '品川区': '東京', '目黒区': '東京',
    '大田区': '東京', '世田谷': '東京', '渋谷区': '東京', '中野区': '東京', '杉並区': '東京',
    '豊島区': '東京', '北区東京': '東京', '荒川区': '東京', '板橋区': '東京', '練馬区': '東京',
    '足立区': '東京', '足立': '東京', '葛飾': '東京', 'かつしか': '東京', '江戸川区': '東京',
    'としま': '東京',
    # 東京のその他の地名（会場名に出る形）
    '代々木': '東京', '笹塚': '東京', '池尻大橋': '東京', '三軒茶屋': '東京', '阿佐谷': '東京',
    '江戸川橋': '東京', '小岩': '東京', '表参道': '東京', '茅場町': '東京', '多摩センター': '東京',
    '上馬': '東京', '神楽坂': '東京', '中目黒': '東京', '中延': '東京', '大塚': '東京',
    # そのほか（地名と県が1対1のもの）
    '溝ノ口': '神奈川', '溝の口': '神奈川', '洗足学園': '神奈川', '彦根': '滋賀', 'ひこね': '滋賀',
    'とくしま': '徳島', '五泉': '新潟', '大須': '愛知', '掛川': '静岡', '越谷': '埼玉',
}
# 🚨ローマ字で書く会場が多い（Gotanda G6／GT LIVE TOKYO／SHIBUYA FOWS／HAKATA…）。
#   大文字小文字を無視して当てる。これも地名と県の対応＝事実なので推測ではない。
PLACE_PREF_ROMA = {
    'TOKYO': '東京', 'SHIBUYA': '東京', 'SHINJUKU': '東京', 'IKEBUKURO': '東京',
    'AKIHABARA': '東京', 'GOTANDA': '東京', 'SHIMOKITAZAWA': '東京', 'KICHIJOJI': '東京',
    'UENO': '東京', 'ASAKUSA': '東京', 'ROPPONGI': '東京', 'HARAJUKU': '東京',
    'YOKOHAMA': '神奈川', 'KAWASAKI': '神奈川', 'SAPPORO': '北海道', 'SENDAI': '宮城',
    'NAGOYA': '愛知', 'OSAKA': '大阪', 'UMEDA': '大阪', 'NAMBA': '大阪', 'SHINSAIBASHI': '大阪',
    'KYOTO': '京都', 'KOBE': '兵庫', 'HAKATA': '福岡', 'FUKUOKA': '福岡',
    'HIROSHIMA': '広島', 'OKAYAMA': '岡山', 'NIIGATA': '新潟', 'KANAZAWA': '石川',
    'OKINAWA': '沖縄', 'NAHA': '沖縄', 'SAITAMA': '埼玉', 'CHIBA': '千葉',
}
_ROMA_KEYS = sorted(PLACE_PREF_ROMA, key=len, reverse=True)
# 長い地名から当てる（「西川口」を「川口」より先に見る／「GOTANDA」など）
_PLACE_KEYS = sorted(PLACE_PREF, key=len, reverse=True)


# 🚨`pref_of` は「福岡県」の形しか見ない＝「マリンメッセ福岡B館」は拾えない。
#   県名の**短い形**もここで見る（これは推測でなく事実）。
BARE_PREF = ('北海道 青森 岩手 宮城 秋田 山形 福島 茨城 栃木 群馬 埼玉 千葉 東京 神奈川 新潟 富山 '
             '石川 福井 山梨 長野 岐阜 静岡 愛知 三重 滋賀 京都 大阪 兵庫 奈良 和歌山 鳥取 島根 '
             '岡山 広島 山口 徳島 香川 愛媛 高知 福岡 佐賀 長崎 熊本 大分 宮崎 鹿児島 沖縄').split()


def pref_from_place(text):
    """会場名・公演名の地名から県を当てる。表にある地名と県名の短い形だけ＝推測はしない。"""
    t = text or ''
    for k in _PLACE_KEYS:
        if k in t:
            return PLACE_PREF[k]
    # 🚨「京都」が「東京都」に誤マッチしないよう、東京を先に潰してから見る（index.html と同じ手）
    scan = t.replace('東京', '東京_')
    if '東京_' in scan:
        return '東京'
    for p in BARE_PREF:
        if p != '東京' and p in scan:
            return p
    up = t.upper()
    for k in _ROMA_KEYS:
        if k in up:
            return PLACE_PREF_ROMA[k]
    return None


# 🎯🎯2026-09-18 ユーザーが見つけた＝**会場の欄を押すとGoogleマップが開いて県が分かる**。
#   TIGETのHTMLには住所が無いが、会場リンクが `https://maps.google.com/?cid=<cid>` の形。
#   そのcidに **`&output=embed`** を付けると**2.6KBの軽いページ**が返り、住所が丸ごと入っている
#   （実測＝「〒169-0072 東京都新宿区大久保１丁目１７−８ RE:LIVE HALL」）。
#   ⚠️`output=embed` を付けないと800KBのJSの殻が返るだけで住所は取れない。
_CID_CACHE = {}


def pref_from_cid(cid, sleep=0.4):
    """GoogleマップのcidからJ都道府県を取る（`output=embed` の軽いページを読む）。"""
    if not cid:
        return None
    if cid in _CID_CACHE:
        return _CID_CACHE[cid]
    # 🚨Googleには**ブラウザのUAと日本語のAccept-Language**で行く。
    #    道具の共通UA（OSHINAVI-harvest）で引くと住所が日本語で返らず、県が1件も取れなかった
    #    （2026-09-18＝88件ぜんぶ None になって気づいた）。
    req = urllib.request.Request(
        'https://maps.google.com/maps?cid=%s&output=embed' % cid,
        headers={'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                '(KHTML, like Gecko) Chrome/120.0 Safari/537.36'),
                 'Accept-Language': 'ja,en;q=0.8'})
    try:
        h = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')
    except Exception:
        _CID_CACHE[cid] = None
        return None
    m = re.search(r'(東京都|大阪府|京都府|北海道|[一-龥]{2,3}県)', h)
    p = None
    if m:
        p = m.group(1)
        p = p if p == '北海道' else p[:-1]
    _CID_CACHE[cid] = p
    time.sleep(sleep)
    return p


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
    # 🚨「あと○日」「完売」の札（c-statusbox__tag）は event-title より**前**に出るので、
    #    タイトルから後ろだけ見ると取れない（2026-09-18 に取りこぼした）。カード全体で切る。
    for cm in re.finditer(r'<div class="col-xs-12(.*?)(?=<div class="col-xs-12|$)', html, re.S):
        blk = cm.group(1)
        im = re.search(r'<div class="event-title"><a href="/events/(\d+)">', blk)
        if not im:
            continue
        eid = im.group(1)
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
    # 会場リンクのGoogleマップcid（これがあれば県は確実に取れる）
    cm = re.search(r'href="https?://maps\.google\.com/\?cid=(\d+)"', sec.get('会場', ''))
    out['venue_cid'] = cm.group(1) if cm else None
    # 県の優先順＝①会場名の県名 ②JSON-LDのaddressRegion ③会場名・公演名の地名（対応表）
    #   ④（呼ぶ側で）一覧の「場所：」。⚠️配信だけのイベントは県を入れない（会場が「配信」）
    out['prefecture'] = pref_of(ven) or pref_of(out['ld_region'] or '')
    if not out['prefecture'] and not re.search(r'配信|オンライン|アーカイブ', ven + (out['name'] or '')):
        out['prefecture'] = pref_from_place(ven) or pref_from_place(out['name'] or '')
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
        # 🚨公演の塊の見出しから日付が読めないことがある（主催者が自由に書くので
        #    「1部／2部」だけ、といった形がある）。2026-09-18 に3件が「公演日なし」になり
        #    **開催が終わったものと誤判定して落とした**（コウタ10周年・Limited・YURiコス）。
        #    → 読めなければ「イベント詳細の開催日」で埋める（さらに一覧の開催日が控え＝呼ぶ側で入れる）。
        prog = {'datetime_text': dt,
                'date': parse_jp_date(dt) or out.get('detail_date'),
                'tickets': []}
        # 🚨券種の塊は「次の c-ordering-btn まで」で切る。閉じタグの並びで切ると
        #   2つめの受付期間（コンビニ決済）を落とす（2026-09-18 に実測で気づいた）。
        parts = re.split(r'<div class="c-ordering-btn ([^"]*)">', blk)
        for k in range(1, len(parts) - 1, 2):
            cls, tb = parts[k].strip(), parts[k + 1]
            out['statuses'].append(cls)
            # 🚨🚨TIGETには券種の書き方が**2種類**ある（2026-09-18＝片方しか読んでおらず
            #    61イベント・432枠が「名前も値段も無い」状態で入った）。
            #    A（単発もの）: <div class="c-ordering-btn__content__name">優先入場<br>
            #                   <div class="play-date-label">…</div>5,500円</div>
            #    B（複数日・複数枠もの）: <div class="c-ordering-btn__content-main-event__name">
            #                   <span class='c-ordering-ticket-name'>名前</span><br>
            #                   <span class='c-ordering-ticket-date'>2027年03月07日(日) 10:00開場</span><br>
            #                   <span class="c-ordering-ticket-price">110円</span></div>
            #    🚨Bは**券種ごとに公演日時を持ち、公演の塊に見出しが無い**＝日付もここから取る。
            name, price, tdate, ttime = '', None, None, None
            nb = re.search(r"c-ordering-ticket-name'>(.*?)</span>", tb, re.S)
            if nb:
                name = unesc(strip_tags(nb.group(1)))
                pb = re.search(r'c-ordering-ticket-price">\s*([0-9,]+)\s*円', tb)
                if pb:
                    price = int(pb.group(1).replace(',', ''))
                db = re.search(r"c-ordering-ticket-date'>(.*?)</span>", tb, re.S)
                if db:
                    dt2 = unesc(strip_tags(db.group(1)))
                    tdate = parse_jp_date(dt2)
                    tm2 = re.search(r'(\d{1,2}):(\d{2})', dt2)
                    ttime = '%d:%s' % (int(tm2.group(1)), tm2.group(2)) if tm2 else None
            else:
                nm = re.search(r'__content__name">(.*?)</div>\s*<div class="c-ordering-btn__content__status', tb, re.S)
                raw = nm.group(1) if nm else ''
                name = unesc(strip_tags(re.sub(r'<div class="play-date-label">.*?</div>', ' ', raw, flags=re.S)))
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
            prog['tickets'].append({'name': name, 'price': price, 'class': cls,
                                    'date': tdate, 'time': ttime, 'periods': periods})
        # 🚨B形は券種ごとに公演日時を持つ＝公演の塊の見出しが無いので、券種の日付で塊を割り直す。
        #    これをしないと「1つの公演に45券種」に見えて、昼夜も日別も潰れる。
        if any(t.get('date') for t in prog['tickets']):
            byday = {}
            for t in prog['tickets']:
                k = (t.get('date') or prog['date'], t.get('time'))
                byday.setdefault(k, []).append(t)
            for (dd, tt), ts in byday.items():
                out['programs'].append({
                    'datetime_text': ('%s %s開場' % (dd, tt)) if tt else (dd or ''),
                    'date': dd, 'tickets': ts})
        else:
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
    # カードは <div class="col-xs-12 …> で区切られ、札（あと○日）はタイトルより**前**に出る
    # 🚨地名→県の対応表（表にあるものだけ・曖昧な地名は入れない）
    assert pref_from_place('マリンメッセ福岡B館') == '福岡'
    assert pref_from_place('仙台市青葉区中央2-5-7') == '宮城'
    assert pref_from_place('池袋西口公園 グローバルリングシアター') == '東京'
    assert pref_from_place('GOTANDA G6') == '東京'
    assert pref_from_place('西川口Lavis') == '埼玉'          # 川口より先に当たること
    assert pref_from_place('リリリカフェ【百合が原公園内】') == '北海道'
    assert pref_from_place('名古屋駅 周辺') == '愛知'
    assert pref_from_place('広島アイドルライブ「POPAPIPUPEPOPA NEO」') == '広島'
    assert pref_from_place('東京都内某所') == '東京'
    assert pref_from_place('京都劇場') == '京都'              # 「東京都」に誤マッチしないこと
    assert pref_from_place('Gotanda G6') == '東京'            # 小文字でも当てる
    assert pref_from_place('GT LIVE TOKYO') == '東京'
    assert pref_from_place('GIGS YOKOHAMA TSURUMI') == '神奈川'
    assert pref_from_place('ベイサイドライブホール BY ACTIVE HAKATA') == '福岡'
    assert pref_from_place('松江canova') == '島根'
    assert pref_from_place('都内某所') == '東京'              # 「都内」は東京都内の意味
    assert pref_from_place('としま区民センター６階') == '東京'
    assert pref_from_place('溝ノ口劇場') == '神奈川'
    assert pref_from_place('ひこね市文化プラザ グランドホール') == '滋賀'
    assert pref_from_place('月夜のケダモノ') is None          # 決まらないものは空のまま
    assert pref_from_place('Nakano space Q') is None         # 中野は東京/長野で決まらない
    assert pref_from_place('ライブスペース スペシャルカラーズ') is None
    lm = parse_list_meta('<div class="col-xs-12 ev">'
                         "<div class='c-statusbox__tag'>あと64日</div>"
                         '<div class="event-title"><a href="/events/9">名</a></div>'
                         '<div class="play-date">開催：2026年11月21日(土)</div>'
                         '<div class="event-area">場所：東京都</div>')
    assert lm['9']['area'] == '東京都' and lm['9']['play_date'] == '2026年11月21日(土)', lm
    assert lm['9']['status_tag'] == 'あと64日', lm
    # 🚨券種の書き方B（複数日・複数枠もの）＝名前・値段・公演日時が span で入る形
    htmlB = ('<div class="pg-event__ordering__program">'
             '<div class="c-ordering-btn is-available ">'
             '<div class="c-ordering-btn__content-main-event__name">'
             "<span class='c-ordering-ticket-name'>AAA. 個人協賛</span><br>"
             "<span class='c-ordering-ticket-date'> 2027年03月07日(日) 10:00開場 </span> <br>"
             '<span class="c-ordering-ticket-price">110円</span></div>'
             '<div class="c-ordering-btn__content__status"><span>事前支払い</span></div>'
             '<div class="purchase-period"><div class="purchase-period__label">カード決済</div>'
             '<div class="purchase-period__value">:2026.04.27 03:48 ~ 2027.03.07 14:00</div></div>'
             '</div></div><div class="pg-event__ordering__caption">')
    dB = parse_event(htmlB, '1')
    assert len(dB['programs']) == 1, dB['programs']
    tB = dB['programs'][0]['tickets'][0]
    assert tB['name'] == 'AAA. 個人協賛' and tB['price'] == 110, tB
    assert dB['programs'][0]['date'] == '2027-03-07', dB['programs'][0]
    assert tB['periods'][0]['parsed'][2] == '2027-03-07', tB['periods']
    print('selftest OK: parse_jp_date/parse_period/pref_of/parse_list_page/parse_list_meta/券種B形')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cats', default='81,84')
    ap.add_argument('--out', default='tmp/tiget_harvest.json')
    ap.add_argument('--sleep', type=float, default=1.0)
    ap.add_argument('--limit', type=int, default=0)
    # 🆕毎朝のスイープ用＝一覧は新着順なので「登録済みばかりのページ」に当たったら止める。
    #   これで1カテゴリ1〜3ページ（全部で数十件）で済む。0 を渡すと従来どおり最後のページまで。
    ap.add_argument('--stop-known', type=int, default=0,
                    help='登録済みだけのページがこの回数続いたら、そのカテゴリを打ち切る（毎朝用は 1）')
    ap.add_argument('--index', default='index.html', help='登録済みidを読むファイル')
    a = ap.parse_args([x for x in sys.argv[1:] if x != '--selftest'])

    known = set()
    if a.stop_known:
        try:
            known = set(re.findall(r'tiget\.net/events/(\d+)',
                                   io.open(a.index, encoding='utf-8', newline='').read()))
            print(f'  登録済みのTIGETイベント {len(known)}件（新着順で追い越したら打ち切る）')
        except Exception as e:
            print(f'  ⚠️登録済みidが読めなかった（打ち切りなしで回す）: {str(e)[:60]}')
            known = set()

    events, order = {}, []
    for cat in a.cats.split(','):
        page, last = 1, 1
        allknown = 0
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
            fresh = [i for i in ids if i not in known]
            print(f'  一覧 cat={cat}({CAT_NAME.get(cat, cat)}) page={page}/{last} … {len(ids)}件'
                  f'（未登録{len(fresh)}件）/ 累計{len(order)}件')
            page += 1
            time.sleep(a.sleep)
            if a.stop_known and ids:
                allknown = allknown + 1 if not fresh else 0
                if allknown >= a.stop_known:
                    print(f'  → 登録済みだけのページが{allknown}枚続いたので cat={cat} は打ち切り')
                    break

    rows, errs = [], []
    # 打ち切りモードでは、個別ページを引くのも**未登録の分だけ**（毎朝の負荷を軽くする）
    if a.stop_known and known:
        skipped_known = [i for i in order if i in known]
        order = [i for i in order if i not in known]
        print(f'  登録済み {len(skipped_known)}件は個別ページを引かない / これから引く {len(order)}件')
    todo = order[:a.limit] if a.limit else order
    for n, eid in enumerate(todo, 1):
        try:
            d = parse_event(fetch(f'{BASE}/events/{eid}'), eid)
            d['cats'] = events[eid]['cats']
            d['cat_names'] = [CAT_NAME.get(c, c) for c in d['cats']]
            d['list'] = events[eid].get('list') or {}
            # 県は「一覧の 場所：」が正（TIGET自身が持っている値）。無いときだけ会場名/JSON-LDから
            d['prefecture'] = pref_of(d['list'].get('area') or '') or d['prefecture']
            # 公演日が読めなかった塊は、一覧の「開催：」で埋める（最後の控え）
            lpd = parse_jp_date(d['list'].get('play_date') or '')
            if lpd:
                d['detail_date'] = d.get('detail_date') or lpd
                for p in d['programs']:
                    if not p.get('date'):
                        p['date'] = lpd
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
