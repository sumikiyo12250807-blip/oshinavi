# -*- coding: utf-8 -*-
"""(A)判定の穴を潰すための追加点検。ネットワーク未使用。"""
import re, json, io, os

BASE = r"C:\Users\user\oshinavi"
TODAY = "2026-09-07"
h = open(os.path.join(BASE, "index.html"), encoding="utf-8").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\n", h, re.S).group(1))

def nd(d):
    if not d or not isinstance(d, str):
        return None
    mm = re.match(r"^(\d{4})[-/](\d{1,2})[-/](\d{1,2})", d.strip())
    return "%04d-%02d-%02d" % tuple(map(int, mm.groups())) if mm else None

past = [e for e in EV if nd(e.get("date")) and nd(e["date"]) < TODAY]

out = io.StringIO()
W = lambda s="": out.write(s + "\n")

W("### 追加点検（(A)候補の穴つぶし）")
W()

# 1. エントリ直下の saleEndUnknown
ent_unk = [e for e in EV if e.get("saleEndUnknown")]
ent_unk_past = [e for e in past if e.get("saleEndUnknown")]
W("1) エントリ直下 saleEndUnknown=true : 全体 %d 件 / うち公演日が過去 %d 件"
  % (len(ent_unk), len(ent_unk_past)))
for e in ent_unk_past:
    W("   - id=%s %s (公演日 %s)" % (e.get("id"), e.get("name"), e.get("date")))
W()

# 2. 公演日が過去のエントリで、startDate が未来の枠（これから発売＝生きている可能性）
W("2) 公演日が過去 かつ startDate が %s 以降の枠を持つエントリ" % TODAY)
n = 0
for e in past:
    fs = [t for t in (e.get("tickets") or []) if nd(t.get("startDate")) and nd(t["startDate"]) >= TODAY]
    if fs:
        n += 1
        W("   - id=%s %s (公演日 %s)" % (e.get("id"), e.get("name"), e.get("date")))
        for t in fs:
            W("       %s  発売開始=%s 終了=%s" % (t.get("type"), t.get("startDate"), t.get("date")))
W("   該当 %d 件" % n)
W()

# 3. 公演日が過去 かつ saleUntilSoldOut / soldout / saleEnded の分布
W("3) 公演日が過去のエントリのフラグ分布")
cnt = {}
for e in past:
    for t in (e.get("tickets") or []):
        for k in ("soldout", "saleEnded", "saleUntilSoldOut", "saleEndUnknown"):
            if t.get(k):
                cnt[k] = cnt.get(k, 0) + 1
W("   %s" % json.dumps(cnt, ensure_ascii=False, sort_keys=True))
W()

# 4. 公演日が過去 かつ saleUntilSoldOut を持つ枠（売り切れまで販売＝終了日を過ぎても生きうる）
W("4) 公演日が過去 かつ saleUntilSoldOut の枠（終了日が過去でも念のため列挙）")
for e in past:
    su = [t for t in (e.get("tickets") or []) if t.get("saleUntilSoldOut")]
    if su:
        W("   - id=%s %s (公演日 %s)" % (e.get("id"), e.get("name"), e.get("date")))
        for t in su:
            W("       %s  終了=%s soldout=%s" % (t.get("type"), t.get("date"), bool(t.get("soldout"))))
W()

# 5. 配信・オンライン系のキーワードを持つ、公演日が過去のエントリ（見落とし警戒）
W("5) 公演日が過去で「配信/オンライン/アーカイブ/見逃し」を含むエントリ")
kw = ("配信", "オンライン", "アーカイブ", "見逃し", "ライブビューイング", "ＬＶ")
for e in past:
    blob = (e.get("name", "") + e.get("venue", "") + e.get("dateLabel", "") +
            " ".join(str(t.get("type", "")) for t in (e.get("tickets") or [])))
    if any(k in blob for k in kw):
        alive = [t for t in (e.get("tickets") or []) if nd(t.get("date")) and nd(t["date"]) >= TODAY]
        W("   - id=%s %s (公演日 %s) 生きた枠=%d" % (e.get("id"), e.get("name"), e.get("date"), len(alive)))
        for t in (e.get("tickets") or []):
            W("       %s  終了=%s" % (t.get("type"), t.get("date")))
W()

# 6. longrun / showSalePeriod を持つ公演日が過去のエントリ
W("6) 公演日が過去で longrun / showSalePeriod を持つエントリ")
for e in past:
    if e.get("longrun") or e.get("showSalePeriod"):
        W("   - id=%s %s (公演日 %s) longrun=%s showSalePeriod=%s"
          % (e.get("id"), e.get("name"), e.get("date"), e.get("longrun"), e.get("showSalePeriod")))
W()

# 7. 公演日が過去のエントリの date 分布（古すぎる＝取りこぼしの残骸を炙る）
W("7) 公演日が過去のエントリの公演日分布")
dist = {}
for e in past:
    dist[nd(e["date"])] = dist.get(nd(e["date"]), 0) + 1
for k in sorted(dist):
    W("   %s : %d 件" % (k, dist[k]))
W()

# 8. verified=false のもの
W("8) 公演日が過去で verified が true でないエントリ")
for e in past:
    if e.get("verified") is not True:
        W("   - id=%s %s verified=%r" % (e.get("id"), e.get("name"), e.get("verified")))
W()

with open(os.path.join(BASE, "tmp", "agent_delcheck_0907_sanity.txt"), "w", encoding="utf-8") as f:
    f.write(out.getvalue())
print("sanity done past=%d" % len(past))
