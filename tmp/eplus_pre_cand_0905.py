# -*- coding: utf-8 -*-
"""e+未登録プールから「これから発売」だけを取り出し、eplus_harvest.py build に渡す候補JSONを作る。

🚨 ネットは叩かない（判定は json の windows の日付だけ）。build 側が実ページを見る。
🚨 eid で重複を潰す（プールは同じ公演が複数行で入っている）。
出力: tmp/eplus_pre_cand_0905.json  … [{"eid":..., "title":...}, ...]
"""
import json, io, re, datetime

SRC = "tmp/_word_pool_miss_0901.json"
OUT = "tmp/eplus_pre_cand_0905.json"
LOG = "tmp/eplus_pre_cand_0905.txt"
TODAY = datetime.date.today()


def parse(s):
    m = re.search(r"(\d{4})[/-](\d{1,2})[/-](\d{1,2})", s or "")
    if not m:
        return None
    try:
        return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


pool = json.load(io.open(SRC, encoding="utf-8"))
h = open("index.html", encoding="utf-8").read()
dbids = set(re.findall(r"/sf/detail/(\d+)", h))

seen, cands, buf = set(), [], []
for it in pool:
    starts = []
    for w in (it.get("windows") or []):
        if isinstance(w, (list, tuple)) and len(w) >= 3:
            s = parse(str(w[1]))
        else:
            ds = re.findall(r"\d{4}[/-]\d{1,2}[/-]\d{1,2}", str(w))
            s = parse(ds[0]) if ds else None
        if s:
            starts.append(s)
    if not starts or min(starts) <= TODAY:
        continue                      # 受付中／終了済みは対象外（今日は「これから発売」だけ）
    eid = str(it.get("eid") or "")
    if not eid or eid in seen:
        continue
    seen.add(eid)
    if eid in dbids:
        buf.append("SKIP 登録済み eid=%s %s" % (eid, it.get("name", "")))
        continue
    cands.append({"eid": eid, "title": it.get("name") or "", "url": it.get("url") or "",
                  "venue": it.get("venue") or "", "pref": it.get("pref") or "",
                  "date": it.get("date") or "", "_rls": min(starts).isoformat()})
    buf.append("%s | 受付開始 %s | %s | %s(%s) | 公演%s"
               % (eid, min(starts).isoformat(), it.get("name", ""), it.get("venue", ""),
                  it.get("pref", ""), it.get("date", "")))

cands.sort(key=lambda c: (c["_rls"], c["date"]))
json.dump(cands, io.open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
io.open(LOG, "w", encoding="utf-8").write(
    "これから発売の候補 %d件（eid重複除去後・登録済み除外後）\n\n" % len(cands) + "\n".join(buf))
print("PRE_CAND=%d -> %s" % (len(cands), OUT))
