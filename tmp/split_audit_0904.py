# -*- coding: utf-8 -*-
"""同じアーティストが複数エントリに分裂しているものを洗い出して、畳む案を作る。

きっかけ＝今朝のスイープで「統合先が複数あって決められない」12件が出た。
根っこは**既存側が分裂している**こと（syrup16gが3エントリ、SCANDALが3エントリ…）。
[[feedback_tour_consolidate]]＝ツアー・複数会場は1エントリにまとめる、が方針。

🚨畳んではいけないもの（[[feedback_sports_home_away_never_merge]]）
   - スポーツの主催違い（ホーム/ビジターで売り場が違う）
   - 座席種で売り場が分かれているもの（車椅子席など）
   - オーケストラの「1公演＝1エントリ」（多数派の作りに合わせる）
なので**案を出すだけ**。実行はしない。
"""
import json, re, io, unicodedata
from collections import defaultdict

html = io.open("index.html", encoding="utf-8", newline="").read()
events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", html, re.S).group(1))


def norm(s):
    s = unicodedata.normalize("NFKC", s or "")
    return re.sub(r"[\s　・／/＜＞<>「」『』（）()【】’'\"!！\-—]", "", s).lower()


# 名前が完全一致するエントリを束ねる（部分一致では別団体を巻き込む）
g = defaultdict(list)
for e in events:
    if e.get("genre") == "new":
        continue
    k = norm(e.get("name"))
    if k:
        g[k].append(e)

SPORTS = {"sports"}
groups = [(k, v) for k, v in g.items() if len(v) > 1]
groups.sort(key=lambda kv: -len(kv[1]))

buf = ["同じ名前で複数エントリに分裂しているもの", ""]
n_merge, n_keep = 0, 0
for k, es in groups:
    ids = [e.get("id") for e in es]
    gens = set(e.get("genre") for e in es)
    # 畳まない判定
    why = None
    if gens & SPORTS:
        why = "スポーツ＝主催や座席種で売り場が違うことがある（畳まない）"
    elif any("オーケストラ" in (e.get("name") or "") or "交響楽団" in (e.get("name") or "")
             or "フィル" in (e.get("name") or "") for e in es):
        why = "オーケストラ＝1公演1エントリが多数派（畳まない）"
    elif any(re.search(r"[≪＜<【]", e.get("name") or "") for e in es):
        why = "券種・座席種が名前に入っている（畳まない）"
    buf.append("=" * 70)
    buf.append("■ %s  … %d エントリ %s" % (es[0].get("name"), len(es), ids))
    for e in es:
        ts = e.get("tickets", [])
        alive = sum(1 for t in ts if (t.get("date") or "") >= "2026-09-04" or t.get("soldout"))
        buf.append("   id=%-5s [%s] %s" % (e.get("id"), e.get("genre"), e.get("dateLabel")))
        buf.append("         会場=%s" % (e.get("venue") or "")[:64])
        buf.append("         枠=%d（生きている枠%d）" % (len(ts), alive))
    if why:
        buf.append("   → 🚫 %s" % why); n_keep += 1
    else:
        buf.append("   → ✅ 畳む候補（いちばん枠の多いエントリに寄せる）"); n_merge += 1

io.open("tmp/split_audit_0904.txt", "w", encoding="utf-8").write("\n".join(buf))
print("分裂しているアーティスト=%d組" % len(groups))
print("  畳む候補=%d組 / 触らない=%d組" % (n_merge, n_keep))
print("WROTE tmp/split_audit_0904.txt")
