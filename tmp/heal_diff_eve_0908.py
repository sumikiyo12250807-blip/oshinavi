# -*- coding: utf-8 -*-
"""ヒール適用の前後で「画面に出る枠」が減ったエントリを数える。
🚨 ヒール自身の安全弁は「公演単位」でしか比べないので、同じ公演の券種違いが
   丸ごと消えても気づかない（2026-09-01 阪神×広島 12枠→1枠）。
   だからここでは **券種名（日付部分を落とす）＋飛び先URL** で突き合わせる。
"""
import io, re, json, sys, collections

TODAY = "2026-09-08"
BEFORE = "index.html.bak_0908_preeveheal"   # 19時台のヒール直前
AFTER = "index.html"


def load(path):
    h = io.open(path, encoding="utf-8", newline="").read()
    return {e["id"]: e for e in json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", h, re.S).group(1))}


def visible(t):
    if t.get("saleUntilSoldOut") or t.get("soldout"):
        return True
    sd, d = t.get("startDate"), t.get("date")
    return not ((not sd or sd <= TODAY) and (d or "") < TODAY)


def key(t):
    """券種名から日付部分を落とし、飛び先URLと組にする。
    「9/1 10:00発売」→「〜12/20 23:59」の書き換えを『消えた』と数えないため。"""
    ty = t.get("type") or ""
    ty = re.sub(r"〜\s*\d{1,2}/\d{1,2}(?:\s*\d{1,2}:\d{2})?\s*$", "", ty)
    ty = re.sub(r"\d{1,2}/\d{1,2}(?:\s*\d{1,2}:\d{2})?\s*発売\s*$", "", ty)
    ty = re.sub(r"本日発売\s*$", "", ty)
    return (ty.strip(), t.get("url") or "")


A, B = load(BEFORE), load(AFTER)

lost, gained = [], []
tot_a = tot_b = 0
for eid, ea in A.items():
    va = {key(t) for t in ea.get("tickets", []) if visible(t)}
    tot_a += len(va)
    eb = B.get(eid)
    if eb is None:
        if va:
            lost.append((eid, ea.get("name", "")[:40], len(va), 0, sorted(va)))
        continue
    vb = {key(t) for t in eb.get("tickets", []) if visible(t)}
    tot_b += len(vb)
    gone = va - vb
    if gone:
        lost.append((eid, ea.get("name", "")[:40], len(va), len(vb), sorted(gone)))
    add = vb - va
    if add:
        gained.append((eid, ea.get("name", "")[:40], len(va), len(vb)))

for eid, eb in B.items():
    if eid not in A:
        tot_b += sum(1 for t in eb.get("tickets", []) if visible(t))

with io.open("tmp/heal_diff_eve_0908.txt", "w", encoding="utf-8") as f:
    f.write("=== ヒール適用の前後・画面に出る枠の突合 (today=%s) ===\n" % TODAY)
    f.write("前 %d枠 → 後 %d枠 （差 %+d）\n" % (tot_a, tot_b, tot_b - tot_a))
    f.write("枠が消えたエントリ %d件 / 枠が増えたエントリ %d件\n\n" % (len(lost), len(gained)))
    if lost:
        f.write("🚨【枠が消えたエントリ】\n")
        for eid, name, na, nb, gone in lost:
            f.write("  id=%-6s %s  %d枠→%d枠\n" % (eid, name, na, nb))
            for ty, url in gone:
                f.write("      - %s | %s\n" % (ty[:56], url[:70] or "(urlなし)"))
    else:
        f.write("✅ 画面に出る枠が消えたエントリは0件。\n")
    f.write("\n【枠が増えたエントリ %d件】\n" % len(gained))
    for eid, name, na, nb in gained[:60]:
        f.write("  id=%-6s %s  %d枠→%d枠\n" % (eid, name, na, nb))

print("前=%d 後=%d 差=%+d / 消えた%d件 増えた%d件" % (tot_a, tot_b, tot_b - tot_a, len(lost), len(gained)))
