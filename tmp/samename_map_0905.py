# -*- coding: utf-8 -*-
"""同名候補70件について、突き合わせ先の既存エントリ id を特定する（昼の統合作業の材料）。
正規化名で index.html を引き、候補URLが既に登録済みかも見る。ネットは叩かない。"""
import re, json, io, unicodedata

SRC = "tmp/presale_01_0905.json"
OUT = "tmp/samename_map_0905.txt"


def norm(s):
    s = unicodedata.normalize("NFKC", s or "")
    return re.sub(r"[\s　・／/＜＞<>「」『』（）()【】’'\"!！\-—]", "", s).lower()


h = open("index.html", encoding="utf-8").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\n", h, re.S).group(1))

by_name = {}
for e in EV:
    for f in ("artist", "name"):
        if e.get(f):
            by_name.setdefault(norm(e[f]), []).append(e)

known_cds = set()
for e in EV:
    for t in e.get("tickets", []):
        mm = re.search(r"event(?:Bundle)?Cd=(\w+)", t.get("url") or "")
        if mm:
            known_cds.add(mm.group(1))
    mm = re.search(r"event(?:Bundle)?Cd=(\w+)", (e.get("links") or {}).get("pia") or "")
    if mm:
        known_cds.add(mm.group(1))

cands = [x for x in json.load(io.open(SRC, encoding="utf-8"))["new"] if x.get("name_in_db")]
grp = {}
for x in cands:
    grp.setdefault(x["artist"], []).append(x)

buf = ["同名候補 %d件 / %dアーティスト → 統合先の既存エントリ" % (len(cands), len(grp)), ""]
nomatch = 0
already = 0
for artist, xs in sorted(grp.items()):
    hits = by_name.get(norm(artist), [])
    buf.append("■ %s … 候補%d件 / 既存%d件" % (artist, len(xs), len(hits)))
    for e in hits:
        buf.append("    既存 id=%-5s %s | %s | date=%s | genre=%s | 枠%d"
                   % (e["id"], e.get("name", ""), e.get("venue", "")[:34], e.get("date"),
                      e.get("genre"), len(e.get("tickets", []))))
    if not hits:
        nomatch += 1
    for x in xs:
        mm = re.search(r"event(?:Bundle)?Cd=(\w+)", x.get("url") or "")
        cd = mm.group(1) if mm else "?"
        dup = cd in known_cds
        if dup:
            already += 1
        buf.append("    候補 %s %s | %s | 発売%s | %s%s"
                   % (x.get("saletype", ""), x.get("perfdate", ""), x.get("venue", ""),
                      x.get("rlsdate", ""), x.get("url", ""), "  ← 既に登録済みのeventCd" if dup else ""))
    buf.append("")

io.open(OUT, "w", encoding="utf-8").write("\n".join(buf))
print("ARTISTS=%d NOMATCH=%d ALREADY_REGISTERED_CD=%d -> %s" % (len(grp), nomatch, already, OUT))
