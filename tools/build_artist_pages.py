#!/usr/bin/env python3
"""アーティストごとの軽い静的ページ artist/<番号>.html と一覧 artists.html を作る（2026-10-09 ユーザー決定「2番でいきましょう」）。

Why: OSHINAVI の中身は index.html の EVENTS（JS）にあり、検索エンジンから
「◯◯ チケット 発売日」で来る入口が無い。1組1ページの軽いHTMLを置いて検索の入口にする。
ページは JS なし・その組の「これから買える／発売前の枠」だけを発売日順に並べ、
売り場への直リンクと OSHINAVI の検索（/?q=名前）へのリンクを置く。

判定は build_ai_page.py の関数（index.html の表示ルールと揃えたもの）をそのまま使う。
URL の番号は tools/artist_pages.json に名前ごとに固定する（作り直しても同じ名前は同じURL）。

使い方:
  python tools/build_artist_pages.py               # 作る（sitemap.xml にも足す）
  python tools/build_artist_pages.py --today 2026-10-09
build_ai_page.py の最後から呼ばれる（sitemap.xml を作り直した後に足すため）。
"""
import argparse
import html
import json
import os
import re
import unicodedata
from collections import defaultdict
from datetime import date, datetime, timedelta
from urllib.parse import quote

import build_ai_page as A
import click_track

REG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "artist_pages.json")
OUT_DIR = "artist"
MAX_PAGES = 20000        # 人気の組から（これから買える・発売前の枠が多い順）。10/13 500→5000→20000（買える枠のある名前は全部＝13,188組・ユーザー「とにかく早く目標を達成して」。sitemap の上限5万URLの内）
MIN_ROWS = 1
POP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "artist_popularity.json")  # collect_followers.py
# 名前として使わない（出演者の総称・告知文・催しや会場の名前が artist 欄に入っているもの）
SKIP_NAME = re.compile(r"出演者多数|芸人多数|多数|ほか$|他$|^未定$|^TBA$|^ゲスト|^各|^\s*$|ご確認|公式HP|お知らせ"
                       r"|TOUR|ツアー|公演|ライブ|LIVE|イベント|発売記念|展$|展覧|ミュージアム|CAFE|カフェ|寄席|繁昌亭|館$"
                       r"|劇場|巡業|フェス|FES|祭|コンサート|CONCERT|ミュージカル|『|「|〜|~|in |IN |\d{4}"
                       # 10/13 5000組に広げたら切れ端が名前になった（「16(Fri)】 …」「【…】…」「ADAM at」）
                       r"|【|】|\[|\]|\(|\)|（|）|^[\d\W_]|\s(?:at|and|with|feat\.?|vs\.?|x|×)$|^(?:at|with|feat)\s"
                       # 🆕10/27 抜き打ち（すちこ「A」のゲート）＝「愛はズボーンPresents」「第65回全日本女子剣道選手権大会」
                       # （大文字小文字を区別しないのはこの「presents」だけ＝全体に re.I を付けると FES が Professor に当たる）
                       r"|(?i:presents?)$|プレゼンツ$|^第\d+回|大会$|選手権|リーグ|杯$|定期演奏会|演奏会$|独演会|リサイタル|落語会|発表会")


def norm(s):
    return unicodedata.normalize("NFKC", s or "").replace(" ", "").replace("　", "").lower()


# トップのジャンルの名前（index.html の GENRE_LABEL と同じ言葉）＋総称＝出演者の名前にしない
GENRE_WORDS = {w.lower() for w in (
    "2.5次元 HIP HOP J-POP K-POP TikToker VTuber YouTuber 新着 お笑い その他 アイドル アニソン イベント イベントアート キッズ "
    "クラシック クラブ/DJ グルメ サーカス シャンソン ジャズ スポーツ ダンス ディナーショー トークショー ファンイベント フェス ボカロ "
    "マジック ミュージカル ロック 伝統 声優 学園祭 怪談 映画 歌い手 洋楽 演劇 演歌 童謡・唱歌 舞台挨拶 花火大会 配信 駐車場 "
    "落語 漫才 コント 講談 浪曲 寄席 音楽 芸人").split()} | {"hip hop"}


# 一覧の行（10/27）＝かなの行 → A〜Z → 数字・記号 → 漢字（読みが付くまでは漢字で始まる名前をまとめる）
KANA_ROWS = ["あ", "か", "さ", "た", "な", "は", "ま", "や", "ら", "わ"]
_KANA_HEAD = {r: r for r in KANA_ROWS}
for _r, _cs in (("あ", "あいうえおぁぃぅぇぉゔ"), ("か", "かきくけこ"), ("さ", "さしすせそ"), ("た", "たちつてとっ"), ("な", "なにぬねの"),
                ("は", "はひふへほ"), ("ま", "まみむめも"), ("や", "やゆよゃゅょ"), ("ら", "らりるれろ"), ("わ", "わをんゎゐゑ")):
    for _c in _cs:
        _KANA_HEAD[_c] = _r
ROWS = KANA_ROWS + [chr(c) for c in range(ord("a"), ord("z") + 1)] + ["0-9"]   # 10/27 漢字の行は無し＝読みで あ〜わ へ
ROW_LABEL = {chr(c): chr(c).upper() for c in range(ord("a"), ord("z") + 1)}
ROW_LABEL.update({"0-9": "0-9・記号"})
ROW_ID = {r: r for r in ROWS}
ROW_ID.update({"あ": "a1", "か": "ka", "さ": "sa", "た": "ta", "な": "na", "は": "ha", "ま": "ma", "や": "ya", "ら": "ra", "わ": "wa",
               "0-9": "num", "漢字": "kanji"})
ROW_ID.update({chr(c): "e" + chr(c) for c in range(ord("a"), ord("z") + 1)})


_KKS = None
YOMI_FIX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "artist_yomi.json")   # 読み違いの手直し {名前: よみ}
try:
    _YOMI = json.load(open(YOMI_FIX, encoding="utf-8"))
except FileNotFoundError:
    _YOMI = {}


def yomi(t):
    """漢字の入った名前に読み（ひらがな）を付ける（🆕10/27 すちこ「読みであかさたなに入れられる？　漢字は無し」＝pykakasi）。
    芸名は読み違えることがある＝ tools/artist_yomi.json で手直し"""
    global _KKS
    if t in _YOMI:
        return _YOMI[t]
    t = t.replace("髙", "高").replace("﨑", "崎").replace("德", "徳")   # 辞書に無い異体字（髙田→たかだ）
    if not re.search(r"[一-鿿㐀-䶿々〆]", t):
        return t
    if _KKS is None:
        import pykakasi
        _KKS = pykakasi.kakasi()
    _YOMI[t] = "".join(x["hira"] for x in _KKS.convert(t))   # 同じ名前は1回だけ読む
    return _YOMI[t]


def kana_key(s):
    """カタカナ→ひらがな・濁点を外した読みの並び（ガ→か・パ→は）・漢字は読みに"""
    t = norm(s)
    t = t.lstrip("「『【〔［[（(\"'・")   # 作品名の『』は外して並べる（『ハイキュー!!』→ は行）
    t = yomi(t)
    t = "".join(chr(ord(c) - 96) if "ァ" <= c <= "ヶ" else c for c in t)
    return unicodedata.normalize("NFC", "".join(c for c in unicodedata.normalize("NFD", t) if c not in "゙゚"))


def row_of(name):
    c = kana_key(name)[:1]
    if c in _KANA_HEAD:
        return _KANA_HEAD[c]
    if "a" <= c <= "z":
        return c
    return "0-9"


def esc(s):
    return html.escape(str(s)) if s is not None else ""


ROLE_PAREN = re.compile(
    r"\s*\((?:[^()]*(?:ソプラノ|アルト|テノール|テナー|バリトン|バス|メゾ|ピアノ|オルガン|チェンバロ|ヴァイオリン|バイオリン|ヴィオラ|チェロ|コントラバス|"
    r"フルート|クラリネット|オーボエ|ファゴット|サックス|トランペット|トロンボーン|ホルン|ハープ|ギター|ベース|ドラム|パーカッション|打楽器|三味線|尺八|箏|琴|太鼓|"
    r"指揮|作曲|編曲|演出|司会|ナレーション|ナビゲーター|語り|お話|朗読|ゲスト|映像出演|声の出演|特別出演|公演|回|日)[^()]*"
    r"|(?i:vn|vl|va|vc|cb|pf|p|fl|cl|ob|fg|sax|as|ts|bs|tp|tb|hr|hp|g|gt|b|ba|ds|dr|perc|key|kb|vo|cho|recd?|cmb|cemb|org|sop|ten|bar|mc|cond|vn\.|pf\.)\.?)\)\s*$")


def artist_names(ev):
    """エントリの artist を名前に分ける（「A／B」は両方の組のページに載せる）。"""
    a = unicodedata.normalize("NFKC", ev.get("artist") or "").strip()
    if not a:
        return []
    # NFKC で「／」は「/」になる。「AC/DC」のような名前（両側が英字1〜3文字）は割らない
    if re.fullmatch(r"[A-Za-z]{1,3}/[A-Za-z]{1,3}", a):
        parts = [a]
    else:
        parts = [p.strip() for p in a.split("/") if p.strip()]
    if len(parts) > 6:      # 大人数の催しは名前ページにしない
        return []
    # 「aiko Live Tour」のように名前のあとにツアー名が続く形は、前の名前だけを使う
    parts = [re.split(r"\s+(?:LIVE|Live|live|TOUR|Tour|tour|ツアー|CONCERT|Concert|コンサート|ONE ?MAN|ワンマン)\b", p)[0].strip()
             for p in parts]
    # 🆕10/27 ぴあ［出演］の「岡村明美(ナレーション)」「大平倍大(テノール)」＝役・楽器の括弧は名前に入れない
    parts = [ROLE_PAREN.sub("", p).strip() for p in parts]
    # 🆕10/27 すちこ「お笑いを選択…1件」＝「ガクヅケ／お笑い」の「お笑い」が名前ページになっていた＝ジャンルの名前は名前にしない
    #   （公演名そのものが同じ名前＝グループの「サーカス」は残す）
    nm = unicodedata.normalize("NFKC", ev.get("name") or "").strip()
    return [p for p in parts if len(p) >= 2 and not SKIP_NAME.search(p) and not re.search(r"(?i)live|tour", p) and len(p) <= 40
            and not (p.lower() in GENRE_WORDS and p != nm)]


# 🆕2026-10-18 すちこ「ファインディング ネバーランドで検索かけた時、oshinavi が出てくるってこと？」＝出なかった。
#   SKIP_NAME が「ミュージカル」「『」を名前から外すので、作品名で探される公演（ミュージカル・バレエ・第九…）に
#   ページが無かった（買える枠のあるエントリ 5,106件が漏れ）。名前ページが作れないエントリだけ、『』「」の作品名でページを作る。
WORK_BR = re.compile(r"[『「]([^』」]{2,40})[』」]")
# 作品名として弱い言葉（季節・一般語）＝1つのページに別々の催しが混ざるだけ
WORK_SKIP = re.compile(r"^(?:クリスマス|冬祭り\d*|夏祭り\d*|オフ会|color|RUSH|ONE|LIVE|SHOW|Xmas)$|多数|ほか$|他$|公式|お知らせ|ご確認", re.I)


_GF_OK = None


def cast_ok(ev):
    """出演者の欄が売り場の出演者から来ている（公演名のままではない）＝gate_fields M と同じ見方"""
    global _GF_OK
    import gate_fields as GF
    if _GF_OK is None:
        _GF_OK = (GF._artist_ok(), GF._artist_nocast())
    ok, nocast = _GF_OK
    # 売り場に出演者の記載が無かった（artist_nocast＝公演名のままで正しい）エントリも、名前ページにはしない
    if str(ev.get("id")) in nocast:
        return False
    return not GF.artist_looks_like_title(ev, ok)


def title_like_name(nm, ev):
    """名前が公演名そのもの（長い・空白入り）＝「あばれる君 熱血授業in掛川」「◯◯対◯◯ 明治安田J2リーグ」。
    出演者の欄に公演名が入ったまま番人（gate_fields M）の言葉に当たらなかった形＝確実ではないので名前ページにしない
    （本当のグループ名なら tools/artist_ok.txt に書けば出る）"""
    import gate_fields as GF
    if _GF_OK is None:
        cast_ok(ev)
    t = unicodedata.normalize("NFKC", nm).strip()
    return (t == unicodedata.normalize("NFKC", ev.get("name") or "").strip() and len(t) >= 12 and " " in t
            and nm not in _GF_OK[0])


CASTCHECK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "artist_castcheck.json")   # refetch_artist が書く
_CC = None


def only_title_source(nm, evs):
    """元のエントリが全部「公演名＝名前」で、どれも売り場の出演者の欄で確かめていない（artist_castcheck に無い）＝確実ではない。
    作品名のページ（『』）と人が書いた名前（artist_ok.txt）は対象外"""
    global _CC
    if nm.startswith("『") or nm.startswith("ミュージカル『"):
        return False
    if _GF_OK is None and evs:
        cast_ok(evs[0])
    if nm in _GF_OK[0]:
        return False
    if _CC is None:
        try:
            _CC = json.load(open(CASTCHECK, encoding="utf-8"))
        except FileNotFoundError:
            _CC = {}
    t = unicodedata.normalize("NFKC", nm).strip()
    if not evs or not all(unicodedata.normalize("NFKC", ev.get("name") or "").strip() == t for ev in evs):
        return False
    return not any(t in unicodedata.normalize("NFKC", (_CC.get(str(ev.get("id"))) or {}).get("cast", "")) for ev in evs)


def work_names(ev):
    """名前ページが作れないエントリの作品名（「ミュージカル『◯◯』」「『◯◯』」）。"""
    src = unicodedata.normalize("NFKC", (ev.get("artist") or "") + " " + (ev.get("name") or ""))
    m = WORK_BR.search(src)
    if not m:
        return []
    t = m.group(1).strip()
    if len(t) < 2 or WORK_SKIP.search(t):
        return []
    return [("ミュージカル" if "ミュージカル" in src else "") + f"『{t}』"]


def ticket_rows(ev, today):
    """これから発売・販売中の枠（売り切れ・終わった枠は出さない）。"""
    out = []
    for t in ev.get("tickets") or []:
        if t.get("soldout"):
            continue
        sd, d = t.get("startDate"), t.get("date")
        try:
            if sd and A.parse(sd) >= today:
                key, state = sd, "発売前"
            elif d and A.parse(d) >= today:
                key, state = d, "販売中"
            else:
                continue
        except ValueError:
            continue
        out.append((key, state, t))
    return out


def fmt_md(iso):
    try:
        d = date.fromisoformat(iso)
    except (TypeError, ValueError):
        return ""
    return f"{d.month}/{d.day}({'月火水木金土日'[d.weekday()]})"


def state_text(state, t, today):
    # 静的ページは1日3回しか作り直さない＝「本日」「明日」は日付が変わると嘘になる。日付だけで書く
    sd, d = t.get("startDate"), t.get("date")
    if state == "発売前":
        when = f"{fmt_md(sd)}発売"
        if d and d != sd and not t.get("saleEndUnknown"):
            return f"{when}（〜{fmt_md(d)}）"
        return when
    if t.get("saleUntilSoldOut"):
        return "販売中（予定枚数に達し次第終了）"
    if t.get("saleEndUnknown"):
        return f"{fmt_md(sd)}〜発売中" if sd else "販売中"
    return f"販売中（〜{fmt_md(d)}）"


def vendor_of(url):
    u = url or ""
    for k, name in [("rakuten", "楽天チケット"), ("pia.jp", "チケットぴあ"), ("eplus", "e+"), ("l-tike", "ローチケ"),
                    ("tiget", "TIGET"), ("fany", "FANY"), ("zaiko", "ZAIKO"), ("livepocket", "livePocket")]:
        if k in u:
            return name
    return "売り場"


def cta(q, name, pic=False):
    """OSHINAVI へ戻るボタン（文言はそのまま・形は 10/28 すちこの絵の真ん中）
    pic=True＝10/28 すちこのキャラ入りボタンの絵（img/btn_oshinavi_matsuko.png・白い背景は抜いた）"""
    if pic:
        return (f'<a class="ctp" href="{q}"><img src="../img/btn_oshinavi_matsuko.png" width="360" height="183" '
                f'alt="OSHINAVIで「{esc(name)}」を見る"></a>')
    return (f'<a class="cta" href="{q}"><span class="o"><span class="i"><span class="t"><b>OSHINAVI</b>で「{esc(name)}」を見る</span>'
            '<span class="c" aria-hidden="true">≫</span></span></span></a>')


CSS = ("body{font-family:sans-serif;max-width:860px;margin:0 auto;padding:16px;line-height:1.6;color:#1a1a1a;background:#fff}"
       "h1{font-size:22px;margin:8px 0}h2{font-size:17px;margin:20px 0 6px;border-left:4px solid #e4007f;padding-left:8px}"
       ".note{color:#555;font-size:13px}"
       # 🆕10/28 すちこ「色がピンクなのがいや」「この真ん中のボタンを使って」＝角を切った紺の枠・水色に光る縁と ≫（絵は CSS で描く）
       ".cta{display:inline-block;max-width:100%;margin:12px 0;text-decoration:none;filter:drop-shadow(0 0 6px rgba(41,211,255,.6))}"
       ".cta .o,.cta .i{clip-path:polygon(12px 0,calc(100% - 12px) 0,100% 12px,100% calc(100% - 12px),calc(100% - 12px) 100%,12px 100%,0 calc(100% - 12px),0 12px)}"
       ".cta .o{display:block;padding:2px;background:linear-gradient(90deg,#29d3ff,#3a6bff 55%,#29d3ff)}"
       ".cta .i{position:relative;display:flex;align-items:center;gap:14px;padding:12px 20px 14px;"
       "background:linear-gradient(180deg,#0d2a78,#061650 60%,#0a2266);color:#fff;font-weight:bold;font-size:16px;line-height:1.4}"
       ".cta .i:before{content:'';position:absolute;top:5px;left:16px;width:22px;height:4px;"
       "background:repeating-linear-gradient(115deg,#29d3ff 0 3px,transparent 3px 7px)}"
       ".cta .i:after{content:'';position:absolute;bottom:5px;left:18%;width:45%;height:2px;"
       "background:linear-gradient(90deg,transparent,#29d3ff 30%,#29d3ff 75%,#d03cff 80%,#d03cff 92%,transparent)}"
       ".ctp{display:inline-block;margin:6px 0;max-width:100%}.ctp img{display:block;width:360px;max-width:100%;height:auto}"
       ".cta .t{min-width:0}.cta b{font-style:italic;font-weight:900;letter-spacing:.5px;text-shadow:0 0 6px rgba(127,230,255,.8)}"
       ".cta .c{flex:none;margin-left:auto;color:#5fe0ff;font-size:28px;line-height:1;font-weight:900;"
       "text-shadow:0 0 8px #29d3ff}.ev{border:1px solid #ddd;border-radius:8px;padding:10px 12px;margin:10px 0}"
       ".ev .n{font-weight:bold}.ev .v{color:#444;font-size:14px}ul{padding-left:18px;margin:6px 0}li{margin:4px 0;font-size:14px}"
       ".st{font-weight:bold;color:#c00}.pre{color:#0a58ca}a{color:#06c;word-break:break-all}"
       ".btns{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0}.ab{display:inline-block;text-decoration:none;font-size:13px;font-weight:bold}"
       ".ab:not(.ai){padding:7px 14px;border-radius:8px;background:#ff9900;color:#111}.ab.ai img{height:36px;display:block}"
       "@media (prefers-color-scheme: dark){body{background:#111;color:#eee}.ev{border-color:#444}.ev .v,.note{color:#bbb}a{color:#6af}}")


GTAG = ('<script async src="https://www.googletagmanager.com/gtag/js?id=G-RM1EQ5M4HT"></script>'
        "<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}"
        "gtag('js',new Date());gtag('config','G-RM1EQ5M4HT');</script>")
CLICK = click_track.snippet("artist")   # 🆕10/27 ボタンのクリックを GA4 へ（tools/click_track.py）

# 🆕2026-10-27 すちこ「①と②からお願い」＝検索から来る人が最初に着くアーティストのページに、トップのカードと同じ
#   アフィリのボタン（楽天チケット・最新CD/ジャンルのグッズ・会場近くのホテル）を付ける。それまで1つも無かった。
#   文言と画像は index.html の BTN_IMG・GENRE_AMAZON_LINKS・hotelHref と同じもの（画面の決まりを変えない）。
AMZ_TAG = "oshinavi0a-22"
HOTEL_VC = "https://ck.jp.ap.valuecommerce.com/servlet/referral?sid=3769972&pid=892633446"
BTN_IMG = {"楽天チケット": "img/btn2_rakuten.png", "予習する（最新CD）": "img/btn_cd_0915.png",
           "会場近くのホテルを探す": "img/btn2_hotel.png", "推しうちわを作る": "img/btn2_uchiwa.png",
           "推し活グッズ": "img/btn2_goods.png", "ライブ用耳栓": "img/btn2_earplug.png", "オペラグラス": "img/btn2_operaglass.png",
           "観戦グッズ": "img/btn2_kansen.png", "フェスの必需品": "img/btn2_fes.png", "花火の必需品": "img/btn2_hanabi.png",
           "ぬりえ": "img/btn2_nurie.png"}
_CONCERT = ("https://amzn.to/3OnUo4K", "推し活グッズ")
_UCHIWA = ("https://www.amazon.co.jp/s?k=%E5%BF%9C%E6%8F%B4%E3%81%86%E3%81%A1%E3%82%8F%20%E6%89%8B%E4%BD%9C%E3%82%8A%20%E3%82%BB%E3%83%83%E3%83%88&tag=oshinavi0a-22", "推しうちわを作る")
_OPERA = ("https://amzn.to/47ZHLUm", "オペラグラス")
GENRE_AMAZON = {"fes": ("https://amzn.to/4uprRe4", "フェスの必需品"),
                "hanabi": ("https://www.amazon.co.jp/s?k=%E8%8A%B1%E7%81%AB%E5%A4%A7%E4%BC%9A%20%E6%8C%81%E3%81%A1%E7%89%A9&tag=oshinavi0a-22", "花火の必需品"),
                "engeki": _OPERA, "musical": _OPERA, "classic": _OPERA, "rock": ("https://amzn.to/48LOZM1", "ライブ用耳栓"),
                "hiphop": _CONCERT, "anime": _CONCERT, "chanson": _CONCERT, "musicetc": _CONCERT,
                "kids": ("https://amzn.to/4qTnpV0", "ぬりえ")}
for _g in ("jpop", "kpop", "jazz", "yougaku", "enka", "utaite", "vocaloid", "club", "hougaku", "idol", "youtuber", "vtuber",
           "tiktoker", "owarai", "seiyuu", "2.5ji", "fanevent"):
    GENRE_AMAZON[_g] = _UCHIWA
BASEBALL_RE = re.compile(r"タイガース|ドラゴンズ|スワローズ|ファイターズ|バファローズ|マリーンズ|ジャイアンツ|カープ|ホークス|ライオンズ|イーグルス|ベイスターズ|NPB|プロ野球|野球")
# 最新CDを名前の検索で作ってよいジャンル（reference_amazon_affiliate の付与対象・クラシックは名前だけで探す）
CD_GENRES = {"jpop", "rock", "idol", "kpop", "hiphop", "classic", "anime", "seiyuu", "vtuber", "youtuber", "enka", "jazz"}


def rakuten_deep(url):
    """楽天チケットの素URLは LinkShare の Deep Link に（feedback_rakuten_deeplink）。"""
    if url and url.startswith("https://ticket.rakuten.co.jp/") and "linksynergy" not in url:
        return f"https://click.linksynergy.com/deeplink?id=z9x6HLNpWco&mid=53531&murl={quote(url, safe='')}"
    return url


def btn(url, label, icon, nofollow=False):
    img = BTN_IMG.get(label)
    inner = (f'<img src="../{img}" alt="{esc(label)}" loading="lazy" decoding="async">' if img else f"{icon} {esc(label)}")
    rel = "nofollow noopener" if nofollow else "noopener"
    return f'<a class="ab{" ai" if img else ""}" href="{esc(url)}" target="_blank" rel="{rel}">{inner}</a>'


def genre_amazon(ev):
    g = ev.get("genre")
    if g == "sports":
        return (("https://amzn.to/4cjW1IR" if BASEBALL_RE.search((ev.get("name") or "") + (ev.get("artist") or ""))
                 else "https://amzn.to/4vqJXOw"), "観戦グッズ")
    return GENRE_AMAZON.get(g)


def cd_url(name, items):
    """そのアーティストの最新CD。エントリに付いている links.amazon（人が選んだリンク）を先に、無ければ名前の検索。"""
    for _, ev, _ in items:
        u = (ev.get("links") or {}).get("amazon")
        if u and not (ev.get("links") or {}).get("amazonLabel"):
            return u
    if "『" in name or not any(ev.get("genre") in CD_GENRES for _, ev, _ in items):
        return None
    cls = all(ev.get("genre") == "classic" for _, ev, _ in items)
    k = name if cls else f"{name} CD"
    return f"https://www.amazon.co.jp/s?k={quote(k)}&i=specialty-aps&srs=26200021051&tag={AMZ_TAG}"


def hotel_url(ev, today):
    """index.html の hotelHref と同じ＝会場が1つのカードだけ会場名＋県（1日だけの公演は日付も）で Expedia の宿の検索へ。"""
    v = (ev.get("venue") or "").strip()
    if not v or re.search(r"全国ツアー|／|/|、|配信|オンライン|Zaiko Live|Streaming|未定|各地", v, re.I):
        return HOTEL_VC
    dest = re.sub(r"[（(][^）)]*[）)]\s*$", "", v).strip()
    if not dest:
        return HOTEL_VC
    pref = (ev.get("prefecture") or "").strip()
    if pref and not re.search(r"・|全国|海外|、", pref) and pref not in dest:
        dest += " " + pref
    q = "destination=" + quote(dest)
    days = set(re.findall(r"\d{1,2}月\d{1,2}日", ev.get("dateLabel") or ""))
    d = ev.get("date") or ""
    if len(days) == 1 and re.fullmatch(r"\d{4}-\d{2}-\d{2}", d) and d >= today.isoformat():
        q += f"&startDate={d}&endDate={(date.fromisoformat(d) + timedelta(days=1)).isoformat()}"
    return HOTEL_VC + "&vc_url=" + quote("https://www.expedia.co.jp/Hotel-Search?" + q + "&adults=2", safe="")


def event_jsonld(ev, rows):
    """Google の「イベント」枠に出すための構造化データ（schema.org Event）。2026-10-13 追加。
    🚨嘘を書かない＝公演日が1日・会場が1つと読めるエントリだけ出す（ツアー・会期・複数会場は出さない）。"""
    held = ev.get("dateLabel") or ""
    venue = (ev.get("venue") or "").strip()
    pref = (ev.get("prefecture") or "").strip()
    d = ev.get("date") or ""
    if not (re.fullmatch(r"\d{4}-\d{2}-\d{2}", d) and venue and pref):
        return None
    if re.search(r"〜|～|~|全国|ツアー|TOUR|／|・|複数|未定|設定中|オンライン|配信", held + venue + pref):
        return None
    m = re.search(r"(\d{1,2}):(\d{2})\s*開演", held)
    start = f"{d}T{int(m.group(1)):02d}:{m.group(2)}:00+09:00" if m else d
    url = next((t.get("url") for _, _, t in rows if t.get("url")), None) or A.buy_url(ev)[0]
    j = {"@context": "https://schema.org", "@type": "Event", "name": ev.get("name") or "",
         "startDate": start, "eventStatus": "https://schema.org/EventScheduled",
         "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
         "location": {"@type": "Place", "name": venue,
                      "address": {"@type": "PostalAddress", "addressRegion": pref, "addressCountry": "JP"}}}
    if ev.get("artist"):
        j["performer"] = {"@type": "PerformingGroup", "name": ev["artist"]}
    if url:
        sd = min((t.get("startDate") for _, _, t in rows if t.get("startDate")), default=None)
        off = {"@type": "Offer", "url": url, "availability": "https://schema.org/InStock"}
        if sd:
            off["validFrom"] = sd
        j["offers"] = off
    return json.dumps(j, ensure_ascii=False).replace("</", "<\\/")


def page_html(name, items, today, stamp, total_rows, num=None):
    # 検索結果で押されるように、次の発売日をタイトルと説明文に出す（2026-10-17 90日計画 A-3）
    nxt = min(((t.get("startDate"), t.get("type") or "") for _, _, rows in items for _, st, t in rows
               if st == "発売前" and t.get("startDate")), default=None)
    nxt_md = fmt_md(nxt[0]) if nxt else ""
    title = (f"{name} チケット発売日・先行・一般発売まとめ（次は{nxt_md}発売）| OSHINAVI" if nxt_md
             else f"{name} チケット発売日・先行・一般発売まとめ | OSHINAVI")
    first = items[0][0] if items else None
    desc = (f"{name}のチケット情報（{today.month}/{today.day}更新）。"
            + (f"次の発売は{nxt_md}「{nxt[1][:40]}」。" if nxt_md else "")
            + f"これから発売・販売中の受付{total_rows}件を発売日順に。先行・一般発売の日付と売り場へのリンクをまとめています。")
    # 作品ページ（「ミュージカル『◯◯』」）は作品名だけで探す＝「第九」「『第九』」どちらの書き方の公演も出る
    qname = re.sub(r"^ミュージカル|[『』]", "", name) if "『" in name else name
    q = html.escape(f"https://oshinavi.jp/?q={qname}", quote=True)
    o = ["<!DOCTYPE html>", '<html lang="ja"><head>', '<meta charset="UTF-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
         '<meta name="robots" content="index,follow">',
         f"<title>{esc(title)}</title>", f'<meta name="description" content="{esc(desc)}">']
    if num is not None:
        can = f"https://oshinavi.jp/{OUT_DIR}/{num}.html"
        o += [f'<link rel="canonical" href="{can}">', '<meta property="og:type" content="website">',
              f'<meta property="og:title" content="{esc(title)}">', f'<meta property="og:description" content="{esc(desc)}">',
              f'<meta property="og:url" content="{can}">', '<meta property="og:image" content="https://oshinavi.jp/og-image.png">']
    for _, ev, rows in items:
        j = event_jsonld(ev, rows)
        if j:
            o.append(f'<script type="application/ld+json">{j}</script>')
    top_btns = []
    cu = cd_url(name, items)
    if cu:
        top_btns.append(btn(cu, "予習する（最新CD）", "🎧"))
    ga = next((genre_amazon(ev) for _, ev, _ in items if genre_amazon(ev)), None)
    if ga:
        top_btns.append(btn(ga[0], ga[1], "🛍"))
    o += [GTAG, CLICK, f"<style>{CSS}</style></head><body>",
         # 🆕10/24 リンクは相対に（すちこ「ファイルが出てこないわよ」＝file:// で開くと /artists.html が C:\ を探す）
         '<p class="note"><a href="../index.html">OSHINAVI</a> ＞ <a href="../artists.html">アーティスト一覧</a></p>',
         f"<h1>{esc(name)} のチケット発売日</h1>",
         *([f'<p class="pre"><b>次の発売：{esc(nxt_md)}</b> {esc(nxt[1])}</p>'] if nxt_md else []),
         f'<p class="note">最終更新：{esc(stamp)}／これから発売・販売中の受付 {total_rows}件（発売日・締切が近い順）。'
         f'日付は各売り場の掲載にもとづきます。買う前に売り場のページで必ず確かめてください。</p>',
         cta(q, name, pic=True),
         *([f'<div class="btns">{"".join(top_btns)}</div>'] if top_btns else [])]
    for _, ev, rows in items:
        o.append('<div class="ev">')
        o.append(f'<div class="n">{esc(ev.get("name") or "")}</div>')
        venue = ev.get("venue") or ""
        pref = ev.get("prefecture") or ""
        held = ev.get("dateLabel") or ev.get("date") or ""
        o.append(f'<div class="v">{esc(venue)}{("（" + esc(pref) + "）") if pref else ""}／公演 {esc(held)}</div><ul>')
        for key, state, t in rows:
            cls = "pre" if state == "発売前" else "st"
            url = rakuten_deep(t.get("url") or A.buy_url(ev)[0])
            link = f' <a href="{esc(url)}" target="_blank" rel="noopener">{esc(vendor_of(url))}</a>' if url else ""
            o.append(f'<li><span class="{cls}">{esc(state_text(state, t, today))}</span> {esc(t.get("type") or "")}{link}</li>')
        o.append("</ul>")
        eb = []
        rk = rakuten_deep((ev.get("links") or {}).get("rakuten"))
        if rk:
            eb.append(btn(rk, "楽天チケット", "🎫"))
        eb.append(btn(hotel_url(ev, today), "会場近くのホテルを探す", "🏨", nofollow=True))
        o.append(f'<div class="btns">{"".join(eb)}</div></div>')
    o.append(cta(q, name))
    o.append('<p class="note"><a href="../artists.html">ほかのアーティストを見る</a>｜<a href="../index.html">OSHINAVI トップ</a></p>')
    o.append("</body></html>")
    return "\n".join(o)


def build(today):
    _n = datetime.now()
    stamp = f"{today.year}年{today.month}月{today.day}日 {_n:%H:%M}"
    events = [e for e in A.extract_events_array("index.html") if e.get("verified") is True and e.get("genre") != "new"]

    by = defaultdict(lambda: {"name": None, "items": []})
    for ev in events:
        rows = ticket_rows(ev, today)
        if not rows:
            continue
        rows.sort(key=lambda r: r[0])
        # 🆕🚨10/27 すちこ「確実じゃなきゃ載せるべきじゃない　もし載せるなら、完璧なゲートをちゃんと作らなきゃ」→「A」
        #   名前ページは「売り場の出演者の欄から取れた名前」だけ＝出演者の欄が公演名のまま（gate_fields M）のエントリからは作らない
        #   （「怪談和尚・三木大雲の怪談説法」「柳家喬太郎 独演会」が名前になっていた）。作品名（『』）のページはそのまま
        for nm in [n for n in (artist_names(ev) if cast_ok(ev) else []) if not title_like_name(n, ev)] or work_names(ev):
            k = norm(nm)
            if not k:
                continue
            g = by[k]
            g["name"] = g["name"] or nm
            g["items"].append((rows[0][0], ev, rows))

    # 🆕🚨10/27 「公演名＝名前」しか元が無い組（ほかの公演に出演者として出てこない）は、売り場の出演者の欄で確かめた分だけ
    #   （抜き打ちで「SONIC BOOM」＝クラブの催しの名前か出演者か確かめられなかった／「大阪個人撮影会」「風間杜夫ひとり芝居」が混ざる）
    for k in [k for k, g in by.items() if only_title_source(g["name"], [ev for _, ev, _ in g["items"]])]:
        del by[k]

    # 人気の組から＝X投稿の準備で調べたフォロワー数（エントリ単位）の最大値 → 受付の数
    try:
        pop = {int(k): v for k, v in json.load(open(POP, encoding="utf-8")).items()}
    except FileNotFoundError:
        pop = {}
    for g in by.values():
        g["pop"] = max((pop.get(ev.get("id"), 0) for _, ev, _ in g["items"]), default=0)
    ranked = sorted(by.items(), key=lambda kv: (-kv[1]["pop"], -sum(len(r) for _, _, r in kv[1]["items"]),
                                                -len(kv[1]["items"]), kv[0]))
    ranked = [kv for kv in ranked if sum(len(r) for _, _, r in kv[1]["items"]) >= MIN_ROWS][:MAX_PAGES]

    try:
        reg = json.load(open(REG, encoding="utf-8"))
    except FileNotFoundError:
        reg = {}
    nxt = max(reg.values(), default=0) + 1
    os.makedirs(OUT_DIR, exist_ok=True)
    made = []
    for k, g in ranked:
        if k not in reg:
            reg[k] = nxt
            nxt += 1
        items = sorted(g["items"], key=lambda x: (x[0], x[1].get("id", 0)))
        total_rows = sum(len(r) for _, _, r in items)
        with open(os.path.join(OUT_DIR, f"{reg[k]}.html"), "w", encoding="utf-8") as f:
            f.write(page_html(g["name"], items, today, stamp, total_rows, reg[k]))
        made.append((g["name"], reg[k], total_rows))
    json.dump(reg, open(REG, "w", encoding="utf-8"), ensure_ascii=False, indent=0, sort_keys=True)

    # 今回作らなかった（これから買える枠が無くなった）組の古いページは消す＝売り切れ・終わった情報を検索に残さない
    live = {str(n) for _, n, _ in made}
    for fn in os.listdir(OUT_DIR):
        m = re.fullmatch(r"(\d+)\.html", fn)
        if m and m.group(1) not in live:
            os.remove(os.path.join(OUT_DIR, fn))

    # 一覧ページ（行ごと＝あ〜わ・A〜Z・数字記号・漢字）
    # 🆕10/27 すちこ「ア行か行　Z行とかにすぐ飛べる仕組み考えて」＝上に貼りつく帯から行へ飛ぶ・JS が動けば選んだ行だけ出す
    groups = defaultdict(list)
    for x in made:
        groups[row_of(x[0])].append(x)
    for g in groups.values():
        g.sort(key=lambda x: kana_key(x[0]))
    order = [r for r in ROWS if r in groups]
    made_sorted = [x for r in order for x in groups[r]]
    o = ["<!DOCTYPE html>", '<html lang="ja"><head>', '<meta charset="UTF-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1.0">', '<meta name="robots" content="index,follow">',
         "<title>アーティスト別 チケット発売日一覧 | OSHINAVI</title>",
         f'<meta name="description" content="OSHINAVIに載っているアーティスト{len(made)}組の、これから発売・販売中のチケット発売日ページの一覧。">',
         '<link rel="canonical" href="https://oshinavi.jp/artists.html">', GTAG,
         f"<style>{CSS}</style></head><body>",
         '<p class="note"><a href="index.html">OSHINAVI</a></p>', "<h1>アーティスト別 チケット発売日</h1>",
         f'<p class="note">最終更新：{esc(stamp)}／{len(made)}組（これから発売・販売中の受付がある組）。</p>',
         # 🆕10/27 すちこ「A」＝全部の名簿とは言わない（売り場に出演者が書いてある公演だけ・フェスの出演者を全部は拾えない）
         '<p class="note">売り場に出演者の名前が書いてある公演から作った一覧です。フェスの出演者や、主催の名前だけの公演は'
         '入っていないことがあるので、見つからない時は <a href="index.html">OSHINAVI トップの検索</a> で探してね。</p>',
         # 🆕2026-10-24 すちこ「検索窓あってもいいかもよ」＝1万組以上を探せるように名前の絞り込み（大文字小文字・全角半角・カタカナひらがなを区別しない）
         '<input id="q" type="search" placeholder="アーティスト名で探す" autocomplete="off" '
         'style="width:100%;max-width:420px;box-sizing:border-box;font-size:16px;padding:10px 12px;margin:4px 0 4px;'
         'border:1px solid #888;border-radius:8px">',
         '<p class="note" id="hit" aria-live="polite"></p>']
    # 行へ飛ぶ帯（上に貼りつく）＝かなの行は1段目、A〜Z は2段目
    def tab(r):
        return f'<a href="#r-{ROW_ID[r]}" data-r="{ROW_ID[r]}">{ROW_LABEL.get(r, r)}</a>'
    kana = [r for r in order if r in KANA_ROWS]
    rest = [r for r in order if r not in KANA_ROWS]
    # 🆕10/27 すちこ「トップページにとべるボタンも作って」＝帯の頭に置く（下に流しても消えない）
    o.append('<nav id="jump" style="position:sticky;top:0;z-index:5;background:#fff;padding:6px 0 4px;border-bottom:1px solid #ddd">'
             '<a class="home" href="index.html">← OSHINAVI トップへ</a>'
             '<div class="jr">' + "".join(tab(r) for r in kana) + "</div>"
             '<div class="jr">' + "".join(tab(r) for r in rest) + "</div></nav>")
    o.append("<style>.jr{display:flex;flex-wrap:wrap;gap:4px;margin:2px 0}.jr a{min-width:30px;text-align:center;padding:5px 6px;"
             "border:1px solid #ccc;border-radius:6px;text-decoration:none;color:#1a1a1a;font-size:14px}"
             ".jr a.on{background:#e4007f;color:#fff;border-color:#e4007f}"
             ".home{display:inline-block;margin:0 0 4px;padding:6px 12px;background:#e4007f;color:#fff;border-radius:6px;"
             "text-decoration:none;font-weight:bold;font-size:14px}#list h2{scroll-margin-top:96px}</style>")
    o.append('<div id="list">')
    for r in order:
        o.append(f'<section data-r="{ROW_ID[r]}"><h2 id="r-{ROW_ID[r]}">{ROW_LABEL.get(r, r)}{"行" if r in KANA_ROWS else ""}'
                 f'（{len(groups[r])}組）</h2><ul>')
        for nm, n, cnt in groups[r]:
            o.append(f'<li><a href="{OUT_DIR}/{n}.html">{esc(nm)}</a>（{cnt}件）</li>')
        o.append("</ul></section>")
    o.append("</div>")
    # JS が動けば＝選んだ行だけ出す（1万5千組を一度に描かない）・探す欄に入れたら全部の行から探す。JS が無ければ全部出る
    o.append("<script>(function(){var q=document.getElementById('q'),hit=document.getElementById('hit'),"
             "sec=[].slice.call(document.querySelectorAll('#list section')),tabs=[].slice.call(document.querySelectorAll('#jump .jr a')),"
             "li=[].slice.call(document.querySelectorAll('#list li'));"
             "function n(s){return s.normalize('NFKC').toLowerCase().replace(/[\\u30a1-\\u30f6]/g,function(c){"
             "return String.fromCharCode(c.charCodeAt(0)-96)}).replace(/[\\s・･]/g,'')}"
             "var key=li.map(function(x){return n(x.firstChild.textContent)});"
             "function show(r){sec.forEach(function(s){s.hidden=s.getAttribute('data-r')!==r});"
             "tabs.forEach(function(t){t.classList.toggle('on',t.getAttribute('data-r')===r)})}"
             "tabs.forEach(function(t){t.addEventListener('click',function(e){e.preventDefault();q.value='';hit.textContent='';"
             "li.forEach(function(x){x.hidden=false});show(t.getAttribute('data-r'));"
             "try{history.replaceState(null,'','#r-'+t.getAttribute('data-r'))}catch(_){}window.scrollTo(0,0)})});"
             "var h=(location.hash.match(/^#r-(.+)$/)||[])[1];show(h&&sec.some(function(s){return s.getAttribute('data-r')===h})?h:sec[0].getAttribute('data-r'));"
             "q.addEventListener('input',function(){var v=n(q.value),c=0;if(!v){show((document.querySelector('#jump .jr a.on')||tabs[0]).getAttribute('data-r'));"
             "li.forEach(function(x){x.hidden=false});hit.textContent='';return}"
             "sec.forEach(function(s){s.hidden=false});li.forEach(function(x,i){var ok=key[i].indexOf(v)>=0;x.hidden=!ok;if(ok)c++});"
             "sec.forEach(function(s){s.hidden=!s.querySelector('li:not([hidden])')});"
             "hit.textContent=c?c+'組が見つかったわ':'見つからなかったわ。トップの検索も試してね'});})();</script>")
    o.append("</body></html>")
    with open("artists.html", "w", encoding="utf-8") as f:
        f.write("\n".join(o))

    # sitemap.xml に足す（build_ai_page が毎回作り直すので、その後に呼ばれる前提）
    sm = open("sitemap.xml", encoding="utf-8").read()
    sm = re.sub(r"\s*<url><loc>https://oshinavi\.jp/(?:artists\.html|artist/\d+\.html)</loc>.*?</url>", "", sm)
    add = [f'  <url><loc>https://oshinavi.jp/artists.html</loc><lastmod>{today.isoformat()}</lastmod><changefreq>daily</changefreq></url>']
    for _, n, _ in made:
        add.append(f'  <url><loc>https://oshinavi.jp/{OUT_DIR}/{n}.html</loc><lastmod>{today.isoformat()}</lastmod><changefreq>daily</changefreq></url>')
    sm = sm.replace("</urlset>", "\n".join(add) + "\n</urlset>")
    open("sitemap.xml", "w", encoding="utf-8").write(sm)
    print(f"artist pages {len(made)} + artists.html + sitemap (today={today})")
    return made


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--today", default=None)
    a = ap.parse_args()
    build(date.fromisoformat(a.today) if a.today else date.today())


if __name__ == "__main__":
    main()
