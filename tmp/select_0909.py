# -*- coding: utf-8 -*-
"""9/9朝のスイープで出た未掲載を「統合行き／新規候補／保留」に仕分ける。

判定
  ・URL(eventCd)で重複を潰す
  ・正規化した名前が既存エントリの name/artist と**完全一致** → 統合行き（ツアーの分裂）
  ・既存の名前が**ぴあ公演名の頭に来る**（部分一致） → 保留＝1件ずつ見る
    🚨素の部分一致で畳むと別団体を消す（「新日本フィル」が「日本フィル」を含む）
  ・それ以外 → 新規候補
  ・発売日が取れないもの（rlsdate 空）は保留
"""
import io, json, glob, re, sys

sys.stdout.reconfigure(encoding="utf-8")

cands = {}
for p in sorted(glob.glob("tmp/sweep_0909/*.json")):
    d = json.load(io.open(p, encoding="utf-8"))
    for c in d.get("new") or []:
        m = re.search(r"eventCd=(\w+)", c["url"])
        key = m.group(1) if m else c["url"]
        cands.setdefault(key, c)
print("未掲載（URL重複を潰した後）: %d件" % len(cands))

src = io.open("index.html", encoding="utf-8").read()
evs = json.loads(re.search(r"const EVENTS = (\[.*?\]);\n", src, re.S).group(1))


def norm(s):
    s = (s or "")
    # 全角英数→半角
    s = "".join(chr(ord(ch) - 0xFEE0) if 0xFF01 <= ord(ch) <= 0xFF5E else ch for ch in s)
    s = re.sub(r"[（(【\[].*?[）)】\]]", "", s)
    return re.sub(r"[\s　・･'\"’”!！?？~〜\-ー–—.,、。/／]", "", s).lower()


exact, partial = {}, []
for e in evs:
    for f in ("name", "artist"):
        n = norm(e.get(f))
        if len(n) >= 3:
            exact.setdefault(n, e["id"])
            partial.append((n, e["id"]))
partial.sort(key=lambda x: -len(x[0]))

merge, new, hold = [], [], []
for key, c in cands.items():
    nm = norm(c["artist"])
    if not c.get("rlsdate"):
        hold.append((key, c, "発売日が取れない", None)); continue
    hit = exact.get(nm)
    if hit:
        merge.append((key, c, hit)); continue
    # 既存の名前が「ぴあ公演名の頭」に来る形だけ拾う
    ph = next((i for n, i in partial if len(n) >= 4 and nm.startswith(n)), None)
    if ph:
        hold.append((key, c, "部分一致（頭に既存名）", ph)); continue
    new.append((key, c))

print("  統合行き（同名の既存あり）: %d件" % len(merge))
print("  保留（要目視）           : %d件" % len(hold))
print("  新規候補                : %d件" % len(new))

json.dump([{"newid": None, "artist": c["artist"], "urls": [c["url"]], "eventCd": k}
           for k, c in new],
          io.open("tmp/new_cand_0909.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump([{"eventCd": k, "artist": c["artist"], "url": c["url"], "existing_id": i}
           for k, c, i in merge],
          io.open("tmp/merge_cand_0909.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
with io.open("tmp/hold_0909.txt", "w", encoding="utf-8") as f:
    for k, c, why, i in hold:
        f.write("%s\t%s\t%s\t%s\t%s\n" % (k, why, i or "", c["artist"], c["url"]))
print("→ tmp/new_cand_0909.json / tmp/merge_cand_0909.json / tmp/hold_0909.txt")
