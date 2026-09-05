# -*- coding: utf-8 -*-
"""e+未登録プールのうち「これから発売」ぶんを、eplus_harvest.py build の入力形にする。
build は c['title'] と c['eid'] しか見ない（eid から実ページを取り直して JSON-LD で組む）。

  python tmp/eplus_cand_0905.py            # 「これから発売」だけ
  python tmp/eplus_cand_0905.py --all      # 受付中も含める
"""
import json, io, re, sys, datetime

SRC = "tmp/_word_pool_miss_0901.json"
OUT = "tmp/eplus_live_cand_0905.json"
TODAY = datetime.date.today()


def parse(s):
    m = re.search(r"(\d{4})[/-](\d{1,2})[/-](\d{1,2})", str(s) or "")
    if not m:
        return None
    try:
        return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


pool = json.load(io.open(SRC, encoding="utf-8"))
out, seen = [], set()
for it in pool:
    starts, ends = [], []
    for w in (it.get("windows") or []):
        if isinstance(w, (list, tuple)) and len(w) >= 3:
            s, e = parse(w[1]), parse(w[2])
            if s:
                starts.append(s)
            if e:
                ends.append(e)
    pre = bool(starts) and min(starts) > TODAY
    live = bool(ends) and max(ends) >= TODAY
    if not (pre or ("--all" in sys.argv and live)):
        continue
    eid = it.get("eid")
    if not eid or eid in seen:
        continue
    seen.add(eid)
    out.append({"title": it.get("name") or "", "eid": eid, "url": it.get("url") or "",
                "date": it.get("date") or "", "venue": it.get("venue") or "",
                "pref": it.get("pref") or "", "in_db": False})

json.dump(out, io.open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("EPLUS_CAND=%d -> %s" % (len(out), OUT))
