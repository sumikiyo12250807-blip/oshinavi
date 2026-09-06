# -*- coding: utf-8 -*-
"""削除する83件の記録を logs/removed_2026-09-07.md に書く。
削除の"前"に走らせる（消したあとでは公演名もURLも取れない）。
URLは index.html から機械抽出したものだけ（DELETE_GATE 4.7・手で書かない）。
"""
import io, re, json

IDS = [268,302,411,498,631,732,759,938,1013,1061,1062,1116,1260,1288,1613,1615,1616,1849,
       1920,1992,1993,1997,2008,2035,2098,2178,2216,2226,2267,2279,2284,2288,2300,2313,
       2341,2353,2373,2504,2522,2624,2749,2806,2844,2918,3079,3120,3229,3271,3365,3441,
       3540,3632,3669,3711,3718,4017,4029,4145,4224,4270,4334,4346,4433,4737,4790,4971,
       4980,4982,5081,5121,5239,5321,5620,5633,6173,6182,6189,6264,6437,6710,6712,6952,6964]

html = io.open("index.html", encoding="utf-8", newline="").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", html, re.S).group(1))
by = {e["id"]: e for e in EV}

rows = []
for eid in IDS:
    e = by.get(eid)
    if not e:
        rows.append((eid, "", "現物に無い", ""))
        continue
    url = ""
    for k in ("pia", "eplus", "rakuten", "lawson"):
        if (e.get("links") or {}).get(k):
            url = e["links"][k]
            break
    rows.append((eid, e.get("date") or "", e.get("name", ""), url))

rows.sort(key=lambda r: r[1])

with io.open("logs/removed_2026-09-07.md", "w", encoding="utf-8", newline="\n") as f:
    f.write("# 2026-09-07 朝に削除したエントリ（%d件）\n\n" % len(rows))
    f.write("理由＝**公演日が過ぎた**（公演当日は残して翌朝消す運用）。\n")
    f.write("判定は `check_expired.py` ＋ 別エージェントの独立再導出の**両方が一致したものだけ**。\n")
    f.write("ずれた2件（id16 ONE PARK FESTIVAL／id271 舞台『TARKIE』）は `saleEndUnknown` が付いていたので\n")
    f.write("削除せず「要再確認」に回した。id1904（劇団かもめんたる）は配信の視聴券が10/4まで生きているので残した。\n\n")
    f.write("| id | 公演日 | 公演名 | 確認用URL |\n|---|---|---|---|\n")
    for eid, d, name, url in rows:
        link = "[確認](%s)" % url if url else "(URLなし)"
        f.write("| %s | %s | %s | %s |\n" % (eid, d, name.replace("|", "／"), link))
print("wrote logs/removed_2026-09-07.md (%d件)" % len(rows))
