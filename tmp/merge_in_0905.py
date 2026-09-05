# -*- coding: utf-8 -*-
"""同名候補70件を既存エントリへ統合するための build_pia_entries 入力を作る。

🚨 入力は「そのエントリの**既存ぴあURL全部** ＋ 今日の新URL」を渡す
   （feedback_build_pia_multiurl_loses_ticket_url＝1本だけ渡すと multi=False になり
    ticket.url が1つも刻まれず、別会場の枠が「その枠を売っていないページ」に飛ぶ）。
🚨 同名の既存エントリが2つ以上ある／新着プールにある ものは自動で決めずに保留にする。
"""
import re, json, io, unicodedata

SRC = "tmp/presale_01_0905.json"
OUT = "tmp/merge_in_0905.json"
HOLD = "tmp/merge_hold_0905.txt"


def norm(s):
    s = unicodedata.normalize("NFKC", s or "")
    return re.sub(r"[\s　・／/＜＞<>「」『』（）()【】’'\"!！\-—]", "", s).lower()


h = open("index.html", encoding="utf-8").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\n", h, re.S).group(1))

by_name = {}
for e in EV:
    for f in ("artist", "name"):
        if e.get(f):
            by_name.setdefault(norm(e[f]), set()).add(e["id"])
by_id = {e["id"]: e for e in EV}


def pia_urls(e):
    out = []
    u = (e.get("links") or {}).get("pia")
    if u:
        out.append(u)
    for t in e.get("tickets", []):
        u = t.get("url") or ""
        if "pia.jp" in u:
            out.append(u)
    # eventCd/eventBundleCd で重複を潰す（ホスト違いの同一ページを1本に）
    seen, uniq = set(), []
    for u in out:
        mm = re.search(r"event(?:Bundle)?Cd=(\w+)", u)
        k = mm.group(1) if mm else u
        if k not in seen:
            seen.add(k)
            uniq.append(u)
    return uniq


cands = [x for x in json.load(io.open(SRC, encoding="utf-8"))["new"] if x.get("name_in_db")]
grp = {}
for x in cands:
    grp.setdefault(x["artist"], []).append(x)

build_in, hold = [], []
for artist, xs in sorted(grp.items()):
    ids = sorted(by_name.get(norm(artist), []))
    if len(ids) != 1:
        hold.append("■ %s … 既存が%d件 %s（どれに足すか決められないので保留）" % (artist, len(ids), ids))
        for x in xs:
            hold.append("    候補 %s %s | %s | %s" % (x.get("saletype"), x.get("perfdate"), x.get("venue"), x.get("url")))
        continue
    e = by_id[ids[0]]
    if e.get("genre") == "new":
        hold.append("■ %s … 統合先 id=%d がまだ新着プールにいるので保留" % (artist, e["id"]))
        continue
    urls = pia_urls(e)
    newu = [x["url"] for x in xs]
    have = set()
    for u in urls:
        mm = re.search(r"event(?:Bundle)?Cd=(\w+)", u)
        if mm:
            have.add(mm.group(1))
    add = []
    for u in newu:
        mm = re.search(r"event(?:Bundle)?Cd=(\w+)", u)
        if mm and mm.group(1) not in have:
            add.append(u)
            have.add(mm.group(1))
    if not add:
        hold.append("■ %s … 新URLが既に登録済み（統合不要）" % artist)
        continue
    build_in.append({"newid": e["id"], "artist": e.get("artist") or artist, "urls": urls + add,
                     "_existing": len(urls), "_added": len(add)})

json.dump(build_in, io.open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
io.open(HOLD, "w", encoding="utf-8").write("\n".join(hold))
print("MERGE_TARGETS=%d (URL合計 %d) / HOLD_LINES=%d -> %s"
      % (len(build_in), sum(len(b["urls"]) for b in build_in), len(hold), OUT))
