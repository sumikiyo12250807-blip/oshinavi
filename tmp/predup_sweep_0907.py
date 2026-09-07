# -*- coding: utf-8 -*-
"""投入する**前**に、候補が既存と同じ公演でないかを正規化名で照合する。

🚨 ぴあは同じ公演に別の eventCd を立てることがあるので、eventCd 一致だけでは弾けない
   （2026-09-07 朝、61件投入したうち20件が既存と重複していた＝投入後に気づいた）。
   今度は投入前に弾く。
判定＝正規化した公演名が既存と一致（会場か公演日の一致までは、この段階では見ない＝
      名前が同じものは全部あたしが目で確かめる）。
"""
import io, re, json, unicodedata


def norm(s):
    s = unicodedata.normalize("NFKC", s or "")
    s = re.sub(r"[\s　]+", "", s)
    s = re.sub(r"[『』「」【】（）\(\)＜＞<>\[\]～〜\-‐−–—・,、.。/／!！?？:：;；\"'”’]", "", s)
    return s.lower()


h = io.open("index.html", encoding="utf-8", newline="").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", h, re.S).group(1))
idx = {}
for e in EV:
    idx.setdefault(norm(e.get("name")), []).append(e)

cand = json.load(io.open("tmp/cand_sweep_0907.json", encoding="utf-8"))
keep, drop = [], []
for c in cand:
    hits = idx.get(norm(c["artist"]), [])
    if hits:
        drop.append((c, hits))
    else:
        keep.append(c)

json.dump(keep, io.open("tmp/cand_sweep_ok_0907.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

with io.open("tmp/predup_sweep_0907.txt", "w", encoding="utf-8") as f:
    f.write("=== 投入前の重複チェック（正規化名で照合）===\n")
    f.write("候補 %d件 → 投入する %d件 / 既存とぶつかった %d件\n\n" % (len(cand), len(keep), len(drop)))
    if drop:
        f.write("【既存とぶつかったので投入しない】\n")
        for c, hits in drop:
            f.write("  候補id=%s %s\n" % (c["newid"], c["artist"][:50]))
            for e in hits:
                f.write("     ⇔ 既存 id=%-6s [%-9s] 公演%s %s / %s\n"
                        % (e["id"], e.get("genre"), e.get("date"),
                           (e.get("venue") or "")[:26], (e.get("name") or "")[:36]))
            f.write("     %s\n" % c["urls"][0])
print("候補%d → 投入%d / 重複で外す%d" % (len(cand), len(keep), len(drop)))
