# -*- coding: utf-8 -*-
"""本日発売ぶん（today 8件＋unknownの"TODAY"表記28件）と、新規エントリにする日本フィル1件の
候補JSONを作る。

🚨本日発売の子は締切日が入らない（ぴあが発売時刻を過ぎるまで締切を出さない）＝
   投入しても「隠れ枠」になるので、**昼のヒールで必ず締切を取り込む**
   （[[feedback_harvest_today_sale_enddate]]）。
"""
import json, io, re, unicodedata

tri = json.load(io.open("tmp/_triage_0904.json", encoding="utf-8"))
items = list(tri["today"]) + [x for x in tri["unknown"] if (x.get("rlsdate") or "").strip() == "TODAY"]
rest_unknown = [x for x in tri["unknown"] if (x.get("rlsdate") or "").strip() != "TODAY"]

html = io.open("index.html", encoding="utf-8", newline="").read()
events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", html, re.S).group(1))
ex_cds = set(re.findall(r"event(?:Bundle)?Cd=(\w+)", html))


def cd(u):
    m = re.search(r"event(?:Bundle)?Cd=(\w+)", u or "")
    return m.group(1) if m else ""


def norm(s):
    s = unicodedata.normalize("NFKC", s or "")
    return re.sub(r"[\s　・／/＜＞<>「」『』（）()【】’'\"!！\-—]", "", s).lower()


allnames = [n for n in ([norm(e.get("name")) for e in events] +
                        [norm(e.get("artist")) for e in events]) if n]

add, skip_cd, skip_name = [], [], []
for it in items:
    if cd(it.get("url")) in ex_cds:
        skip_cd.append(it); continue
    k = norm(it.get("artist"))
    if any(k.startswith(n) or n.startswith(k) for n in allnames):
        skip_name.append(it); continue
    add.append(it)

# 日本フィル 第九特別演奏会2026（阪哲朗指揮）＝新規エントリ
extra = json.load(io.open("tmp/newentry_cand_0904.json", encoding="utf-8"))

cand = [{"newid": 6700 + n, "artist": it.get("artist", ""), "urls": [it["url"]]}
        for n, it in enumerate(add, 10)]
cand += extra
json.dump(cand, io.open("tmp/today_cand_0904.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
json.dump(skip_name, io.open("tmp/today_skipname_0904.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
json.dump(rest_unknown, io.open("tmp/unknown_rest_0904.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

buf = []
for it in add:
    buf.append("%s | %s %s" % (it.get("artist"), it.get("pref"), it.get("venue")))
    buf.append("   %s" % it.get("url"))
io.open("tmp/today_list_0904.txt", "w", encoding="utf-8").write("\n".join(buf))

print("本日発売の候補=%d（today %d + unknownのTODAY %d）" % (
    len(items), len(tri["today"]), len(items) - len(tri["today"])))
print("  投入する=%d  eventCd登録済み=%d  同名で統合行き=%d" % (len(add), len(skip_cd), len(skip_name)))
print("  ＋新規エントリ（日本フィル）=%d" % len(extra))
print("発売日が本当に不明=%d" % len(rest_unknown))
