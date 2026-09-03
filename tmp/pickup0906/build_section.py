# -*- coding: utf-8 -*-
"""draft.md（Fableが書いた本文）を、index.html に差し込める section HTML に組む。

構造は前号（tmp/pickup0906/prev_section.html）と同じ：
  pk-label / pk-title / pk-sub / pk-lede(3行・最後がpk-tease) / pk-more(id=pickupMore)
  → pk-body(id=pickupBody)
      pk-h2「今週の主役」→ pk-act × 5（最初だけ pk-act pk-top）
      pk-h2「今週の深掘り」→ pk-act × 1
      pk-others（名前タイル12組）
      pk-tail（締め）→ pk-more pk-close(id=pickupClose)

🚨「。」のあとは必ず <br>（apply_pickup.py がそこで落ちる）
🚨▲▼は書かない（CSSの ::after が足す）
🚨pk-most は使わない（本文の箱は pk-act + pk-detail）
"""
import json, re, io, datetime, html as H

DRAFT = "tmp/pickup0906/draft.md"
OUT = "tmp/pickup0906/section.html"
MAIN = [("MONO NO AWARE", 4500), ("ASKA", 4489), ("東京スカパラダイスオーケストラ", 4236),
        ("佐藤竹善", 668), ("湖月わたる", 4246)]
TILES = [("ブギ連 ブギる心～外伝", 6060), ("HIZAKI TOUR 2026「ASTRAIA」", 6003),
         ("天満天神繁昌亭", 950), ("kobore", 4228), ("DYGL", 4235), ("川崎鷹也", 4227),
         ("ヤミテラ", 5993), ("Sick2", 6009), ("矢野顕子", 4103),
         ("令和八年 冬巡業 大相撲三田場所", 6141), ("THE BAWDIES", 4230), ("アンジュルム", 4490)]
FROM, TO = "2026-09-07", "2026-09-13"
WD = "月火水木金土日"

html = io.open("index.html", encoding="utf-8", newline="").read()
events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", html, re.S).group(1))
by_id = {e.get("id"): e for e in events}
draft = io.open(DRAFT, encoding="utf-8").read()


def esc(t):
    return H.escape(t, quote=True)


def br(paras):
    """段落ごとに <p>…</p>。「。」のあとに <br> を入れる（末尾は除く）。"""
    out = []
    for p in paras:
        p = p.strip()
        if not p:
            continue
        t = esc(p)
        t = t.replace("。", "。<br>")
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


def show_list(e):
    """pk-shows の中身＝「県 M/D公演」を券種名から機械で抜いて並べる（会場は本文で触れている）"""
    seen, out = set(), []
    for t in week_slots(e):
        m = re.search(r"（(.+?)\s*((?:R9年\s*)?[\d/〜]+(?:R9年\s*[\d/]+)?)公演）", t.get("type", ""))
        if not m:
            continue
        lab = "%s %s" % (m.group(2).strip(), m.group(1).strip())
        if lab not in seen:
            seen.add(lab); out.append(lab)
    return "／".join(out)


def sale_label(e):
    ss = week_slots(e)
    ds = sorted(set(t.get("startDate") for t in ss))
    tms = sorted(set(re.search(r"(\d{1,2}:\d{2})発売", t["type"]).group(1)
                     for t in ss if re.search(r"(\d{1,2}:\d{2})発売", t["type"])))
    return "%s%s 一般発売" % ("／".join(jp(d) for d in ds), tms[0] if len(tms) == 1 else "")


# ── draft.md を節に割る
lines = draft.split("\n")
title = lines[0].strip()
secs, cur = {}, "（導入）"
for ln in lines[1:]:
    m = re.match(r"^## (.+)$", ln)
    if m:
        cur = m.group(1).strip(); secs[cur] = []
    else:
        secs.setdefault(cur, []).append(ln)
lede = [x for x in secs.get("（導入）", []) if x.strip()]

B = []
B.append('<section class="pickup" id="pickup">')
B.append('  <span class="pk-label">📖 今週のピックアップ</span>')
B.append('  <h2 class="pk-title">%s</h2>' % esc(title))
B.append('  <p class="pk-sub">9/7(月)〜9/13(日)にチケットの発売が始まるアーティスト紹介</p>')
B.append('  <div class="pk-lede">')
for i, p in enumerate(lede):
    cls = ' class="pk-tease"' if i == len(lede) - 1 else ""
    B.append('    <p%s>%s</p>' % (cls, esc(p.strip())))
B.append('  </div>')
B.append('  <button class="pk-more" id="pickupMore" type="button" aria-expanded="false" '
         'aria-controls="pickupBody">今週の主役を読む</button>')
B.append('  <div class="pk-body" id="pickupBody" hidden>')
B.append('      <h3 class="pk-h2">今週の主役</h3>')

for n, (name, eid) in enumerate(MAIN):
    e = by_id[eid]
    body = secs.get(name, [])
    paras = []
    cur2 = []
    for ln in body:
        if ln.strip():
            cur2.append(ln.strip())
        elif cur2:
            paras.append("\n".join(cur2)); cur2 = []
    if cur2:
        paras.append("\n".join(cur2))
    cls = "pk-act pk-top" if n == 0 else "pk-act"
    shut = name if len(name) <= 14 else "閉じる"
    B.append('      <div class="%s">' % cls)
    B.append('        <button class="pk-open" type="button" aria-expanded="false">')
    B.append('          <span class="pk-name">%s</span>' % esc(name))
    B.append('          <span class="pk-sale">%s</span>' % esc(sale_label(e)))
    B.append('        </button>')
    B.append('        <div class="pk-detail" hidden>')
    B.append(br(paras))
    B.append('        <a class="pk-shows" href="#" data-pk-search="%s">' % esc(name))
    B.append('          <b>発売になる公演<span class="pk-go">タップで探す →</span></b>')
    B.append('          %s' % esc(show_list(e)))
    B.append('        </a>')
    B.append('        <button class="pk-more pk-close" type="button" data-pk-shut>%sを閉じる</button>'
             % esc(shut))
    B.append('        </div>')
    B.append('      </div>')

# 深掘り
deep = secs.get("今週の深掘り", [])
dtitle = ""
dparas, cur2 = [], []
for ln in deep:
    m = re.match(r"^\*\*(.+?)\*\*$", ln.strip())
    if m and not dtitle:
        dtitle = m.group(1); continue
    if ln.strip():
        cur2.append(ln.strip())
    elif cur2:
        dparas.append("\n".join(cur2)); cur2 = []
if cur2:
    dparas.append("\n".join(cur2))
B.append('      <h3 class="pk-h2">今週の深掘り</h3>')
B.append('      <div class="pk-act">')
B.append('        <button class="pk-open" type="button" aria-expanded="false">')
B.append('          <span class="pk-name">%s</span>' % esc(dtitle or "MONO NO AWARE「Passion Tours」"))
B.append('        </button>')
B.append('        <div class="pk-detail" hidden>')
B.append(br(dparas))
B.append('        <button class="pk-more pk-close" type="button" data-pk-shut>閉じる</button>')
B.append('        </div>')
B.append('      </div>')

# 名前タイル
B.append('      <p class="pk-others-note">今週はほかにも、こんな名前が出るのよ。</p>')
B.append('      <div class="pk-others">')
for name, eid in TILES:
    e = by_id.get(eid)
    if not e:
        continue
    ss = week_slots(e)
    ds = sorted(set(t.get("startDate") for t in ss))
    when = "／".join(jp(d) for d in ds[:3]) + ("ほか" if len(ds) > 3 else "")
    disp = e.get("name") or name
    B.append('        <a href="#" data-pk-search="%s"><span class="pk-o-name">%s</span>'
             '<span class="pk-o-when">%s</span></a>' % (esc(disp), esc(disp), esc(when)))
B.append('      </div>')

B.append('      <a class="pk-tail" href="#" data-pk-status="urgent">'
         '他にも気になるアーティストがチケット発売しているわよ。'
         '<span class="pk-go">今週発売を見る →</span></a>')
B.append('      <button class="pk-more pk-close" id="pickupClose" type="button" '
         'aria-controls="pickupBody">折りたたむ</button>')
B.append('  </div>')
B.append('</section>')

io.open(OUT, "w", encoding="utf-8", newline="").write("\r\n".join(B))
print("WROTE %s  (%d bytes)" % (OUT, len("\r\n".join(B))))
print("主役=%d / タイル=%d" % (len(MAIN), len(TILES)))
