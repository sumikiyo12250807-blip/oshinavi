# -*- coding: utf-8 -*-
"""組み立てた60件を「既存へ統合」と「新エントリ」に仕分ける。

判定（機械で決めるのはここまで。迷った件は人が見る側に寄せる）
  A) 既存に **同じ公演日＋同じ会場** のエントリがある → 券種違い＝統合候補
  B) 無い → 別公演＝新エントリ候補（新着プールへ）

🚨スポーツは公演日と会場が同じでも畳まない＝応援する側で売り場が違う
  （feedback_sports_home_away_never_merge）。だから sports は必ず B に落とす。
🚨会場だけ同じ（寄席・ホール）は同一公演の証拠にならない → 公演日も一致した時だけ A。
"""
import io, json, re, sys

sys.stdout.reconfigure(encoding="utf-8")

SPORTS_KW = ("マリーンズ", "プロレス", "ＦＣ", "FC", "リーグ", "公式戦")

built = json.load(io.open("tmp/sweep_rest_built.json", encoding="utf-8"))
cands = {c["newid"]: c for c in json.load(io.open("tmp/sweep_rest_0909.json", encoding="utf-8"))}

s = io.open("index.html", encoding="utf-8").read()
evs = json.loads(re.search(r"const EVENTS = (\[.*?\]);\n", s, re.S).group(1))


def norm(v):
    v = re.sub(r"[（(].*?[）)]", "", v or "")
    return re.sub(r"[\s　・]", "", v)


A, B = [], []
for b in built:
    kw = cands[b["id"]]["artist"]
    sports = any(k in kw for k in SPORTS_KW)
    hit = None
    if not sports:
        for e in evs:
            if e.get("genre") == "new":
                continue
            blob = (e.get("name") or "") + (e.get("artist") or "")
            if kw not in blob:
                continue
            if (e.get("date") or "") != (b.get("date") or ""):
                continue
            if norm(b.get("venue")) and norm(b.get("venue")) in norm(e.get("venue")):
                hit = e["id"]
                break
    (A if hit else B).append((b, kw, hit, sports))

out = ["■ A＝既存へ統合（同じ公演日・同じ会場＝券種違い）", ""]
for b, kw, hit, sp in A:
    out.append("id%-5s ← new%d %s ／ %s ／ %s" % (hit, b["id"], kw, b.get("date"), b.get("venue")))
    for t in b.get("tickets") or []:
        out.append("      + %s" % t.get("type"))
out += ["", "■ B＝新エントリ候補（別公演。スポーツは必ずこちら）", ""]
for b, kw, hit, sp in B:
    out.append("new%d %s%s ／ %s ／ %s ／ %s"
               % (b["id"], kw, "【スポーツ】" if sp else "", b.get("date"),
                  b.get("prefecture"), b.get("venue")))
    out.append("      %s" % (b.get("name") or ""))
    for t in b.get("tickets") or []:
        out.append("      + %s" % t.get("type"))
    out.append("      %s" % (b.get("links") or {}).get("pia"))

io.open("tmp/sweep_triage_0909.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
print("A(統合) %d件 / B(新エントリ) %d件 -> tmp/sweep_triage_0909.txt" % (len(A), len(B)))

json.dump([b for b, k, h, s2 in B], io.open("tmp/sweep_new_0909.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
json.dump([{"newid": b["id"], "target": h} for b, k, h, s2 in A],
          io.open("tmp/sweep_mergemap_0909.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
