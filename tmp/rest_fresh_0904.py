# -*- coding: utf-8 -*-
"""fresh のうち、まだ投入していない残り全部の候補JSONを作る。

🚨1バッチの上限は100件（2026-08-21 ユーザー変更）。「50件」は上限でなくただのペース。
   未掲載は全部入れるのが方針（[[feedback_capture_all_not_select]]＝選考をやめる）。
"""
import json, io, re, unicodedata

tri = json.load(io.open("tmp/_triage_0904.json", encoding="utf-8"))
fresh = tri["fresh"]
done = set(x["urls"][0] for x in json.load(io.open("tmp/newbatch_cand_0904.json", encoding="utf-8")))
held = set(x.get("url") for x in json.load(io.open("tmp/newbatch_held_0904.json", encoding="utf-8")))

html = io.open("index.html", encoding="utf-8", newline="").read()
events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", html, re.S).group(1))
ex_cds = set(re.findall(r"event(?:Bundle)?Cd=(\w+)", html))


def cd(u):
    m = re.search(r"event(?:Bundle)?Cd=(\w+)", u or "")
    return m.group(1) if m else ""


def norm(s):
    s = unicodedata.normalize("NFKC", s or "")
    return re.sub(r"[\s　・／/＜＞<>「」『』（）()【】’'\"!！\-—]", "", s).lower()


# いま index にある全エントリ名（新着プール含む）と同名なら投入しない＝統合行き
allnames = [norm(e.get("name")) for e in events] + [norm(e.get("artist")) for e in events]
allnames = [n for n in allnames if n]

rest, skip_dup, skip_name = [], [], []
for it in fresh:
    u = it.get("url")
    if u in done or u in held:
        continue
    if cd(u) in ex_cds:          # 投入済みのeventCd
        skip_dup.append(it); continue
    k = norm(it.get("artist"))
    if any(n and (k.startswith(n) or n.startswith(k)) for n in allnames):
        skip_name.append(it); continue
    rest.append(it)

cand = [{"newid": 6600 + n, "artist": it.get("artist", ""), "urls": [it["url"]]}
        for n, it in enumerate(rest, 1)]
json.dump(cand, io.open("tmp/rest_cand_0904.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
json.dump(skip_name, io.open("tmp/rest_skipname_0904.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

buf = []
for it in rest:
    buf.append("%s | 発売%s | %s %s" % (it.get("artist"), it.get("rlsdate"),
                                        it.get("pref"), it.get("venue")))
    buf.append("   %s" % it.get("url"))
io.open("tmp/rest_list_0904.txt", "w", encoding="utf-8").write("\n".join(buf))

print("FRESH=%d  投入済み=%d  保留=%d" % (len(fresh), len(done), len(held)))
print("REST_TO_ADD=%d  eventCd重複でskip=%d  同名でskip(統合行き)=%d" % (
    len(rest), len(skip_dup), len(skip_name)))
