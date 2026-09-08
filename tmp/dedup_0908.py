# -*- coding: utf-8 -*-
"""投入前の重複チェック。
 ①枠0のエントリを外す（貸切公演など）
 ②正規化名が既存と一致する候補を洗い出し、(県, 公演日, 締切日) まで比べて
   「同じ販売窓＝投入しない」「別の窓＝投入する（または既存へ足す）」に分ける。
   ＝feedback_capture_all_deadlines_on_add の判定方法。
🚨 部分一致で畳まない（「新日本フィル」が消える事故）＝完全一致だけ。
"""
import io, re, json, unicodedata, collections


def norm(s):
    s = unicodedata.normalize("NFKC", s or "")
    s = re.sub(r"[\s　]+", "", s)
    s = re.sub(r"[『』「」【】（）\(\)＜＞<>\[\]～〜\-‐−–—・,、.。/／!！?？:：;；\"'”’]", "", s)
    return s.lower()


def windows(e):
    """(県, 公演日らしき文字, 締切日) の集合。券種名から県と公演日を抜く。"""
    out = set()
    for t in e.get("tickets", []) or []:
        ty = t.get("type") or ""
        m = re.search(r"（([^（）]*?)\s*([\d/〜～・]+)公演）", ty)
        pref = m.group(1).strip() if m else (e.get("prefecture") or "")
        perf = m.group(2).strip() if m else ""
        out.add((pref, perf, t.get("date") or "", t.get("startDate") or ""))
    return out


h = io.open("index.html", encoding="utf-8", newline="").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", h, re.S).group(1))
idx = collections.defaultdict(list)
for e in EV:
    idx[norm(e.get("name"))].append(e)

built = json.load(io.open("tmp/built_0908.json", encoding="utf-8"))

zero = [e for e in built if not (e.get("tickets") or [])]
alive = [e for e in built if (e.get("tickets") or [])]

same, addto, fresh = [], [], []
for c in alive:
    hits = idx.get(norm(c.get("name")), [])
    if not hits:
        fresh.append(c)
        continue
    cw = windows(c)
    exist_w = set()
    for e in hits:
        exist_w |= windows(e)
    if cw and cw <= exist_w:
        same.append((c, hits))          # 販売窓がぜんぶ既存にある＝同じもの
    else:
        addto.append((c, hits, cw - exist_w))   # 既存に無い窓がある

o = io.open("tmp/dedup_0908.md", "w", encoding="utf-8")
W = o.write
W("# 投入前の重複チェック（2026-09-08）\n\n")
W("ビルド **%d件** → 枠0で外す **%d件** / 判定対象 **%d件**\n\n" % (len(built), len(zero), len(alive)))
W("| 区分 | 件数 | 意味 |\n|---|---|---|\n")
W("| ✅ そのまま投入 | %d | 同名の既存が無い |\n" % len(fresh))
W("| ⚠️ 既存に無い窓あり | %d | 名前は同じだが別公演/別の販売窓＝投入するか既存へ足す |\n" % len(addto))
W("| ⛔ 投入しない | %d | 販売窓が全部すでに既存にある＝同じもの |\n" % len(same))

if zero:
    W("\n## 枠0で外したもの\n\n")
    for e in zero:
        W("- id%s %s\n" % (e.get("id"), (e.get("name") or "")[:50]))

if same:
    W("\n## ⛔ 投入しない（既存と同じ販売窓）\n\n")
    for c, hits in same:
        W("- id%s %s\n" % (c.get("id"), (c.get("name") or "")[:46]))
        for e in hits[:3]:
            W("    ⇔ 既存 id=%s [%s] 公演%s / %s\n"
              % (e["id"], e.get("genre"), e.get("date"), (e.get("venue") or "")[:30]))

if addto:
    W("\n## ⚠️ 名前は同じだが既存に無い窓がある（1件ずつ見る）\n\n")
    for c, hits, diff in addto:
        W("- id%s %s ／ 公演%s ／ %s\n"
          % (c.get("id"), (c.get("name") or "")[:44], c.get("date"), (c.get("venue") or "")[:30]))
        for e in hits[:3]:
            W("    ⇔ 既存 id=%s [%s] 公演%s / %s\n"
              % (e["id"], e.get("genre"), e.get("date"), (e.get("venue") or "")[:30]))
        for d in sorted(diff)[:6]:
            W("    ＋既存に無い窓: 県=%s 公演=%s 締切=%s 発売=%s\n" % d)
        W("    %s\n" % (((c.get("links") or {}).get("pia")) or ""))
o.close()

json.dump([c for c in fresh], io.open("tmp/inject_fresh_0908.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
json.dump([c for c, _, _ in addto], io.open("tmp/inject_addto_0908.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("built=%d zero=%d fresh=%d addto=%d same=%d -> tmp/dedup_0908.md"
      % (len(built), len(zero), len(fresh), len(addto), len(same)))
