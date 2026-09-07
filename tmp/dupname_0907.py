# -*- coding: utf-8 -*-
"""今朝投入した新着61件（id7098..7161）に、既存と同じ公演が混ざっていないか洗う。

🚨 投入時は eventCd でしか重複を見ていなかった。ぴあは**同じ公演に別のeventCdを立てる**ことが
   あるので、それだけでは弾けない（feedback_harvest_dedup_check＝eventCd＋正規化名の両方で見る）。
判定＝正規化した公演名が一致 かつ（会場が一致 または 公演日が一致）。
"""
import io, re, json, unicodedata


def norm(s):
    s = unicodedata.normalize("NFKC", s or "")
    s = re.sub(r"[\s　]+", "", s)
    s = re.sub(r"[『』「」【】（）\(\)＜＞<>\[\]～〜\-‐−–—・,、.。/／!！?？:：;；\"'”’]", "", s)
    return s.lower()


h = io.open("index.html", encoding="utf-8", newline="").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", h, re.S).group(1))

new = [e for e in EV if 7098 <= e["id"] <= 7161]
old = [e for e in EV if e["id"] < 7098 or e["id"] > 7161]

idx = {}
for e in old:
    idx.setdefault(norm(e.get("name")), []).append(e)

hits = []
for n in new:
    for o in idx.get(norm(n.get("name")), []):
        same_venue = norm(n.get("venue")) == norm(o.get("venue"))
        same_date = (n.get("date") or "") == (o.get("date") or "")
        if same_venue or same_date:
            hits.append((n, o, same_venue, same_date))

with io.open("tmp/dupname_0907.txt", "w", encoding="utf-8") as f:
    f.write("=== 投入した新着61件のうち、既存と同じ公演に見えるもの %d件 ===\n\n" % len(hits))
    for n, o, sv, sd in hits:
        f.write("■ 新 id=%-6s ⇔ 既存 id=%-6s  （会場一致=%s / 公演日一致=%s）\n"
                % (n["id"], o["id"], sv, sd))
        f.write("   名前 : %s\n" % (n.get("name") or "")[:70])
        f.write("   会場 : 新 %s / 既 %s\n" % ((n.get("venue") or "")[:34], (o.get("venue") or "")[:34]))
        f.write("   公演日: 新 %s / 既 %s\n" % (n.get("date"), o.get("date")))
        f.write("   既存ジャンル: %s\n" % o.get("genre"))
        f.write("   新の枠 %d / 既存の枠 %d\n" % (len(n.get("tickets", [])), len(o.get("tickets", []))))
        for t in n.get("tickets", []):
            f.write("     新: %s | %s\n" % (t.get("type"), (t.get("url") or "")[:62]))
        for t in o.get("tickets", []):
            f.write("     既: %s | %s\n" % (t.get("type"), (t.get("url") or "")[:62]))
        f.write("\n")

print("新着%d件 / 同名で既存にぶつかったもの %d件" % (len(new), len(hits)))
