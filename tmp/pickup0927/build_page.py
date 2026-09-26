# -*- coding: utf-8 -*-
"""9/27号「今週のピックアップ」＝今回から別ページで出す形（2026-09-26）。
  draft_main.md ＋ draft_zen.md →
    tmp/pickup0927/section_top.html … index.html の <section class="pickup"> と差し替える短い版
                                       （見出し・サブ・導入3行・「つづきを読む」リンクだけ。本文は入れない）
    pickup/2026-09-27.html         … 記事の本文ページ（別タブで開く）
  🚨index.html は読むだけ（EVENTS・CSS・gtag を写す）。書き換えない。
  🚨文章は draft のまま（1文字も変えない）。draft を直したら `python tmp/pickup0927/build_page.py` で作り直す。
  別ページなので index.html の中でしか効かない仕掛けは置き換える：
    data-pk-search="名前"   → href="../?q=<URLエンコード>"
    data-pk-status="urgent" → href="../?status=urgent"
  （index.html は URLSearchParams で q／status を読む。status の値は .filter-btn[data-status] と同じ urgent）
  形は前号 tmp/pickup0920/build_section.py を下敷きにした。
"""
import datetime, html as H, io, json, re, sys, urllib.parse
sys.stdout.reconfigure(encoding='utf-8')

DRAFTS = ["tmp/pickup0927/draft_main.md", "tmp/pickup0927/draft_zen.md"]
OUT_TOP = "tmp/pickup0927/section_top.html"
OUT_PAGE = "pickup/2026-09-27.html"
PAGE_REL = "pickup/2026-09-27.html"
CANON = "https://oshinavi.jp/pickup/2026-09-27.html"
FROM, TO = "2026-09-28", "2026-10-04"
SUB = "9/28(月)〜10/4(日)にチケットの発売が始まるアーティスト紹介"
WD = "月火水木金土日"
MAIN = [("SCANDAL", [6284, 7031, 11068, 24300]),
        ("松任谷由実", [21210]),
        ("三浦大知", [4042, 7118]),
        ("秦基博", [3051]),
        ("TOTO", [5656, 24301])]
DEEP_IDS = [2949]
DEEP_HEAD = "会期 10/3(土)〜12/6(日)（京都市京セラ美術館 新館 東山キューブ）"
# タイル＝brief.md「タイルの順」（Xフォロワー順）。今週(9/28〜10/4)に発売が始まる枠があるものだけ・12組まで。
# (表示名＝検索語, [id])。🚨枠が無ければ assert で落ちる＝入れない。
# 候補の「中村雅俊・舟木一夫」は別々のエントリ（中村雅俊 id1634・21235／舟木一夫 id21152）で、
# 2組に割ると13組になるので、12組目は中村雅俊までにした（舟木一夫は13番目で入らない）。
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

html = io.open("index.html", encoding="utf-8", newline="").read()
events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", html, re.S).group(1))
by_id = {e["id"]: e for e in events}
draft = "\n".join(io.open(p, encoding="utf-8").read().rstrip("\n") for p in DRAFTS).replace("\r", "")


def esc(t):
    return H.escape(t, quote=True)


def q_href(q):
    return "../?q=" + urllib.parse.quote(q, safe="")


def br_p(paras, ind="        "):
    """draft.md の1行＝画面の1行（「。」のあとで改行済み）。空行で段落を割る。"""
    return "\n".join('%s<p>%s</p>' % (ind, "<br>\n".join(esc(l) for l in p)) for p in paras)


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
    # 東京都→東京・大阪府→大阪・栃木県→栃木（「京都」の「都」は削らない）
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
    """画面と同じ判定（verified のみ・artist+name の部分一致・小文字化）で何件出るか"""
    return sum(1 for e in events if e.get("verified") is True
               and q.lower() in (e.get("artist", "") + " " + e.get("name", "")).lower())


# ── draft を分ける
lines = draft.split("\n")
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


def lede_block(ind):
    # 導入3行＝1〜2行目が今週の話、3行目が深掘りの予告（pk-tease＝点線の下）
    return ['%s<div class="pk-lede">' % ind,
            '%s  <p>%s</p>' % (ind, "<br>\n".join(esc(l) for l in lede[:2])),
            '%s  <p class="pk-tease">%s</p>' % (ind, esc(lede[2])),
            '%s</div>' % ind]


# ── 1) トップに置く短い版
TOP = ['<section class="pickup" id="pickup">',
       '  <style>',
       '    /* 9/27号から本文は別ページ（別タブ）。ボタンはリンクなので下向きの印を → に替える */',
       '    .pickup a.pk-more { text-align: center; text-decoration: none; }',
       "    .pickup a.pk-more::after { content: ' →'; }",
       '  </style>',
       '  <span class="pk-label">📖 今週のピックアップ</span>',
       '  <h2 class="pk-title">%s</h2>' % esc(title),
       '  <p class="pk-sub">%s</p>' % esc(SUB)]
TOP += lede_block("  ")
TOP += ['  <a class="pk-more" href="%s" target="_blank" rel="noopener">つづきを読む</a>' % PAGE_REL,
        '</section>']
top = "\r\n".join(TOP)

# ── 2) 本文ページ
css_all = html[html.index("<style>") + len("<style>"):html.index("</style>")].replace("\r\n", "\n")
m_root = re.search(r"\n    :root \{.*?\n    \}\n", css_all, re.S)
m_body = re.search(r"\n    body \{.*?\n    \}\n", css_all, re.S)
i0 = css_all.index("    /* ── 週1記事「今週のピックアップ」")
i1 = css_all.index("    /* ── 最終更新")
pk_css = css_all[i0:i1].rstrip()
gtag = re.search(r"  <!-- Google tag \(gtag\.js\) -->.*?</script>\r?\n", html, re.S).group(0).replace("\r\n", "\n")
assert "G-RM1EQ5M4HT" in gtag

desc = ("%s。SCANDALの「最後の旅」47都道府県ツアー、松任谷由実、三浦大知、秦基博、TOTO。"
        "深掘りは京都市京セラ美術館の『禅とジブリ』京都展。" % SUB)
page_title = "今週のピックアップ｜%s - OSHINAVI" % title

P = ['<!DOCTYPE html>', '<html lang="ja">', '<head>', gtag.rstrip("\n"),
     '  <meta charset="UTF-8">',
     '  <meta name="viewport" content="width=device-width, initial-scale=1.0">',
     '  <title>%s</title>' % esc(page_title),
     '  <meta name="description" content="%s">' % esc(desc),
     '  <link rel="canonical" href="%s">' % CANON,
     '  <meta property="og:title" content="%s">' % esc("今週のピックアップ｜" + title),
     '  <meta property="og:description" content="%s">' % esc(desc),
     '  <meta property="og:type" content="article">',
     '  <meta property="og:url" content="%s">' % CANON,
     '  <meta property="og:image" content="https://oshinavi.jp/og-image.png">',
     '  <meta property="og:site_name" content="OSHINAVI">',
     '  <meta property="og:locale" content="ja_JP">',
     '  <meta name="twitter:card" content="summary_large_image">',
     '  <link rel="icon" type="image/png" href="/logo.png">',
     '  <meta name="theme-color" content="#e040fb">',
     '  <style>',
     '    * { margin: 0; padding: 0; box-sizing: border-box; }',
     m_root.group(0).strip("\n"),
     m_body.group(0).strip("\n"),
     '    html, body { overflow-x: hidden; }',
     '    /* ── ページの頭（OSHINAVIへ戻る）＝ pickup/2026-08-20.html と同じ形 ── */',
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
     '      color: var(--text-muted); text-decoration: none; font-size: 13px; white-space: nowrap;',
     '      border: 1px solid var(--border); padding: 7px 14px; border-radius: 4px; transition: .2s;',
     '    }',
     '    .nav-back:hover, .nav-back:focus-visible { color: var(--accent2); border-color: var(--accent2); }',
     '    .wrap { max-width: 820px; margin: 0 auto; padding: 0 0 60px; }',
     '    @media (max-width: 400px) { header { padding: 0 14px; } .logo { font-size: 17px; letter-spacing: 2px; } }',
     '',
     '    /* ↓ index.html の <style> から「今週のピックアップ」の定義をそのまま写したもの */',
     pk_css,
     '',
     '    /* 別ページ用の足し算（index.html には無い並び）＝導入の箱の下に秋のリードの箱が続く */',
     '    .pickup .pk-lede + .pk-lede { margin-top: 18px; }',
     '    .pickup { overflow-wrap: break-word; }',
     '  </style>',
     '</head>',
     '<body>',
     '',
     '<header>',
     '  <a href="../" class="logo">OSHINAVI</a>',
     '  <a href="../" class="nav-back">← OSHINAVIへ戻る</a>',
     '</header>',
     '',
     '<main class="wrap">',
     '<article class="pickup" id="pickup">',
     '  <span class="pk-label">📖 今週のピックアップ</span>',
     '  <h1 class="pk-title">%s</h1>' % esc(title),
     '  <p class="pk-sub">%s</p>' % esc(SUB)]
P += lede_block("  ")
P += ['  <div class="pk-lede">', br_p(lead, "    "), '  </div>',
      '  <h2 class="pk-h2">今週の主役</h2>']

print("── 主役")
for n, (name, ids) in enumerate(MAIN):
    ss = [t for i in ids for t in week_slots(by_id[i])]
    assert ss, name
    shut = ("%sを閉じる" % name) if len(name) <= 14 else "閉じる"
    q = name
    lst = show_list(ss)
    P += ['  <div class="%s">' % ("pk-act pk-top" if n == 0 else "pk-act"),
          '    <button class="pk-open" type="button" aria-expanded="false">',
          '      <span class="pk-name">%s</span>' % esc(name),
          '      <span class="pk-sale">%s</span>' % esc(sale_label(ss)),
          '    </button>',
          '    <div class="pk-detail" hidden>',
          br_p(paras_of(secs[name]), "      "),
          '      <a class="pk-shows" href="%s">' % esc(q_href(q)),
          '        <b>発売になる公演<span class="pk-go">タップで探す →</span></b>',
          '        %s' % esc(lst),
          '      </a>',
          '      <button class="pk-more pk-close" type="button" data-pk-shut>%s</button>' % esc(shut),
          '    </div>',
          '  </div>']
    print("  %s | %s | 検索「%s」→%d件 | %s" % (name, sale_label(ss), q, search_n(q), lst))

deep = secs["深掘り"]
dtitle, rest = "", []
for ln in deep:
    m = re.match(r"^\*\*(.+?)\*\*$", ln.strip())
    if m and not dtitle:
        dtitle = m.group(1); continue
    rest.append(ln)
TAIL = "他にも気になるアーティストがチケット発売しているわよ。"
assert [x for x in rest if x.strip()][-1].strip() == TAIL
rest = [x for x in rest if x.strip() != TAIL]
print("── 深掘り")
P += ['  <h2 class="pk-h2">今週の深掘り</h2>',
      '  <div class="pk-act">',
      '    <button class="pk-open" type="button" aria-expanded="false">',
      '      <span class="pk-name">%s</span>' % esc(dtitle),
      '    </button>',
      '    <div class="pk-detail" hidden>',
      br_p(paras_of(rest), "      ")]
for i in DEEP_IDS:
    e = by_id[i]
    lst = show_list(week_slots(e))
    P += ['      <a class="pk-shows" href="%s">' % esc(q_href(e["name"])),
          '        <b>%s<span class="pk-go">タップで探す →</span></b>' % esc(DEEP_HEAD),
          '        %s' % esc(lst),
          '      </a>']
    print("  %s | 検索「%s」→%d件 | %s" % (dtitle[:20], e["name"], search_n(e["name"]), lst))
P += ['      <button class="pk-more pk-close" type="button" data-pk-shut>閉じる</button>',
      '    </div>',
      '  </div>',
      '  <p class="pk-others-note">今週はほかにも、こんな名前が出るのよ。</p>',
      '  <div class="pk-others">']
print("── タイル")
assert len(TILES) <= 12
for disp, ids in TILES:
    ds = sorted(set(t["startDate"] for i in ids for t in week_slots(by_id[i])))
    assert ds, disp
    assert all(by_id[i].get("verified") is True for i in ids), disp
    when = "／".join(jp(d) for d in ds[:3]) + ("ほか" if len(ds) > 3 else "")
    P.append('    <a href="%s"><span class="pk-o-name">%s</span><span class="pk-o-when">%s</span></a>'
             % (esc(q_href(disp)), esc(disp), esc(when)))
    print("  %s ids%s | %s | 検索→%d件" % (disp, ids, when, search_n(disp)))
P += ['  </div>',
      '  <a class="pk-tail" href="../?status=urgent">%s<span class="pk-go">今週発売を見る →</span></a>' % esc(TAIL),
      '</article>',
      '</main>',
      '',
      '<script>',
      '  // 主役は1組ずつ開く（index.html の【今週のピックアップ】と同じ動き）',
      '  document.querySelectorAll(".pk-open").forEach(btn => {',
      '    btn.addEventListener("click", () => {',
      '      const d = btn.nextElementSibling;',
      '      const open = btn.getAttribute("aria-expanded") === "true";',
      '      d.hidden = open;',
      '      btn.setAttribute("aria-expanded", String(!open));',
      '    });',
      '  });',
      '  // 読み終わったところの「閉じる」＝閉じたらその組の見出しを画面に出す',
      '  document.querySelectorAll("[data-pk-shut]").forEach(btn => {',
      '    btn.addEventListener("click", () => {',
      '      const act = btn.closest(".pk-act");',
      '      const head = act && act.querySelector(".pk-open");',
      '      const detail = act && act.querySelector(".pk-detail");',
      '      if (!head || !detail) return;',
      '      detail.hidden = true;',
      '      head.setAttribute("aria-expanded", "false");',
      '      const hd = document.querySelector("header");',
      '      const gap = (hd ? hd.getBoundingClientRect().height : 0) + 12;',
      '      const top = head.getBoundingClientRect().top + window.pageYOffset - gap;',
      '      window.scrollTo({ top: Math.max(0, top), behavior: "smooth" });',
      '    });',
      '  });',
      '</script>',
      '',
      '</body>',
      '</html>', '']
page = "\r\n".join(P).replace("\r\r\n", "\r\n")
page = re.sub(r"(?<!\r)\n", "\r\n", page)

io.open(OUT_TOP, "w", encoding="utf-8", newline="").write(top)
io.open(OUT_PAGE, "w", encoding="utf-8", newline="").write(page)

# ── 点検
print("── 点検")
for label, s in (("top", top), ("page", page)):
    body = s[s.index("<body>"):] if "<body>" in s else s
    body_nocss = re.sub(r"<style>.*?</style>|<script>.*?</script>", "", body, flags=re.S)
    print("  [%s] pk-most:%d blockquote:%d &gt;:%d |---:%d ▲▼(本文):%d data-pk-search:%d data-pk-status:%d href=#:%d" % (
        label, body_nocss.count("pk-most"), body_nocss.count("blockquote"), body_nocss.count("&gt;"),
        body_nocss.count("|---"), len(re.findall("[▲▼]", body_nocss)), body_nocss.count("data-pk-search"),
        body_nocss.count("data-pk-status"), body_nocss.count('href="#"')))
    un = len(re.findall(r"。(?!<br>)(?!</p>)(?!」)", body_nocss.replace("わよ。<span", "")))
    print("  [%s] 「。」の未改行:%d 行頭に落ちた」:%d" % (label, un, len(re.findall(r"<br>\s*」", body_nocss))))
    css = (css_all if label == "top" else "") + "".join(re.findall(r"<style>(.*?)</style>", s, re.S))
    used = set(re.findall(r'class="([^"]+)"', body_nocss))
    undefined = sorted({c for u in used for c in u.split() if not re.search(r"\.%s(?![\w-])" % re.escape(c), css)})
    print("  [%s] 未定義クラス: %s" % (label, undefined or "なし"))
print("  gtag: %s" % ("あり" if "googletagmanager.com/gtag/js?id=G-RM1EQ5M4HT" in page else "★無し"))


def text_lines(s):
    s = re.sub(r"<style>.*?</style>|<script>.*?</script>|<head>.*?</head>|<header>.*?</header>", "", s, flags=re.S)
    s = re.sub(r"<br>\s*", "\n", s)
    s = re.sub(r"</(p|span|b|h1|h2|button|a|div)>", "\n", s)
    s = s.replace("<span", "\n<span")   # 締めの一文とボタン（pk-go）を別の行に割る
    s = re.sub(r"<[^>]+>", "", s)
    return [H.unescape(x).strip() for x in s.split("\n") if x.strip()]


def draft_lines(parts):
    out = []
    for ln in parts:
        t = ln.strip()
        if not t or t in ("## 秋のリード", "## 深掘り"):
            continue
        t = re.sub(r"^## ", "", t)
        t = re.sub(r"^\*\*(.+)\*\*$", r"\1", t)
        out.append(t)
    return out


def subseq(need, have):
    it = iter(have)
    miss = [x for x in need if not any(x == y for y in it)]
    return miss


dl = draft_lines(lines)
pl = text_lines(page)
miss = subseq(dl, pl)
extra = [x for x in pl if x not in dl]
print("  本文照合(page): draft %d行 → 順番どおり見つからない行 %d" % (len(dl), len(miss)))
for x in miss[:5]:
    print("    ★", x)
print("  page にあって draft に無い行（ラベル・箱・タイル）: %d" % len(extra))
for x in extra:
    print("    ・", x)
tl = text_lines(top)
need_top = [title] + lede
print("  本文照合(top): %s ／ 余分: %s" % ("一致" if subseq(need_top, tl) == [] else "★ずれ",
                                        [x for x in tl if x not in need_top]))
print("WROTE %s (%d bytes) / %s (%d bytes)" % (OUT_TOP, len(top), OUT_PAGE, len(page)))
