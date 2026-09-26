# -*- coding: utf-8 -*-
"""9/27号「今週のピックアップ」＝1組1ページ版（2026-09-26 ユーザー決定）。
  draft_main_long.md ＋ draft_zen.md →
    tmp/pickup0927/pages/index.html   … 目次（号の見出し・カード6枚＝名前・イベント名・公演日時・発売日時・名前タイル・締め）
                                         ※導入3行と秋のリードは目次に置かない（9/26 ユーザー指示）
    tmp/pickup0927/pages/<slug>.html  … 組ごとのページ（本文は折りたたまずに全部）
    tmp/pickup0927/section_top.html   … ボタンのリンク先だけ pickup/2026-09-27/ に替える
  🚨公開フォルダ（pickup/）には書かない。公開時は pages/ の中身を pickup/2026-09-27/ へそのまま移す
    （リンクは全部その場所を前提にした相対リンク＝OSHINAVI本体は ../../）。
  🚨index.html は読むだけ（EVENTS・CSS・gtag を写す）。
  🚨文章は draft のまま（1文字も変えない）。draft を直したら `python tmp/pickup0927/build_pages.py` で作り直す。
  土台は build_page.py（1ページ版）。主役・深掘りの id、名前タイル12組はそこから写した。
"""
import datetime, html as H, io, json, os, re, sys, urllib.parse
sys.stdout.reconfigure(encoding='utf-8')

DRAFT_MAIN = "tmp/pickup0927/draft_main_long.md"
DRAFT_ZEN = "tmp/pickup0927/draft_zen.md"
OUT_DIR = "tmp/pickup0927/pages"
TOP_FILE = "tmp/pickup0927/section_top.html"
TOP_HREF_OLD, TOP_HREF_NEW = 'href="pickup/2026-09-27.html"', 'href="pickup/2026-09-27/index.html"'
BASE = "https://oshinavi.jp/pickup/2026-09-27/"
HOME = "../../index.html"
FROM, TO = "2026-09-28", "2026-10-04"
SUB = "9/28(月)〜10/4(日)にチケットの発売が始まるアーティスト紹介"
WD = "月火水木金土日"
# (draft の見出し, ファイル, ページ名, [id], カードに出す書き出しの行数)
MAIN = [("SCANDAL", "scandal", "SCANDAL", [6284, 7031, 11068, 24300], 2),
        ("松任谷由実", "yuming", "松任谷由実", [21210], 2),
        ("三浦大知", "miura", "三浦大知", [4042, 7118], 2),
        # 秦基博は1行目だけで長い（2行目は公演名）ので1行
        ("秦基博", "hata", "秦基博", [3051], 1),
        ("TOTO", "toto", "TOTO", [5656, 24301], 2)]
DEEP = ("深掘り", "zen", "『禅とジブリ』京都展", [2949], 1)
# 深掘りのバッジ＝1ページ版の箱の見出しと同じ会期（index.html の枠は「当日券 10/3 0:00発売」で、バッジにすると読み違える）
DEEP_BADGE = "会期 10/3(土)〜12/6(日)"
DEEP_HEAD = "会期 10/3(土)〜12/6(日)（京都市京セラ美術館 新館 東山キューブ）"
TILES = [("yama", [4521]),
         ("Silent Siren", [20948]),
         ("プロレスリング・ノア", [3635, 7079]),
         ("9mm Parabellum Bullet", [4366]),
         ("人間椅子", [5349]),
         ("上原ひろみ×熊谷和徳", [4364]),
         ("フラワーカンパニーズ", [738, 24124]),
         ("佐野元春&THE COYOTE BAND", [3117, 20348]),
         ("SHERBETS", [6281, 6282, 7028, 10776, 21310]),
         ("NoGoD", [6016, 21339]),
         ("福田こうへい", [734, 21151]),
         ("中村雅俊", [1634, 21235])]
TAIL = "他にも気になるアーティストがチケット発売しているわよ。"
# 目次のカード＝アーティスト名・イベント名・公演日時・チケット販売日時だけ（2026-09-26 ユーザー指示「導入文は無くしてシンプルに」）
# イベント名は公式の正式名称、開演は公式の START（facts_main.md／SCANDAL 静岡 11/28 は 9/26 に公式 finaltour47 で確認）
EVENT_NAME = {"scandal": "SCANDAL FINAL TOUR 2026-2027「SCANDALの47都道府県ツアー」",
              "yuming": "FORUM8 presents 松任谷由実 THE WORMHOLE TOUR 2025-2026",
              "miura": "DAICHI MIURA LIVE TOUR 2026 Raw / Bare",
              "hata": "HATA MOTOHIRO 20th Anniversary LIVE",
              "toto": "TOTO 50TH ANNIVERSARY TOUR",
              "zen": "京都市京セラ美術館 新館 東山キューブ"}
START = {"10/22 東京": "19:00", "10/24 青森": "17:30", "10/25 秋田": "17:30", "10/27 岩手": "19:00",
         "10/28 宮城": "19:00", "11/1 山形": "17:30", "11/2 福島": "19:00", "11/28 静岡": "17:30",
         "R9年 1/29 三重": "19:00", "R9年 1/31 岐阜": "17:30",
         "11/24 栃木": "18:30", "10/30 宮城": "18:30", "10/31 岩手": "17:30",
         "11/3 大阪": "17:00", "R9年 3/22 大阪": "17:00"}
# 深掘りは会期と開館時間（公式 zen-ghibli.jp/kyoto/）
ZEN_SHOW = "10/3(土)〜12/6(日) 10:00〜18:00 京都"

html = io.open("index.html", encoding="utf-8", newline="").read()
events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", html, re.S).group(1))
by_id = {e["id"]: e for e in events}


def esc(t):
    return H.escape(t, quote=True)


def q_href(q):
    return HOME + "?q=" + urllib.parse.quote(q, safe="")


def paras_of(body):
    out, cur = [], []
    for ln in body:
        if ln.strip():
            cur.append(ln.strip())
        elif cur:
            out.append(cur); cur = []
    if cur:
        out.append(cur)
    return out


def br_p(paras, ind="    ", cls=""):
    c = ' class="%s"' % cls if cls else ""
    return "\n".join('%s<p%s>%s</p>' % (ind, c, "<br>\n".join(esc(l) for l in p)) for p in paras)


def week_slots(e):
    r = []
    for t in e.get("tickets", []):
        if t.get("soldout") or t.get("saleEnded"):
            continue
        sd = t.get("startDate") or ""
        if FROM <= sd <= TO and re.search(r"\d{1,2}/\d{1,2}\s*\d{1,2}:\d{2}発売", t.get("type") or ""):
            r.append(t)
    return r


def jp(d):
    y, m, dd = (int(x) for x in d.split("-"))
    return "%d/%d(%s)" % (m, dd, WD[datetime.date(y, m, dd).weekday()])


def pref(p):
    p = p.strip()
    if p in ("東京都", "京都府", "大阪府") or (p.endswith("県") and len(p) > 2):
        return p[:-1]
    return p


def show_list(ss):
    seen, out = set(), []
    for t in ss:
        m = re.search(r"（([^（）]+?)\s*((?:R9年\s*)?[\d/〜]+(?:R9年\s*[\d/]+)?)公演", t.get("type", ""))
        if not m:
            continue
        lab = "%s %s" % (m.group(2).strip(), pref(m.group(1)))
        if lab not in seen:
            seen.add(lab); out.append(lab)
    return "／".join(out)


def sale_label(ss):
    def part(xs):
        ds = sorted(set(t["startDate"] for t in xs))
        tms = sorted(set(re.search(r"(\d{1,2}:\d{2})発売", t["type"]).group(1) for t in xs))
        return "／".join(jp(d) for d in ds) + (" " + tms[0] if len(tms) == 1 else "")
    gen = [t for t in ss if "一般" in t["type"]]
    pre = [t for t in ss if "一般" not in t["type"]]
    if pre and gen:
        return "先行 %s・一般 %s" % (part(pre), part(gen))
    return "%s %s" % (part(gen or pre), "一般発売" if gen else "先行")


def search_n(q):
    return sum(1 for e in events if e.get("verified") is True
               and q.lower() in (e.get("artist", "") + " " + e.get("name", "")).lower())


# ── draft を分ける
main_raw = io.open(DRAFT_MAIN, encoding="utf-8").read().replace("\r", "").rstrip("\n")
zen_raw = io.open(DRAFT_ZEN, encoding="utf-8").read().replace("\r", "").rstrip("\n")
lines = (main_raw + "\n" + zen_raw).split("\n")
title = lines[0].strip()
secs, cur = {}, "（導入）"
for ln in lines[1:]:
    m = re.match(r"^## (.+)$", ln)
    if m:
        cur = m.group(1).strip(); secs[cur] = []
    else:
        secs.setdefault(cur, []).append(ln)
lede = [l.strip() for l in secs["（導入）"] if l.strip()]
assert len(lede) == 3, lede
lead = paras_of(secs["秋のリード"])

deep = secs["深掘り"]
dtitle, drest = "", []
for ln in deep:
    m = re.match(r"^\*\*(.+?)\*\*$", ln.strip())
    if m and not dtitle:
        dtitle = m.group(1); continue
    drest.append(ln)
assert [x for x in drest if x.strip()][-1].strip() == TAIL
drest = [x for x in drest if x.strip() != TAIL]

# 組ごとの材料
ACTS = []
for head, slug, pname, ids, ncard in MAIN:
    ss = [t for i in ids for t in week_slots(by_id[i])]
    assert ss, head
    body = paras_of(secs[head])
    ACTS.append(dict(slug=slug, name=pname, h1=pname, badge=sale_label(ss), body=body,
                     card=[l for p in body for l in p][:ncard], kind="主役",
                     boxes=[("発売になる公演", q_href(head), show_list(ss))]))
dbody = paras_of(drest)
dboxes = []
for i in DEEP[3]:
    e = by_id[i]
    dboxes.append((DEEP_HEAD, q_href(e["name"]), show_list(week_slots(e))))
ACTS.append(dict(slug=DEEP[1], name=DEEP[2], h1=dtitle, badge=DEEP_BADGE, body=dbody,
                 card=[l for p in dbody for l in p][:DEEP[4]], kind="深掘り", boxes=dboxes))

# ── 共通の head・CSS
css_all = html[html.index("<style>") + len("<style>"):html.index("</style>")].replace("\r\n", "\n")
m_root = re.search(r"\n    :root \{.*?\n    \}\n", css_all, re.S)
m_body = re.search(r"\n    body \{.*?\n    \}\n", css_all, re.S)
i0 = css_all.index("    /* ── 週1記事「今週のピックアップ」")
i1 = css_all.index("    /* ── 最終更新")
pk_css = css_all[i0:i1].rstrip() + "\n"
# 折りたたみ（▼▲のボタン）・画像・pk-most は1組1ページでは使わないので写さない
DROP = r"pk-most|pk-open|pk-close|pk-body|pk-detail|pk-more|pk-fig|pk-portrait|pk-mon"
pk_css = re.sub(r"    @media \(max-width: 359px\) \{\n[^{}]*\{[^{}]*\}\n    \}\n", "", pk_css)
pk_css = re.sub(r"(?m)^    [^{}\n]*(?:%s)[^{}\n]*\{[^{}]*\}\n" % DROP, "", pk_css)
assert not re.search(DROP, pk_css), re.findall(r".*(?:%s).*" % DROP, pk_css)
assert pk_css.count("{") == pk_css.count("}")
pk_css = pk_css.rstrip()
# gtag は async の読み込みと config の両方（1ページ版は async の1行しか写っていなかった）
gtag = re.search(r"  <!-- Google tag \(gtag\.js\) -->.*?gtag\('config', 'G-RM1EQ5M4HT'\);\s*</script>\r?\n",
                 html, re.S).group(0).replace("\r\n", "\n")
assert "googletagmanager.com/gtag/js?id=G-RM1EQ5M4HT" in gtag and "window.dataLayer" in gtag

PAGE_CSS = [
    '    * { margin: 0; padding: 0; box-sizing: border-box; }',
    m_root.group(0).strip("\n"),
    m_body.group(0).strip("\n"),
    '    html, body { overflow-x: hidden; }',
    '    /* ── ページの頭（チケット・イベント一覧へ戻る）＝ 1ページ版・pickup/2026-08-20.html と同じ形 ── */',
    '    header {',
    '      background: var(--bg2); border-bottom: 1px solid var(--border);',
    '      padding: 0 20px; display: flex; align-items: center; justify-content: space-between;',
    '      gap: 12px; height: 64px; position: sticky; top: 0; z-index: 100;',
    '    }',
    '    .logo {',
    '      font-size: 20px; font-weight: 900; letter-spacing: 3px; text-decoration: none;',
    '      background: linear-gradient(90deg, var(--accent), var(--accent2));',
    '      -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;',
    '    }',
    '    .nav-back {',
    '      color: var(--accent2); text-decoration: none; font-size: 13px; font-weight: 700; white-space: nowrap;',
    '      border: 1px solid var(--accent2); background: rgba(0,229,255,.12); padding: 7px 14px; border-radius: 4px; transition: .2s;',
    '    }',
    '    .nav-back:hover, .nav-back:focus-visible { color: #0a0a0a; background: var(--accent2); }',
    '    .wrap { max-width: 820px; margin: 0 auto; padding: 0 0 60px; }',
    '    @media (max-width: 400px) { header { padding: 0 14px; } .logo { font-size: 17px; letter-spacing: 2px; } }',
    '',
    '    /* ↓ index.html の <style> から「今週のピックアップ」の定義を写したもの（折りたたみ・画像の分は除いた） */',
    pk_css,
    '',
    '    /* ── 1組1ページ用の足し算（index.html には無い並び） ── */',
    '    .pickup { overflow-wrap: break-word; }',
    '    .pickup .pk-lede + .pk-lede { margin-top: 18px; }',
    '    /* 目次へ戻る（組のページの一番上）。ヘッダーに並べると 320px で溢れるので記事の上に1行で置く */',
    '    .pk-crumb { max-width: 1200px; margin: 14px auto 0; padding: 0 22px; font-size: 13px; }',
    '    .pk-crumb a { color: var(--accent2); text-decoration: none; font-weight: 700; }',
    '    .pk-crumb a:hover, .pk-crumb a:focus-visible { text-decoration: underline; }',
    '    @media (max-width: 640px) { .pk-crumb { margin: 12px 12px 0; padding: 0 3px; } }',
    '    /* 目次のカード＝押すとその組のページへ */',
    '    .pickup .pk-cards { display: grid; gap: 12px; margin-top: 12px; }',
    '    .pickup a.pk-card {',
    '      display: block; text-decoration: none; color: var(--text);',
    '      background: var(--bg3); border: 1px solid var(--border); border-radius: 6px;',
    '      padding: 14px 15px 12px; transition: .2s;',
    '    }',
    '    .pickup a.pk-card:hover, .pickup a.pk-card:focus-visible { border-color: var(--accent); background: rgba(224,64,251,.10); }',
    '    .pickup .pk-card .pk-sale { margin-bottom: 8px; }',
    '    /* 目次＝1組1リンク（文字ぜんぶが記事へのリンク） */',
    '    .pickup a.pk-item { display: block; padding: 14px 2px; border-bottom: 1px solid var(--border); text-decoration: none; color: var(--text); transition: .2s; }',
    '    .pickup .pk-h2 + a.pk-item { border-top: 1px solid var(--border); margin-top: 10px; }',
    '    .pickup a.pk-item:hover, .pickup a.pk-item:focus-visible { background: rgba(224,64,251,.08); }',
    '    .pickup .pk-i-name { display: block; font-size: 17px; font-weight: 900; color: var(--accent); text-decoration: underline; text-underline-offset: 4px; margin-bottom: 4px; }',
    '    .pickup .pk-i-line { display: block; font-size: 14.5px; line-height: 1.75; text-decoration: underline; text-decoration-color: rgba(255,255,255,.25); text-underline-offset: 4px; }',
    '    .pickup .pk-i-line b { color: var(--accent2); font-weight: 800; font-size: 13px; }',
    '    /* 組のページ＝見出しの下に発売バッジ、本文は折りたたまずに全部 */',
    '    .pickup .pk-page-name { font-size: clamp(20px, 4.6vw, 26px); font-weight: 900; line-height: 1.45; color: var(--accent); margin-bottom: 8px; }',
    '    .pickup .pk-page-name.pk-long { font-size: clamp(17px, 3.6vw, 21px); }',
    '    .pickup .pk-text { margin-top: 8px; }',
    '    .pickup .pk-text p { font-size: 15px; line-height: 1.95; margin-bottom: 14px; color: var(--text); }',
    '    .pickup .pk-shows { margin-top: 6px; }',
    '    /* 前の記事／次の記事 */',
    '    .pickup .pk-pager { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 26px; }',
    '    .pickup .pk-pager a, .pickup .pk-pager .pk-pager-none {',
    '      display: block; min-width: 0; padding: 11px 13px; border-radius: 5px;',
    '      background: var(--bg3); border: 1px solid var(--border); text-decoration: none; transition: .2s;',
    '    }',
    '    .pickup .pk-pager .pk-pager-none { visibility: hidden; }',
    '    .pickup .pk-pager a:hover, .pickup .pk-pager a:focus-visible { border-color: var(--accent); background: rgba(224,64,251,.10); }',
    '    .pickup .pk-pager .pk-prev { text-align: left; }',
    '    .pickup .pk-pager .pk-next { text-align: right; }',
    '    /* Amazonのグッズボタン（深掘りのジブリなど）＝アソシエイトタグ oshinavi0a-22 */',
    '    .pickup .pk-amazon { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-top: 14px; padding: 14px 16px; border: 1px solid var(--orange); border-radius: 12px; color: var(--text); text-decoration: none; background: rgba(255,171,64,.08); font-weight: 700; }',
    '    .pickup .pk-amazon:hover, .pickup .pk-amazon:focus-visible { background: rgba(255,171,64,.16); }',
    '    .pickup .pk-amazon .pk-amazon-go { color: var(--orange); white-space: nowrap; font-size: 13px; }',
    '    .pickup .pk-pager-label { display: block; font-size: 11.5px; color: var(--accent2); font-weight: 700; }',
    '    .pickup .pk-pager-name { display: block; font-size: 14px; font-weight: 800; color: var(--text); margin-top: 2px; }',
    '    .pickup a.pk-toc {',
    '      display: block; margin-top: 12px; padding: 13px; text-align: center; text-decoration: none;',
    '      border: 1px solid var(--accent); border-radius: 5px; color: var(--accent);',
    '      font-size: 14px; font-weight: 800; letter-spacing: .06em; transition: .2s;',
    '    }',
    '    .pickup a.pk-toc:hover, .pickup a.pk-toc:focus-visible { background: rgba(224,64,251,.14); }',
]


def head(ptitle, desc, canon, ogt):
    return ['<!DOCTYPE html>', '<html lang="ja">', '<head>', gtag.rstrip("\n"),
            '  <meta charset="UTF-8">',
            '  <meta name="viewport" content="width=device-width, initial-scale=1.0">',
            '  <title>%s</title>' % esc(ptitle),
            '  <meta name="description" content="%s">' % esc(desc),
            '  <link rel="canonical" href="%s">' % canon,
            '  <meta property="og:title" content="%s">' % esc(ogt),
            '  <meta property="og:description" content="%s">' % esc(desc),
            '  <meta property="og:type" content="article">',
            '  <meta property="og:url" content="%s">' % canon,
            '  <meta property="og:image" content="https://oshinavi.jp/og-image.png">',
            '  <meta property="og:site_name" content="OSHINAVI">',
            '  <meta property="og:locale" content="ja_JP">',
            '  <meta name="twitter:card" content="summary_large_image">',
            '  <link rel="icon" type="image/png" href="/logo.png">',
            '  <meta name="theme-color" content="#e040fb">',
            '  <style>'] + PAGE_CSS + ['  </style>', '</head>', '<body>', '',
            '<header>',
            '  <a href="%s" class="logo">OSHINAVI</a>' % HOME,
            '  <a href="%s" class="nav-back">← チケット・イベント一覧へ</a>' % HOME,
            '</header>', '']


def tail_block():
    return ['  <a class="pk-tail" href="%s?status=urgent">%s<span class="pk-go">今週発売を見る →</span></a>'
            % (HOME, esc(TAIL))]


FOOT = ['</article>', '</main>', '', '</body>', '</html>', '']


def finish(P):
    s = "\r\n".join(P).replace("\r\r\n", "\r\n")
    return re.sub(r"(?<!\r)\n", "\r\n", s)


def lede_block(ind):
    return ['%s<div class="pk-lede">' % ind,
            '%s  <p>%s</p>' % (ind, "<br>\n".join(esc(l) for l in lede[:2])),
            '%s  <p class="pk-tease">%s</p>' % (ind, esc(lede[2])),
            '%s</div>' % ind]


OUT = {}

# ── 1) 目次
desc = ("%s。SCANDALの「最後の旅」47都道府県ツアー、松任谷由実、三浦大知、秦基博、TOTO。"
        "深掘りは京都市京セラ美術館の『禅とジブリ』京都展。" % SUB)
P = head("今週のピックアップ｜%s - OSHINAVI" % title, desc, BASE, "今週のピックアップ｜" + title)
P += ['<main class="wrap">',
      '<article class="pickup" id="pickup">',
      '  <span class="pk-label">📖 今週のピックアップ</span>',
      '  <h1 class="pk-title">%s</h1>' % esc(title),
      '  <p class="pk-sub">%s</p>' % esc(SUB)]


def show_lines(a):
    if a["slug"] == "zen":
        return [ZEN_SHOW]
    out = []
    for lab in a["boxes"][0][2].split("／"):
        m = re.fullmatch(r"(R9年 )?(\d+)/(\d+) (\S+)", lab)
        d = "%d-%02d-%02d" % (2027 if m.group(1) else 2026, int(m.group(2)), int(m.group(3)))
        out.append("%s%s %s %s" % (m.group(1) or "", jp(d), START[lab], m.group(4)))
    return out


def card_sale(a):
    if a["slug"] == "zen":
        t = week_slots(by_id[DEEP[3][0]])[0]
        return "%s %s 当日券" % (jp(t["startDate"]), re.search(r"(\d{1,2}:\d{2})発売", t["type"]).group(1))
    return a["badge"]


def card(a, top=False):
    # 9/26 ユーザー指示＝名前／イベント名／公演（1つめ＋「他」）／チケット販売日時を並べ、文字ぜんぶを記事へのリンクに
    shows = show_lines(a)
    show = shows[0] + (" 他" if len(shows) > 1 else "")
    return ['  <a class="pk-item" href="./%s.html">' % a["slug"],
            '    <span class="pk-i-name">%s</span>' % esc(a["name"]),
            '    <span class="pk-i-line">%s</span>' % esc(EVENT_NAME[a["slug"]]),
            '    <span class="pk-i-line">%s</span>' % esc(show),
            '    <span class="pk-i-line"><b>チケット販売日時</b> %s</span>' % esc(card_sale(a)),
            '  </a>']


P += ['  <h2 class="pk-h2">今週の主役</h2>']
for n, a in enumerate(ACTS[:-1]):
    P += card(a, n == 0)
P += ['  <h2 class="pk-h2">今週の深掘り</h2>']
P += card(ACTS[-1])
P += [
      '  <p class="pk-others-note">今週はほかにも、こんな名前が出るのよ。</p>',
      '  <div class="pk-others">']
print("── タイル")
for disp, ids in TILES:
    ds = sorted(set(t["startDate"] for i in ids for t in week_slots(by_id[i])))
    assert ds, disp
    assert all(by_id[i].get("verified") is True for i in ids), disp
    when = "／".join(jp(d) for d in ds[:3]) + ("ほか" if len(ds) > 3 else "")
    P.append('    <a href="%s"><span class="pk-o-name">%s</span><span class="pk-o-when">%s</span></a>'
             % (esc(q_href(disp)), esc(disp), esc(when)))
    print("  %s | %s | 検索→%d件" % (disp, when, search_n(disp)))
P += ['  </div>'] + tail_block() + FOOT
OUT["index.html"] = finish(P)

# ── 2) 組ごとのページ
print("── 組")
for k, a in enumerate(ACTS):
    fn = a["slug"] + ".html"
    d = "".join(a["card"])
    P = head("%s｜今週のピックアップ - OSHINAVI" % a["name"], d, BASE + fn, "%s｜今週のピックアップ" % a["name"])
    P += ['<nav class="pk-crumb"><a href="./index.html">← 今週のピックアップ（目次）</a></nav>',
          '<main class="wrap">',
          '<article class="pickup" id="pickup">',
          '  <span class="pk-label">📖 今週のピックアップ・今週の%s</span>' % a["kind"],
          '  <h1 class="pk-page-name%s">%s</h1>' % (" pk-long" if len(a["h1"]) > 20 else "", esc(a["h1"])),
          '  <span class="pk-sale">%s</span>' % esc(a["badge"]),
          '  <div class="pk-text">', br_p(a["body"], "    "), '  </div>']
    for bh, href, lst in a["boxes"]:
        P += ['  <a class="pk-shows" href="%s">' % esc(href),
              '    <b>%s<span class="pk-go">タップで探す →</span></b>' % esc(bh),
              '    %s' % esc(lst),
              '  </a>']
        print("  %s | %s | %s | %s" % (fn, a["badge"], href, lst))
    prv = ACTS[k - 1] if k > 0 else None
    nxt = ACTS[k + 1] if k + 1 < len(ACTS) else None
    P.append('  <nav class="pk-pager" aria-label="前の記事・次の記事">')
    P.append('    <a class="pk-prev" href="./%s.html"><span class="pk-pager-label">← 前の記事</span><span class="pk-pager-name">%s</span></a>'
             % (prv["slug"], esc(prv["name"])) if prv else '    <span class="pk-pager-none"></span>')
    P.append('    <a class="pk-next" href="./%s.html"><span class="pk-pager-label">次の記事 →</span><span class="pk-pager-name">%s</span></a>'
             % (nxt["slug"], esc(nxt["name"])) if nxt else '    <span class="pk-pager-none"></span>')
    P += ['  </nav>',
          '  <a class="pk-toc" href="./index.html">今週のピックアップの目次へ戻る</a>']
    P += tail_block() + FOOT
    OUT[fn] = finish(P)

os.makedirs(OUT_DIR, exist_ok=True)
for fn, s in OUT.items():
    io.open(os.path.join(OUT_DIR, fn), "w", encoding="utf-8", newline="").write(s)

# ── 3) トップの短い版＝リンク先だけ替える
top = io.open(TOP_FILE, encoding="utf-8", newline="").read()
if TOP_HREF_OLD in top:
    top = top.replace(TOP_HREF_OLD, TOP_HREF_NEW)
    io.open(TOP_FILE, "w", encoding="utf-8", newline="").write(top)
assert top.count(TOP_HREF_NEW) == 1 and 'target="_blank"' in top

# ── 点検
print("── 点検")
ok = True


def body_of(s):
    b = s[s.index("<body>"):]
    return re.sub(r"<style>.*?</style>|<script>.*?</script>", "", b, flags=re.S)


def text_lines(s):
    s = re.sub(r"<br>\s*", "\n", s)
    s = re.sub(r"</(p|span|b|h1|h2|button|a|div|nav|dt|dd)>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    return [H.unescape(x).strip() for x in s.split("\n") if x.strip()]


def section_text(s, cls):
    m = re.search(r'<div class="%s">(.*?)\r\n  </div>' % cls, s, re.S)
    return text_lines(m.group(1)) if m else None


for fn, s in list(OUT.items()) + [("section_top.html", top)]:
    b = body_of(s) if "<body>" in s else re.sub(r"<style>.*?</style>", "", s, flags=re.S)
    whole = s
    bad = {
        "blockquote": whole.count("blockquote"), "&gt;": b.count("&gt;"), "|---": whole.count("|---"),
        "pk-most": whole.count("pk-most"), "▲▼": len(re.findall("[▲▼]", whole if fn != "section_top.html" else b)),
        'href="#"': whole.count('href="#"'), "data-pk-": whole.count("data-pk-"),
        # 。のあとが 」』" なのは曲名・題名・引用の中（例：『…恋をした。』）
        "。未改行": len(re.findall(r"。(?!<br>|</p>|」|』|&quot;)", b.replace("わよ。<span", ""))),
        "行頭」": len(re.findall(r"<br>\s*」", b)),
    }
    css = "".join(re.findall(r"<style>(.*?)</style>", s, re.S)) + (css_all if fn == "section_top.html" else "")
    used = set(re.findall(r'class="([^"]+)"', b))
    undefined = sorted({c for u in used for c in u.split() if not re.search(r"\.%s(?![\w-])" % re.escape(c), css)})
    links = re.findall(r'href="([^"]+)"', b)
    broken = []
    for h in links:
        if h.startswith(("http", "/")):
            continue
        if fn == "section_top.html":
            if h != "pickup/2026-09-27/index.html":
                broken.append(h)
            continue
        if h.startswith(HOME):
            rest = h[len(HOME):]
            if not (rest == "" or re.fullmatch(r"\?(q=[^\"&#]+|status=urgent)", rest)):
                broken.append(h)
            continue
        if not os.path.exists(os.path.join(OUT_DIR, h)):
            broken.append(h)
    gt = ("googletagmanager.com/gtag/js?id=G-RM1EQ5M4HT" in s and "gtag('config', 'G-RM1EQ5M4HT')" in s) \
        if fn != "section_top.html" else True
    bad_n = sum(bad.values())
    if bad_n or undefined or broken or not gt:
        ok = False
    print("  [%s] 残り:%s 未定義クラス:%s リンク%d本 切れ:%s gtag:%s" % (
        fn, "0" if not bad_n else {k: v for k, v in bad.items() if v}, undefined or "なし",
        len(links), broken or "0", "あり" if gt else "★無し"))

# 本文照合
tl = text_lines(body_of(OUT["index.html"]))
need = [title, SUB]
got = tl[tl.index(title):tl.index(title) + len(need)] if title in tl else []
print("  本文照合 目次（見出し・副題）: %s" % ("一致" if got == need else "★ずれ"))
ok &= got == need
for a in ACTS:
    assert a["name"] in tl and EVENT_NAME[a["slug"]] in tl, a["name"]
    fn = a["slug"] + ".html"
    want = [l for p in a["body"] for l in p]
    have = section_text(OUT[fn], "pk-text")
    h1 = re.search(r'<h1 class="pk-page-name[^"]*">(.*?)</h1>', OUT[fn]).group(1)
    same = have == want and H.unescape(h1) == a["h1"]
    ok &= same
    nchar = sum(len(l) for l in want)
    print("  本文照合 %-10s: %s（%d行・%d字）" % (fn, "一致" if same else "★ずれ", len(want), nchar))
# draft 全体（締めの一文とタイトル類を除く）が各ページに漏れなく1回ずつ入っているか
all_draft = [l.strip() for l in lines if l.strip() and not l.startswith("## ")
             and not re.match(r"^\*\*.+\*\*$", l.strip()) and l.strip() != TAIL]
# 導入3行と秋のリードは目次から外した（9/26）＝トップの短い版にだけある
placed = [x for x in need if x != SUB] + lede + [l for p in lead for l in p] + [l for a in ACTS for p in a["body"] for l in p]
print("  draft の行 %d ／ ページに置いた行 %d ／ 抜け %d" % (len(all_draft), len(placed),
      len([x for x in all_draft if x not in placed])))
ok &= all_draft == placed
print("OK" if ok else "★NG")
for fn, s in OUT.items():
    print("WROTE %s/%s (%d bytes)" % (OUT_DIR, fn, len(s.encode("utf-8"))))
