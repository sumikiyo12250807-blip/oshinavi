# -*- coding: utf-8 -*-
"""記事の下書きに書かれた事実を、index.html の現物と突き合わせる。

見るもの：
  ① 本文に出てくる「◯◯ M/D公演」が、そのエントリの券種名に実在するか
  ② 曜日が実カレンダーと合っているか
  ③ 本文に出てくる会場名が、そのエントリの venue に入っているか
  ④ 発売日時（9/12(土)10:00）が枠と一致するか
"""
import json, re, io, datetime

MAIN = {"MONO NO AWARE": 4500, "ASKA": 4489, "東京スカパラダイスオーケストラ": 4236,
        "佐藤竹善": 668, "湖月わたる": 4246}
WD = "月火水木金土日"

html = io.open("index.html", encoding="utf-8", newline="").read()
events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", html, re.S).group(1))
by_id = {e.get("id"): e for e in events}
draft = io.open("tmp/pickup0906/draft.md", encoding="utf-8").read()

# 節ごとに割る
secs = {}
cur = "（導入）"
for ln in draft.split("\n"):
    m = re.match(r"^## (.+)$", ln)
    if m:
        cur = m.group(1).strip(); secs[cur] = []
    else:
        secs.setdefault(cur, []).append(ln)

ng, ok = [], []

# ① ②「◯◯ M/D公演」「R9年 M/D公演」の実在と曜日
for name, eid in MAIN.items():
    e = by_id[eid]
    types = " ".join(t.get("type", "") for t in e.get("tickets", []))
    body = "\n".join(secs.get(name, []))
    if not body:
        ng.append("本文に「%s」の節が無い" % name); continue
    # 🚨県名は47都道府県のリストで判定する。素の「[一-龥]+」だと直前の日本語まで
    #   飲み込んで（例「初日にあたる大阪」）誤検出になる。
    PREF = ("北海道|青森|岩手|宮城|秋田|山形|福島|茨城|栃木|群馬|埼玉|千葉|東京|神奈川|"
            "新潟|富山|石川|福井|山梨|長野|岐阜|静岡|愛知|三重|滋賀|京都|大阪|兵庫|奈良|和歌山|"
            "鳥取|島根|岡山|広島|山口|徳島|香川|愛媛|高知|福岡|佐賀|長崎|熊本|大分|宮崎|鹿児島|沖縄")
    found = re.findall(r"((?:%s)(?:・(?:%s))*)\s+((?:R9年\s*)?\d{1,2}/\d{1,2}(?:〜(?:R9年\s*)?\d{1,2}/\d{1,2})?)公演"
                       % (PREF, PREF), body)
    for pref, d in found:
        key = "%s %s公演" % (pref, d)
        if key in types:
            ok.append("%s: 「%s」は券種名に実在" % (name, key))
        else:
            ng.append("🚨%s: 「%s」が券種名に無い＝書き換えられている疑い" % (name, key))

# ③ 会場名
for name, eid in MAIN.items():
    e = by_id[eid]
    ven = e.get("venue") or ""
    body = "\n".join(secs.get(name, []))
    for hall in re.findall(r"([A-Za-z][A-Za-z0-9'’\. ]{3,28}|[一-龥ぁ-んァ-ヶ]{3,14}(?:ホール|会館|劇場|座))", body):
        h = hall.strip()
        if len(h) < 4 or h in ("Passion Tours", "Show Time"):
            continue
        if h in ven:
            ok.append("%s: 会場「%s」はvenueに実在" % (name, h))

# ④ 発売日時
for name, eid in MAIN.items():
    e = by_id[eid]
    body = "\n".join(secs.get(name, []))
    for m in re.finditer(r"(\d{1,2})/(\d{1,2})\((.)\)\s*(\d{1,2}:\d{2})", body):
        mo, da, w, tm = int(m.group(1)), int(m.group(2)), m.group(3), m.group(4)
        real = WD[datetime.date(2026, mo, da).weekday()]
        if real != w:
            ng.append("🚨%s: %d/%d は(%s)なのに本文は(%s)" % (name, mo, da, real, w))
        else:
            ok.append("%s: %d/%d(%s) 曜日OK" % (name, mo, da, w))
        want = "%d/%d %s発売" % (mo, da, tm)
        if any(want in (t.get("type") or "") for t in e.get("tickets", [])):
            ok.append("%s: 「%s」は枠に実在" % (name, want))
        else:
            ng.append("🚨%s: 「%s」が枠に無い" % (name, want))

print("=== 記事の事実照合 ===")
print("照合できた項目 %d / 疑い %d" % (len(ok), len(ng)))
print()
for x in ng:  # 出力はファイルへ（コンソールはcp932で落ちる）
    pass
io.open("tmp/pickup0906/verify_draft.txt", "w", encoding="utf-8").write(
    "【OK】\n" + "\n".join(ok) + "\n\n【疑い】\n" + "\n".join(ng))
print()
print("詳細 -> tmp/pickup0906/verify_draft.txt")
