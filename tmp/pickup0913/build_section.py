# -*- coding: utf-8 -*-
"""draft.md → index.html に差し込める section HTML（9/13号）。
形は前号（tmp/pickup0906/build_section.py）と同じ。違いは
- サントリーホールの年末年始＝4つのエントリをまとめた1枚。「発売になる公演」の箱を4つ（プログラムごとに探せる）
- 主役の見出しの発売日は「先行／一般」を分けて書く（先行だけの日を「一般発売」と書かない）
- 「閉じる」ボタンは名前が14文字を超えたら「閉じる」だけ（前号は「閉じるを閉じる」になっていた）
🚨「。」のあとは必ず <br>／▲▼は書かない／pk-most は使わない
"""
import datetime, html as H, io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

DRAFT = "tmp/pickup0913/draft.md"
OUT = "tmp/pickup0913/section.html"
FROM, TO = "2026-09-14", "2026-09-20"
WD = "月火水木金土日"
MAIN = [("ヨーヨー・マ", [7324]),
        ("サントリーホールの年末年始", [4771, 4772, 4850, 4845]),
        ("女王蜂", [4802]),
        ("GENERATIONS from EXILE TRIBE", [3568]),
        ("劇団四季『コーラスライン』", [4898])]
# サントリーホールの「発売になる公演」の箱の見出し（本文と同じ呼び名）
SHORT = {4771: "12/24 聖夜のメサイア", 4772: "12/25 サントリーホールのクリスマス 2026",
         4850: "12/31 ウィーンの大みそか", 4845: "1/1〜1/3 ニューイヤー・コンサート"}
TILE_NAMES = ["柴咲コウ", "さだまさし", "平原綾香", "坂本冬美", "中村雅俊", "一青窈", "Juice=Juice",
              "アンジュルム", "access", "リーガルリリー", "syrup16g", "小野リサ"]
TILE_IDS = [2159, 1, 729, 549, 1634, 5717, 4538, 4490, 4793, 5201, 5526, 523, 4960, None]  # 最後＝BTTF（名前で引く）

html = io.open("index.html", encoding="utf-8", newline="").read()
events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", html, re.S).group(1))
by_id = {e["id"]: e for e in events}
bttf = [e for e in events if e.get("name") == "劇団四季『バック・トゥ・ザ・フューチャー』東京公演"]
assert len(bttf) == 1, len(bttf)
TILE_IDS[-1] = bttf[0]["id"]
draft = io.open(DRAFT, encoding="utf-8").read()


def esc(t):
    return H.escape(t, quote=True)


def br(paras):
    out = []
    for p in paras:
        t = esc(p.strip()).replace("。", "。<br>")
        t = re.sub(r"(<br>)+$", "", t)
        out.append("        <p>%s</p>" % t)
    return "\n".join(out)


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


def show_list(ss):
    seen, out = set(), []
    for t in ss:
        m = re.search(r"（(.+?)\s*((?:R9年\s*)?[\d/〜]+(?:R9年\s*[\d/]+)?)公演", t.get("type", ""))
        if not m:
            continue
        lab = "%s %s" % (m.group(2).strip(), m.group(1).strip())
        if lab not in seen:
            seen.add(lab); out.append(lab)
    return "／".join(out)


def sale_label(ss):
    def part(xs):
        ds = sorted(set(t["startDate"] for t in xs))
        tms = sorted(set(re.search(r"(\d{1,2}:\d{2})発売", t["type"]).group(1) for t in xs))
        return "／".join(jp(d) for d in ds) + (" " + tms[0] if len(tms) == 1 else "")
    gen = [t for t in ss if t["type"].startswith("一般発売")]
    pre = [t for t in ss if not t["type"].startswith("一般発売")]
    if pre and gen:
        return "先行 %s・一般 %s" % (part(pre), part(gen))
    return "%s %s" % (part(gen or pre), "一般発売" if gen else "先行")


def search_ok(q):
    """その語で探したとき、何件のカードが出るか（artist+name の部分一致＝画面と同じ判定）"""
    return sum(1 for e in events if q.lower() in (e.get("artist", "") + " " + e.get("name", "")).lower())


lines = draft.split("\n")
title = lines[0].strip()
secs, cur = {}, "（導入）"
for ln in lines[1:]:
    m = re.match(r"^## (.+)$", ln)
    if m:
        cur = m.group(1).strip(); secs[cur] = []
    else:
        secs.setdefault(cur, []).append(ln)
lede = [x for x in secs["（導入）"] if x.strip()]


def paras_of(body):
    out, cur2 = [], []
    for ln in body:
        if ln.strip():
            cur2.append(ln.strip())
        elif cur2:
            out.append("\n".join(cur2)); cur2 = []
    if cur2:
        out.append("\n".join(cur2))
    return out


B = ['<section class="pickup" id="pickup">',
     '  <span class="pk-label">📖 今週のピックアップ</span>',
     '  <h2 class="pk-title">%s</h2>' % esc(title),
     '  <p class="pk-sub">9/14(月)〜9/20(日)にチケットの発売が始まるアーティスト紹介</p>',
     '  <div class="pk-lede">']
for i, p in enumerate(lede):
    B.append('    <p%s>%s</p>' % (' class="pk-tease"' if i == len(lede) - 1 else "", esc(p.strip())))
B += ['  </div>',
      '  <button class="pk-more" id="pickupMore" type="button" aria-expanded="false" '
      'aria-controls="pickupBody">今週の主役を読む</button>',
      '  <div class="pk-body" id="pickupBody" hidden>',
      '      <h3 class="pk-h2">今週の主役</h3>']

print("── 主役")
for n, (name, ids) in enumerate(MAIN):
    body = secs[name]
    ss_all = [t for i in ids for t in week_slots(by_id[i])]
    shut = ("%sを閉じる" % name) if len(name) <= 14 else "閉じる"
    B += ['      <div class="%s">' % ("pk-act pk-top" if n == 0 else "pk-act"),
          '        <button class="pk-open" type="button" aria-expanded="false">',
          '          <span class="pk-name">%s</span>' % esc(name),
          '          <span class="pk-sale">%s</span>' % esc(sale_label(ss_all)),
          '        </button>',
          '        <div class="pk-detail" hidden>',
          br(paras_of(body))]
    for i in ids:
        e = by_id[i]
        q = e["artist"] if len(ids) == 1 else e["name"]
        if name.startswith("劇団四季"):
            q = "コーラスライン"
        lst = show_list(week_slots(e))
        head = "発売になる公演" if len(ids) == 1 else esc(SHORT[i])
        B += ['        <a class="pk-shows" href="#" data-pk-search="%s">' % esc(q),
              '          <b>%s<span class="pk-go">タップで探す →</span></b>' % head,
              '          %s' % esc(lst),
              '        </a>']
        print("  %s | 検索語「%s」→ %d件 | %s" % (name, q, search_ok(q), lst))
    B += ['        <button class="pk-more pk-close" type="button" data-pk-shut>%s</button>' % esc(shut),
          '        </div>',
          '      </div>']

deep = secs["今週の深掘り"]
dtitle, rest = "", []
for ln in deep:
    m = re.match(r"^\*\*(.+?)\*\*$", ln.strip())
    if m and not dtitle:
        dtitle = m.group(1); continue
    rest.append(ln)
B += ['      <h3 class="pk-h2">今週の深掘り</h3>',
      '      <div class="pk-act">',
      '        <button class="pk-open" type="button" aria-expanded="false">',
      '          <span class="pk-name">%s</span>' % esc(dtitle),
      '        </button>',
      '        <div class="pk-detail" hidden>',
      br(paras_of([x for x in rest if not x.startswith("他にも気になる")])),
      '        <button class="pk-more pk-close" type="button" data-pk-shut>閉じる</button>',
      '        </div>',
      '      </div>',
      '      <p class="pk-others-note">今週はほかにも、こんな名前が出るのよ。</p>',
      '      <div class="pk-others">']
print("── タイル")
for i in TILE_IDS:
    e = by_id[i]
    ds = sorted(set(t["startDate"] for t in week_slots(e)))
    assert ds, (i, e["name"])
    when = "／".join(jp(d) for d in ds[:3]) + ("ほか" if len(ds) > 3 else "")
    disp = e["name"]
    B.append('        <a href="#" data-pk-search="%s"><span class="pk-o-name">%s</span>'
             '<span class="pk-o-when">%s</span></a>' % (esc(disp), esc(disp), esc(when)))
    print("  id%s %s | %s | 検索→%d件" % (i, disp, when, search_ok(disp)))
B += ['      </div>',
      '      <a class="pk-tail" href="#" data-pk-status="urgent">他にも気になるアーティストがチケット発売しているわよ。'
      '<span class="pk-go">今週発売を見る →</span></a>',
      '      <button class="pk-more pk-close" id="pickupClose" type="button" aria-controls="pickupBody">折りたたむ</button>',
      '  </div>',
      '</section>']
s = "\r\n".join(B)
io.open(OUT, "w", encoding="utf-8", newline="").write(s)
# 組んだ直後の点検（memory project_weekly_pickup_article の8項目）
css = html[html.index("<style"):html.index("</style>")]
used = set(re.findall(r'class="([^"]+)"', s))
undefined = sorted({c for u in used for c in u.split() if "." + c not in css})
print("── 点検")
print("  pk-most:%d blockquote:%d &gt;:%d |---:%d ▲▼:%d" % (s.count("pk-most"), s.count("blockquote"),
      s.count("&gt;"), s.count("|---"), len(re.findall("[▲▼]", s))))
print("  pickupClose:%d / data-pk-shut=%d pk-act=%d" % (s.count('id="pickupClose"'), s.count("data-pk-shut"),
      len(re.findall(r'class="pk-act', s))))
print("  未定義クラス:", undefined or "なし")
print("  「。」の未改行:", len(re.findall(r"。(?!<br>)(?!</p>)", s.replace("わよ。<span", ""))))
print("WROTE %s (%d bytes)" % (OUT, len(s)))
