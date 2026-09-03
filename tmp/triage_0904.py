# -*- coding: utf-8 -*-
"""今朝のスイープで出た未掲載を4分類する（昨日 tmp/_triage_0903.json と同じ形）。

  fresh    … 本当に新規（新しいカードになる）
  samename … 既存エントリと同名＝ツアー分裂。既存に枠を足す（新規カードにならない）
  today    … 本日発売（発売時刻を過ぎないと締切が出ないので後回し）
  unknown  … 発売日が取れない

判定は「既存の名前が、ぴあ公演名の頭に来るか」＝素の部分一致で畳まない
（[[project_pia_presale_caught_up]]の「新日本フィル」事故を避ける）。
"""
import json, re, io, glob, unicodedata, datetime
from collections import Counter

TODAY = datetime.date(2026, 9, 4)

html = io.open("index.html", encoding="utf-8", newline="").read()
events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", html, re.S).group(1))


def norm(s):
    s = unicodedata.normalize("NFKC", s or "")
    return re.sub(r"[\s　・／/＜＞<>「」『』（）()【】’'\"!！\-—]", "", s).lower()


ex = []
for e in events:
    if e.get("genre") == "new":
        continue
    for f in ("artist", "name"):
        if e.get(f):
            ex.append((norm(e[f]), e.get("id")))

# スイープ結果を集める（eventCdで重複排除）
seen, items = set(), []
for p in sorted(glob.glob("tmp/_sw_*_0904.json")):
    d = json.load(io.open(p, encoding="utf-8"))
    for it in d.get("new", []):
        cd = re.search(r"event(?:Bundle)?Cd=(\w+)", it.get("url") or "")
        k = cd.group(1) if cd else it.get("url")
        if k in seen:
            continue
        seen.add(k)
        it["_lg"] = d.get("lg")
        it["_status"] = d.get("base_filter")
        items.append(it)


def rls_date(s):
    m = re.match(r"(\d{4})/(\d{1,2})/(\d{1,2})", s or "")
    return datetime.date(*(int(x) for x in m.groups())) if m else None


out = {"fresh": [], "samename": [], "today": [], "unknown": []}
for it in items:
    rd = rls_date(it.get("rlsdate"))
    if rd is None:
        out["unknown"].append(it); continue
    if rd == TODAY:
        out["today"].append(it); continue
    k = norm(it.get("artist"))
    hit = [i for n, i in ex if n and k.startswith(n)]
    if hit:
        it["_merge_into"] = sorted(set(hit))
        out["samename"].append(it)
    else:
        out["fresh"].append(it)

json.dump(out, io.open("tmp/_triage_0904.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print("TOTAL_MISSING=%d" % len(items))
for k in ("fresh", "samename", "today", "unknown"):
    print("  %-9s %d" % (k, len(out[k])))
print("--- freshのジャンル分布(ぴあlg) ---")
lgname = {"01": "音楽", "02": "演劇", "03": "アート", "04": "スポーツ",
          "05": "映画", "06": "イベント", "07": "クラシック"}
c = Counter(it.get("_lg") for it in out["fresh"])
for k, v in c.most_common():
    print("  lg=%s %-8s %d" % (k, lgname.get(k, "?"), v))
