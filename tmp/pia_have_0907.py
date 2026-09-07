# -*- coding: utf-8 -*-
"""OSHINAVIに入っている「ぴあ由来」の数を数える。
ぴあ制覇の分母（ぴあの在庫）と比べるための分子。
"""
import io, re, json, collections

h = io.open("index.html", encoding="utf-8", newline="").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", h, re.S).group(1))

TODAY = "2026-09-07"


def visible(t):
    if t.get("saleUntilSoldOut") or t.get("soldout"):
        return True
    sd, d = t.get("startDate"), t.get("date")
    return not ((not sd or sd <= TODAY) and (d or "") < TODAY)


pia_cd = set()          # 登録済みのぴあ eventCd（ユニーク）
n_pia_entry = 0         # ぴあURLを持つエントリ
n_alive = 0             # うち買える枠があるもの
by_genre = collections.Counter()

for e in EV:
    urls = [(e.get("links") or {}).get("pia")] + [t.get("url") for t in e.get("tickets", [])]
    cds = set()
    for u in urls:
        if u:
            for m in re.finditer(r"event(?:Bundle)?Cd=([a-zA-Z0-9]+)", u):
                cds.add(m.group(1))
    if not cds:
        continue
    pia_cd |= cds
    n_pia_entry += 1
    by_genre[e.get("genre")] += 1
    if any(visible(t) for t in e.get("tickets", [])):
        n_alive += 1

with io.open("tmp/pia_have_0907.txt", "w", encoding="utf-8") as f:
    f.write("=== OSHINAVI に入っているぴあ由来（2026-09-07 夜）===\n")
    f.write("エントリ総数           %d件\n" % len(EV))
    f.write("ぴあURLを持つエントリ  %d件\n" % n_pia_entry)
    f.write("  うち買える枠あり     %d件\n" % n_alive)
    f.write("登録済みの eventCd     %d個（ぴあの1公演＝1eventCd が基本）\n\n" % len(pia_cd))
    f.write("ジャンル別（ぴあ由来のエントリ数）\n")
    for g, c in by_genre.most_common(20):
        f.write("  %-10s %d\n" % (g, c))
print("ぴあ由来 %d件 / eventCd %d個" % (n_pia_entry, len(pia_cd)))
