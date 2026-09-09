# -*- coding: utf-8 -*-
"""0909 昼のヒール前後で index.html の EVENTS を独立に突合する。"""
import json
import re
import sys
import io
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

NEW = r"C:\Users\user\oshinavi\index.html"
OLD = r"C:\Users\user\oshinavi\index.html.bak_0909_prenoonheal"
TODAY = "2026-09-09"


def load_events(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.read().split("\n")
    start = None
    for i, ln in enumerate(lines):
        if ln.strip() == "const EVENTS = [":
            start = i
            break
    if start is None:
        raise RuntimeError("EVENTS start not found in " + path)
    end = None
    for j in range(start + 1, len(lines)):
        if lines[j].rstrip("\r") == "];":
            end = j
            break
    if end is None:
        raise RuntimeError("EVENTS end not found in " + path)
    body = "\n".join(lines[start:end + 1])
    body = body.replace("const EVENTS = [", "[", 1)
    body = body.rstrip()
    assert body.endswith("];")
    body = body[:-1]  # drop trailing ';'
    return json.loads(body), start, end


def visible(t, ev):
    """renderCard の実物の条件をそのまま写す。"""
    if t.get("soldout"):
        return ev.get("date", "9999-99-99") >= TODAY
    # 販売終了したチケットは表示しない
    sd = t.get("startDate")
    if (not sd or sd <= TODAY) and t.get("date", "0000-00-00") < TODAY:
        return False
    return True


DATE_PATS = [
    re.compile(r"\d{4}-\d{1,2}-\d{1,2}"),
    re.compile(r"\d{1,2}\s*/\s*\d{1,2}"),
    re.compile(r"\d{1,2}\s*:\s*\d{2}"),
    re.compile(r"\d{4}\s*年"),
    re.compile(r"\d{1,2}\s*月\s*\d{1,2}\s*日"),
    re.compile(r"\d{1,2}\s*月"),
    re.compile(r"\d{1,2}\s*日"),
]
NOISE = re.compile(r"(発売開始|発売予定|発売終了|販売開始|販売終了|受付開始|受付終了|申込開始|申込締切|締切|まで|発売|受付|より)")


def skel(s):
    s = s or ""
    for p in DATE_PATS:
        s = p.sub("#", s)
    s = NOISE.sub("", s)
    s = re.sub(r"[#\s〜~\-－―（）\(\)・,、。／/]+", "", s)
    return s


new_events, ns, ne = load_events(NEW)
old_events, os_, oe = load_events(OLD)
print("EVENTS行 新: %d-%d / 旧: %d-%d" % (ns + 1, ne + 1, os_ + 1, oe + 1))
print("エントリ数 新=%d 旧=%d" % (len(new_events), len(old_events)))

new_by_id = {e["id"]: e for e in new_events}
old_by_id = {e["id"]: e for e in old_events}
print("id重複 新=%d 旧=%d" % (len(new_events) - len(new_by_id), len(old_events) - len(old_by_id)))

# ---- 2. エントリの増減 ----
removed = sorted(set(old_by_id) - set(new_by_id))
added = sorted(set(new_by_id) - set(old_by_id))
print("\n===== 2. エントリ増減 =====")
print("消えたid数=%d 増えたid数=%d" % (len(removed), len(added)))
for i in removed:
    e = old_by_id[i]
    print("  [DEL] id=%s %s / %s" % (i, e.get("artist"), e.get("name")))
for i in added[:40]:
    e = new_by_id[i]
    print("  [ADD] id=%s %s / %s" % (i, e.get("artist"), e.get("name")))
if len(added) > 40:
    print("  ... 他 %d 件" % (len(added) - 40))

# ---- 1. 画面に出る枠が減ったエントリ ----
print("\n===== 1. 画面に出る枠の減少 =====")
tot_old_vis = 0
tot_new_vis = 0
lost_rows = []
for i in sorted(set(old_by_id) & set(new_by_id)):
    oe_ = old_by_id[i]
    ne_ = new_by_id[i]
    ov = [t for t in oe_.get("tickets", []) if visible(t, oe_)]
    nv = [t for t in ne_.get("tickets", []) if visible(t, ne_)]
    tot_old_vis += len(ov)
    tot_new_vis += len(nv)
    oc = Counter(skel(t.get("type")) for t in ov)
    nc = Counter(skel(t.get("type")) for t in nv)
    lost = oc - nc
    if lost:
        lost_rows.append((i, oe_, ne_, len(ov), len(nv), lost))

print("表示枠 合計 旧=%d 新=%d (差 %+d)  ※共通idのみ" % (tot_old_vis, tot_new_vis, tot_new_vis - tot_old_vis))
print("枠が減ったエントリ数=%d" % len(lost_rows))
for i, oe_, ne_, no, nn, lost in lost_rows:
    print("  id=%s %s / %s  表示枠 %d->%d" % (i, oe_.get("artist"), oe_.get("name"), no, nn))
    for k, c in lost.items():
        samples = [t.get("type") for t in oe_.get("tickets", []) if skel(t.get("type")) == k and visible(t, oe_)]
        print("      x%d 骨格[%s] 例: %s" % (c, k, samples[0] if samples else "?"))

# ---- 4. date / dateLabel の縮み ----
print("\n===== 4. date / dateLabel の変化 =====")
dchg = []
for i in sorted(set(old_by_id) & set(new_by_id)):
    o = old_by_id[i]
    n = new_by_id[i]
    if o.get("date") != n.get("date") or (o.get("dateLabel") or "") != (n.get("dateLabel") or ""):
        dchg.append((i, o, n))
print("date/dateLabel が変わったエントリ数=%d" % len(dchg))
for i, o, n in dchg:
    print("  id=%s %s / %s" % (i, o.get("artist"), o.get("name")))
    print("      date: %s -> %s" % (o.get("date"), n.get("date")))
    print("      label: %s -> %s" % (o.get("dateLabel"), n.get("dateLabel")))

# ---- 3. 今日足された枠 ----
print("\n===== 3. 今日足された枠 =====")
add_rows = []
for i in sorted(set(old_by_id) & set(new_by_id)):
    o = old_by_id[i]
    n = new_by_id[i]
    oc = Counter(skel(t.get("type")) for t in o.get("tickets", []))
    nc = Counter(skel(t.get("type")) for t in n.get("tickets", []))
    gain = nc - oc
    if gain:
        for k, c in gain.items():
            samples = [t for t in n.get("tickets", []) if skel(t.get("type")) == k]
            add_rows.append((i, n, k, c, samples[0]))
print("既存エントリに枠が足されたケース数=%d (対象エントリ %d件)" % (
    sum(r[3] for r in add_rows), len(set(r[0] for r in add_rows))))


def eventcd(url):
    if not url:
        return None
    m = re.search(r"event(?:Bundle)?Cd=([0-9A-Za-z]+)", url)
    return m.group(1) if m else None


seen = set()
picked = []
for i, n, k, c, t in add_rows:
    if i in seen:
        continue
    pia = (n.get("links") or {}).get("pia")
    cd = eventcd(pia)
    if not cd:
        continue
    seen.add(i)
    picked.append((i, n.get("artist"), n.get("name"), t.get("type"), t.get("startDate"),
                   t.get("date"), bool(t.get("soldout")), cd, pia))
    if len(picked) >= 8:
        break
print("\n-- 抜き取り候補8枠 --")
for p in picked:
    print("id=%s | %s | %s" % (p[0], p[1], p[2]))
    print("    type=%s start=%s end=%s soldout=%s" % (p[3], p[4], p[5], p[6]))
    print("    eventCd=%s" % p[7])
print("\nCDLIST=" + ",".join(p[7] for p in picked))

with open(r"C:\Users\user\oshinavi\tmp\verify_picked_0909.json", "w", encoding="utf-8") as f:
    json.dump(picked, f, ensure_ascii=False, indent=1)
