# -*- coding: utf-8 -*-
"""受付中3,304件から、今日入れる100件を選ぶ。

選び方＝ジャンルの優先順（feedback_harvest_genre_priority）
  ①音楽 ②演劇/ジャズ/クラシック/お笑い ③その他
🚨「締切が近いから捨てる」はしない（2026-09-07にユーザーが縛りを外した）。
🚨 newid は「これまでに使った最大id」+1（削除済みidを再利用しない）。
"""
import io, re, json, collections

N = 100
GJP = {"01": "音楽", "02": "演劇", "03": "スポーツ", "04": "映画",
       "05": "アート", "06": "イベント", "07": "クラシック"}
PRIORITY = ["01", "07", "02", "06", "03", "05", "04"]

cand = json.load(io.open("tmp/sweep0101_cand.json", encoding="utf-8"))

h = io.open("index.html", encoding="utf-8", newline="").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", h, re.S).group(1))
st = json.load(io.open(".claude/state/last_batch.json", encoding="utf-8"))
nid = max([max(e["id"] for e in EV)] + [b.get("id_to", 0) for b in st["batches"]]) + 1


def canon(u):
    m = re.search(r"eventBundleCd=([\w]+)", u or "")
    if m:
        return "https://t.pia.jp/pia/event/event.do?eventBundleCd=%s" % m.group(1)
    m = re.search(r"eventCd=([\w]+)", u or "")
    if m:
        return "https://t.pia.jp/pia/event/event.do?eventCd=%s" % m.group(1)
    return u


by = collections.defaultdict(list)
for c in cand:
    by[c.get("_src", "")].append(c)

picked, seen = [], set()
for lg in PRIORITY:
    for c in by.get(lg, []):
        if len(picked) >= N:
            break
        u = canon(c.get("url"))
        key = re.sub(r".*=", "", u)
        if not key or key in seen:
            continue
        seen.add(key)
        picked.append({"newid": nid, "artist": (c.get("artist") or "").strip(), "urls": [u],
                       "_lg": lg, "_srcg": c.get("_src",""), "_pref": c.get("pref", ""), "_perf": c.get("perfdate", ""),
                       "_name_in_db": bool(c.get("name_in_db"))})
        nid += 1
    if len(picked) >= N:
        break

json.dump([{k: v for k, v in c.items() if not k.startswith("_")} for c in picked],
          io.open("tmp/cand0101_0908.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

o = io.open("tmp/cand0101_0908.txt", "w", encoding="utf-8")
o.write("受付中の未掲載 %d件 → 今日入れる %d件（id %s..%s）\n\n"
        % (len(cand), len(picked), picked[0]["newid"], picked[-1]["newid"]))
cnt = collections.Counter(GJP.get(c.get("_srcg") or c["_lg"], c["_lg"]) for c in picked)
for g, n in cnt.most_common():
    o.write("  %s %d件\n" % (g, n))
o.write("\n同名の既存あり＝%d件（投入前に(県・公演日・締切日)で突合する）\n\n"
        % sum(1 for c in picked if c["_name_in_db"]))
for c in picked:
    o.write("  id=%-6s %-40s %s %s%s\n" % (c["newid"], c["artist"][:40], c["_perf"][:20],
                                           c["_pref"], "  ※同名あり" if c["_name_in_db"] else ""))
o.close()
print("在庫%d → 今日%d件 (id %s..%s) %s"
      % (len(cand), len(picked), picked[0]["newid"], picked[-1]["newid"], dict(cnt)))
