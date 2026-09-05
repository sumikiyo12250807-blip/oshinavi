# -*- coding: utf-8 -*-
"""演劇・クラシックのスイープ結果（未掲載）を「同名の既存へ統合する分」と「完全新規」に分ける。

🚨 統合の入力は「そのエントリの**既存ぴあURL全部** ＋ 新URL」を渡す
   （1本だけだと multi=False で ticket.url が刻まれない）。
🚨 同名の既存が2件以上ある／統合先がまだ新着プールにいる／統合先にぴあ枠が1つも無い ものは**保留**。
   （最後のは 2026-09-05 の『ユイカ』『清春』の型＝中身が別の興行でも同名で突き合わせてしまう）
出力:
  tmp/sweep_merge_in_0905.json … 統合用のbuild入力
  tmp/sweep_new_cand_0905.json … 完全新規の候補（idは後で振る）
  tmp/sweep_split_0905.txt     … 保留の理由つき一覧
"""
import re, json, io, unicodedata

SRCS = ["tmp/presale_02_0905.json", "tmp/presale_02lot_0905.json",
        "tmp/presale_07_0905.json", "tmp/presale_07lot_0905.json"]


def norm(s):
    s = unicodedata.normalize("NFKC", s or "")
    return re.sub(r"[\s　・／/＜＞<>「」『』（）()【】’'\"!！\-—]", "", s).lower()


h = open("index.html", encoding="utf-8").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\n", h, re.S).group(1))
by_id = {e["id"]: e for e in EV}

by_name = {}
for e in EV:
    for f in ("artist", "name"):
        if e.get(f):
            by_name.setdefault(norm(e[f]), set()).add(e["id"])

known_cds = set()
for e in EV:
    for t in e.get("tickets", []):
        mm = re.search(r"event(?:Bundle)?Cd=(\w+)", t.get("url") or "")
        if mm:
            known_cds.add(mm.group(1))
    mm = re.search(r"event(?:Bundle)?Cd=(\w+)", (e.get("links") or {}).get("pia") or "")
    if mm:
        known_cds.add(mm.group(1))


def pia_urls(e):
    out = []
    u = (e.get("links") or {}).get("pia")
    if u:
        out.append(u)
    for t in e.get("tickets", []):
        u = t.get("url") or ""
        if "pia.jp" in u:
            out.append(u)
    seen, uniq = set(), []
    for u in out:
        mm = re.search(r"event(?:Bundle)?Cd=(\w+)", u)
        k = mm.group(1) if mm else u
        if k not in seen:
            seen.add(k)
            uniq.append(u)
    return uniq


cands = []
for s in SRCS:
    try:
        d = json.load(io.open(s, encoding="utf-8"))
    except Exception:
        continue
    for x in (d.get("new") or []):
        x["_src"] = d.get("lg")
        cands.append(x)

# 同じ eventCd が複数行に出るので潰す
seen_cd, uniq = set(), []
for x in cands:
    mm = re.search(r"event(?:Bundle)?Cd=(\w+)", x.get("url") or "")
    cd = mm.group(1) if mm else x.get("url")
    if cd in seen_cd or cd in known_cds:
        continue
    seen_cd.add(cd)
    uniq.append(x)

grp = {}
for x in uniq:
    grp.setdefault(x.get("artist") or x.get("name") or "?", []).append(x)

merge_in, new_cand, hold = [], [], []
for artist, xs in sorted(grp.items()):
    ids = sorted(by_name.get(norm(artist), []))
    if not ids:
        new_cand.extend(xs)
        continue
    if len(ids) != 1:
        hold.append("■ %s … 同名の既存が%d件 %s（どれに足すか決められない）" % (artist, len(ids), ids))
        for x in xs:
            hold.append("    候補 %s | %s | %s" % (x.get("perfdate"), x.get("venue"), x.get("url")))
        continue
    e = by_id[ids[0]]
    if e.get("genre") == "new":
        hold.append("■ %s … 統合先 id=%d がまだ新着プールにいる" % (artist, e["id"]))
        continue
    urls = pia_urls(e)
    if not urls:
        hold.append("🚨 %s … 統合先 id=%d に**ぴあ枠が1つも無い**（他社由来）。中身が別の興行かもしれないので保留"
                    % (artist, e["id"]))
        for x in xs:
            hold.append("    候補 %s | %s | %s" % (x.get("perfdate"), x.get("venue"), x.get("url")))
        continue
    merge_in.append({"newid": e["id"], "artist": e.get("artist") or artist,
                     "urls": urls + [x["url"] for x in xs],
                     "_existing": len(urls), "_added": len(xs)})

json.dump(merge_in, io.open("tmp/sweep_merge_in_0905.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(new_cand, io.open("tmp/sweep_new_cand_0905.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
io.open("tmp/sweep_split_0905.txt", "w", encoding="utf-8").write("\n".join(hold))
print("UNIQ=%d  MERGE=%d(URL%d)  NEW=%d  HOLD_LINES=%d"
      % (len(uniq), len(merge_in), sum(len(b["urls"]) for b in merge_in), len(new_cand), len(hold)))
