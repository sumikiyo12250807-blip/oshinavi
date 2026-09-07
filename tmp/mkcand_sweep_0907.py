# -*- coding: utf-8 -*-
"""総ざらいで出た未登録27件（重複あり）を投入候補にする。

🚨 同じ eventCd が複数の組で出る（博多・天神落語まつり／大名古屋らくご祭 など）ので
   eventCd でユニークにする。
🚨 URLは kwsweep の出力から機械で抜く（手で写さない）。
🚨 newid は「これまでに使った最大id」+1 から＝現物の最大id+1 だと削除済みidを再利用してしまう。
"""
import io, re, json

src = io.open("tmp/kwsweep_0907.txt", encoding="utf-8").read()

h = io.open("index.html", encoding="utf-8", newline="").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", h, re.S).group(1))
st = json.load(io.open(".claude/state/last_batch.json", encoding="utf-8"))
nid = max([max(e["id"] for e in EV)] + [b.get("id_to", 0) for b in st["batches"]]) + 1

seen, cand = set(), []
for m in re.finditer(r"🚨 (\w+)\n\s*\[(.*?)\] (.*?)\n\s*(.*?)\n\s*(\S+)\n", src):
    cd, state, name, when, url = m.groups()
    if cd in seen:
        continue
    seen.add(cd)
    cand.append({"newid": nid, "artist": name.strip(),
                 "urls": ["https://t.pia.jp/pia/event/event.do?event%sCd=%s"
                          % ("Bundle" if cd.startswith("b") else "", cd)],
                 "_when": when.strip()})
    nid += 1

json.dump([{k: v for k, v in c.items() if not k.startswith("_")} for c in cand],
          io.open("tmp/cand_sweep_0907.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

with io.open("tmp/cand_sweep_0907.txt", "w", encoding="utf-8") as f:
    f.write("=== 投入候補 %d件（id %s..%s）===\n" % (len(cand), cand[0]["newid"], cand[-1]["newid"]))
    for c in cand:
        f.write("  id=%-6s %-46s %s\n" % (c["newid"], c["artist"][:46], c["_when"][:40]))
print("未登録27件 → eventCdでユニーク化して %d件" % len(cand))
