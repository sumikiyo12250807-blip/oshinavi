# -*- coding: utf-8 -*-
"""御園座で見つかった未登録4件（全部べつの公演）を投入候補にする。
🚨 URLは kwgap の出力から機械で抜く（手で写さない）。newid は現物の最大id+1から。
"""
import io, re, json

src = io.open("tmp/kwgap_0907.txt", encoding="utf-8").read()
sec = src.split("=== tmp/kw_misono_0907.txt ===")[1]

h = io.open("index.html", encoding="utf-8", newline="").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", h, re.S).group(1))

# 🚨 現物の最大id+1 では**削除済みidを再利用してしまう**（欠番は詰めない＝
#    feedback_candidate_list_stable_numbering）。今朝 7160/7161 を消したので
#    現物の最大は 7159 だが、次に使ってよいのは 7162。
#    「これまでに使った最大id」は .claude/state/last_batch.json に残っている。
st = json.load(io.open(".claude/state/last_batch.json", encoding="utf-8"))
nid = max([max(e["id"] for e in EV)] + [b.get("id_to", 0) for b in st["batches"]]) + 1

cand = []
for m in re.finditer(r"🚨未登録 (\w+)\n\s*\[(.*?)\] (.*?)\n\s*(.*?)\n\s*(\S+)\n", sec):
    cd, state, name, when, url = m.groups()
    cand.append({"newid": nid, "artist": name.strip(),
                 "urls": ["https://t.pia.jp/pia/event/event.do?event%sCd=%s"
                          % ("Bundle" if cd.startswith("b") else "", cd)]})
    print("id=%s %s" % (nid, name.strip()[:40]))
    nid += 1

json.dump(cand, io.open("tmp/cand_misono_0907.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("候補 %d件" % len(cand))
