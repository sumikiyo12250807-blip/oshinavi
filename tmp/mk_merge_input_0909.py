# -*- coding: utf-8 -*-
"""統合行き57件を build_pia_entries に渡せる形にする（既存idごとにURLをまとめる）。
🚨build_pia_entries は複数URLを渡すと各ticketにURLを付けてくれる（1本だけだと付かない）
   ＝統合先に焼き込むときに飛び先が消えないよう、既存のぴあURLも一緒に渡す。"""
import io, json, re, sys, collections
sys.stdout.reconfigure(encoding="utf-8")

cand = json.load(io.open("tmp/merge_cand_0909.json", encoding="utf-8"))
src = io.open("index.html", encoding="utf-8").read()
evs = {e["id"]: e for e in json.loads(re.search(r"const EVENTS = (\[.*?\]);\n", src, re.S).group(1))}

byid = collections.defaultdict(list)
for c in cand:
    byid[c["existing_id"]].append(c["url"])

out = []
for eid, urls in byid.items():
    e = evs[eid]
    have = [(e.get("links") or {}).get("pia")]
    have += [t.get("url") for t in (e.get("tickets") or []) if t.get("url")]
    allurls = list(dict.fromkeys([u for u in have if u and "pia" in u] + urls))
    out.append({"newid": eid, "artist": e.get("artist") or e.get("name"), "urls": allurls})
json.dump(out, io.open("tmp/merge_input_0909.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("統合先 %d エントリ分の入力を作った（URL合計 %d本）"
      % (len(out), sum(len(o["urls"]) for o in out)))
