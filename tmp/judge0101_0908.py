# -*- coding: utf-8 -*-
"""27件の「名前は同じだが既存に無い窓がある」候補を1件ずつ突合するための素材出し。

候補の tickets（券種名・締切・startDate・URL）と、
同名の既存エントリ **全部** の tickets を並べて UTF-8 のファイルに書き出す。
eventCd / eventBundleCd も両側から集めて、同じぴあ興行かどうかの機械的な手がかりにする。
"""
import io, re, json, unicodedata, collections


def norm(s):
    s = unicodedata.normalize("NFKC", s or "")
    s = re.sub(r"[\s　]+", "", s)
    s = re.sub(r"[『』「」【】（）\(\)＜＞<>\[\]～〜\-‐−–—・,、.。/／!！?？:：;；\"'”’]", "", s)
    return s.lower()


def cds(e):
    out = set()
    urls = [(e.get("links") or {}).get("pia")]
    urls += [t.get("url") for t in (e.get("tickets") or [])]
    for u in urls:
        if u:
            out |= set(re.findall(r"event(?:Bundle)?Cd=([A-Za-z0-9]+)", u))
    return out


h = io.open("index.html", encoding="utf-8", newline="").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", h, re.S).group(1))
idx = collections.defaultdict(list)
for e in EV:
    idx[norm(e.get("name"))].append(e)

cand = json.load(io.open("tmp/inject0101_addto.json", encoding="utf-8"))

o = io.open("tmp/judge0101_0908.txt", "w", encoding="utf-8")
W = o.write
W("候補 %d 件\n" % len(cand))
for c in cand:
    hits = idx.get(norm(c.get("name")), [])
    ccd = cds(c)
    W("\n" + "=" * 78 + "\n")
    W("[候補] id%s  %s\n" % (c.get("id"), c.get("name")))
    W("  公演日=%s  会場=%s\n" % (c.get("date"), c.get("venue")))
    W("  県=%s  dateLabel=%s\n" % (c.get("prefecture"), c.get("dateLabel")))
    W("  genre=%s/_genre=%s  pia=%s\n" % (c.get("genre"), c.get("_genre"), (c.get("links") or {}).get("pia")))
    W("  cd=%s\n" % ",".join(sorted(ccd)))
    for t in (c.get("tickets") or []):
        W("    - 券種=%s | 締切=%s | 発売=%s | url=%s\n"
          % (t.get("type"), t.get("date"), t.get("startDate"), t.get("url")))
    W("  --- 同名の既存 %d 件 ---\n" % len(hits))
    for e in hits:
        ecd = cds(e)
        W("  [既存] id=%s [%s] 公演日=%s\n" % (e.get("id"), e.get("genre"), e.get("date")))
        W("      会場=%s\n" % e.get("venue"))
        W("      県=%s  dateLabel=%s\n" % (e.get("prefecture"), e.get("dateLabel")))
        W("      pia=%s\n" % ((e.get("links") or {}).get("pia")))
        W("      cd=%s   候補と共通cd=%s\n" % (",".join(sorted(ecd)), ",".join(sorted(ccd & ecd)) or "なし"))
        for t in (e.get("tickets") or []):
            W("        - 券種=%s | 締切=%s | 発売=%s | url=%s\n"
              % (t.get("type"), t.get("date"), t.get("startDate"), t.get("url")))
o.close()
print("wrote tmp/judge0101_0908.txt")
