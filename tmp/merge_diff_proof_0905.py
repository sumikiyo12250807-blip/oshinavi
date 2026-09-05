# -*- coding: utf-8 -*-
"""merge_diff が「消えた」と言った枠が、本当は url を補完しただけかを機械で確かめる。

merge_diff は (券種の基底名, 飛び先URL) の組で数えるので、**url が空だった枠に url を刻む**と
「旧キーが消えた」と見える。これが偽陽性である条件＝
  ① 旧キーの url が空
  ② 同じ券種基底名が、新しい側に（url 付きで）残っている
両方を満たさないものが1つでもあれば本物の欠落。
"""
import re, json, io

TODAY = "2026-09-05"
BEFORE = "index.html.bak_0905_merge"


def load(path):
    h = open(path, encoding="utf-8").read()
    return json.loads(re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S).group(2))


def base_type(ty):
    ty = re.sub(r"〜\s*\d{1,2}/\d{1,2}(?:\s*\d{1,2}:\d{2})?\s*$", "", ty or "")
    ty = re.sub(r"\d{1,2}/\d{1,2}(?:\s*\d{1,2}:\d{2})?\s*発売\s*$", "", ty)
    return ty.strip()


def visible(t):
    if t.get("saleUntilSoldOut") or t.get("soldout"):
        return True
    sd, d = t.get("startDate"), (t.get("date") or "")
    return not ((not sd or sd <= TODAY) and d < TODAY)


old = {e["id"]: e for e in load(BEFORE)}
new = {e["id"]: e for e in load("index.html")}

buf, bad = [], 0
for i, e in new.items():
    if i not in old:
        continue
    ko = {(base_type(t.get("type")), (t.get("url") or "").strip())
          for t in (old[i].get("tickets") or []) if visible(t)}
    kn = {(base_type(t.get("type")), (t.get("url") or "").strip())
          for t in (e.get("tickets") or []) if visible(t)}
    for ty, u in sorted(ko - kn):
        names_new = {k[0] for k in kn}
        ok = (u == "") and (ty in names_new)
        if not ok:
            bad += 1
        buf.append("%s id=%-5s %s | 旧url=%s | 新側に同名あり=%s"
                   % ("OK  " if ok else "🚨NG", i, ty, u or "(空)", ty in names_new))

buf.append("")
buf.append("本物の欠落: %d件" % bad)
io.open("tmp/merge_diff_proof_0905.txt", "w", encoding="utf-8").write("\n".join(buf))
print("REAL_LOSS=%d / checked=%d" % (bad, len(buf) - 2))
raise SystemExit(1 if bad else 0)
