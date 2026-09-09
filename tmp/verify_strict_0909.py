# -*- coding: utf-8 -*-
"""骨格一致で隠れる「すり替え」と、締切の前倒し・買える枠0を独立に見る。"""
import json
import re
import io
import sys
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

NEW = r"C:\Users\user\oshinavi\index.html"
OLD = r"C:\Users\user\oshinavi\index.html.bak_0909_prenoonheal"
TODAY = "2026-09-09"


def load_events(path):
    lines = io.open(path, "r", encoding="utf-8").read().split("\n")
    start = next(i for i, ln in enumerate(lines) if ln.strip() == "const EVENTS = [")
    end = next(j for j in range(start + 1, len(lines)) if lines[j].rstrip("\r") == "];")
    body = "\n".join(lines[start:end + 1]).replace("const EVENTS = [", "[", 1).rstrip()
    return json.loads(body[:-1])


def visible(t, ev):
    if t.get("soldout"):
        return ev.get("date", "9999-99-99") >= TODAY
    sd = t.get("startDate")
    if (not sd or sd <= TODAY) and t.get("date", "0000-00-00") < TODAY:
        return False
    return True


DATE_PATS = [re.compile(p) for p in [
    r"\d{4}-\d{1,2}-\d{1,2}", r"\d{1,2}\s*/\s*\d{1,2}", r"\d{1,2}\s*:\s*\d{2}",
    r"\d{4}\s*年", r"\d{1,2}\s*月\s*\d{1,2}\s*日", r"\d{1,2}\s*月", r"\d{1,2}\s*日"]]
NOISE = re.compile(r"(発売開始|発売予定|発売終了|販売開始|販売終了|受付開始|受付終了|申込開始|申込締切|締切|まで|発売|受付|より)")


def skel(s):
    s = s or ""
    for p in DATE_PATS:
        s = p.sub("#", s)
    s = NOISE.sub("", s)
    return re.sub(r"[#\s〜~\-－―（）\(\)・,、。／/]+", "", s)


new = {e["id"]: e for e in load_events(NEW)}
old = {e["id"]: e for e in load_events(OLD)}
common = sorted(set(new) & set(old))

# A. 生の type 完全一致での消失（骨格でなく厳密に）
print("===== A. type完全一致での「表示枠の消失」=====")
strictA = []
for i in common:
    o, n = old[i], new[i]
    oc = Counter(t.get("type") for t in o.get("tickets", []) if visible(t, o))
    nc = Counter(t.get("type") for t in n.get("tickets", []) if visible(t, n))
    lost = oc - nc
    if lost:
        strictA.append((i, o, lost))
print("完全一致だと消えたように見えるエントリ数=%d（=書き換えを含む上限）" % len(strictA))

# B. url ごとの表示枠数の減少（骨格に依らない）
print("\n===== B. 飛び先URLごとの表示枠数の減少 =====")
lostB = []
for i in common:
    o, n = old[i], new[i]
    oc = Counter((t.get("url") or "") for t in o.get("tickets", []) if visible(t, o))
    nc = Counter((t.get("url") or "") for t in n.get("tickets", []) if visible(t, n))
    d = oc - nc
    if d:
        lostB.append((i, o, n, d))
print("URL単位で枠が減ったエントリ数=%d" % len(lostB))
for i, o, n, d in lostB[:30]:
    print("  id=%s %s / %s" % (i, o.get("artist"), o.get("name")))
    for u, c in d.items():
        print("      x%d URL=%s" % (c, u or "(なし)"))

# C. 締切(t.date)の前倒し（同じ骨格の枠で date が過去方向に動いた）
print("\n===== C. 締切の前倒し =====")
shrink = []
for i in common:
    o, n = old[i], new[i]
    om = defaultdict(list)
    for t in o.get("tickets", []):
        om[skel(t.get("type"))].append(t)
    nm = defaultdict(list)
    for t in n.get("tickets", []):
        nm[skel(t.get("type"))].append(t)
    for k in om:
        if k not in nm or len(om[k]) != len(nm[k]):
            continue
        for a, b in zip(sorted(om[k], key=lambda x: str(x.get("date"))),
                        sorted(nm[k], key=lambda x: str(x.get("date")))):
            if a.get("date") and b.get("date") and b["date"] < a["date"]:
                shrink.append((i, o.get("artist"), o.get("name"), a.get("type"),
                               a["date"], b["date"], b.get("type")))
print("締切が前倒しされた枠数=%d" % len(shrink))
for r in shrink[:40]:
    print("  id=%s %s / %s" % (r[0], r[1], r[2]))
    print("      %s : %s -> %s" % (r[3], r[4], r[5]))
    print("      新type=%s" % r[6])

# D. 「カードは出るのに買える枠0」
print("\n===== D. 表示枠0のエントリ =====")


def zero(evs):
    z = []
    for i, e in evs.items():
        if not any(visible(t, e) for t in e.get("tickets", [])):
            z.append(i)
    return set(z)


zo, zn = zero(old), zero(new)
print("表示枠0 旧=%d 新=%d / 新たに0になったid=%s" % (len(zo), len(zn), sorted(zn - zo)))
for i in sorted(zn - zo)[:20]:
    e = new[i]
    print("  id=%s %s / %s date=%s tickets=%d" % (i, e.get("artist"), e.get("name"), e.get("date"), len(e.get("tickets", []))))

# E. 総枠数（表示・非表示ぜんぶ）
to = sum(len(old[i].get("tickets", [])) for i in common)
tn = sum(len(new[i].get("tickets", [])) for i in common)
print("\n===== E. 総枠数(非表示込み) 旧=%d 新=%d (%+d) =====" % (to, tn, tn - to))

# F. soldout / saleEnded の増減
def cnt(evs, key):
    return sum(1 for i in common for t in evs[i].get("tickets", []) if t.get(key))


print("soldout 旧=%d 新=%d / saleEnded 旧=%d 新=%d" % (
    cnt(old, "soldout"), cnt(new, "soldout"), cnt(old, "saleEnded"), cnt(new, "saleEnded")))

# G. links / venue / name の変化
chg = 0
for i in common:
    if json.dumps(old[i].get("links"), sort_keys=True, ensure_ascii=False) != \
       json.dumps(new[i].get("links"), sort_keys=True, ensure_ascii=False):
        chg += 1
print("links が変わったエントリ数=%d" % chg)
gchg = [i for i in common if old[i].get("genre") != new[i].get("genre")]
print("genre が変わったエントリ数=%d %s" % (len(gchg), gchg[:10]))
vchg = [i for i in common if old[i].get("venue") != new[i].get("venue")]
print("venue が変わったエントリ数=%d %s" % (len(vchg), vchg[:10]))
