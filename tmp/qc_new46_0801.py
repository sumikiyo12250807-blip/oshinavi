# -*- coding: utf-8 -*-
"""新着46件(id3572-3621)の投入後QC。券種差分では見えない型を潰す。

 ① 重複: eventCd/BundleCd（links.pia＋tickets[].url）／NFKC正規化したartist名 で既存と照合
 ② 全角残り: artist/name/venue/dateLabel/ticket.type に全角ラテン・全角数字が残っていないか
 ③ バッジ潰れ: 同一エントリ内で同じticket.type文字列が2枚以上（席種違いが潰れている疑い）
 ④ カウントダウン価値: 発売開始までの日数（4日未満が混じっていないか）
 ⑤ 会場に県名が入る罠: prefecture=全国なのに会場が1つだけ 等
出力はUTF-8ファイル（コンソールに日本語を出さない＝化け読み防止）。"""
import io
import json
import re
import sys
import datetime
import unicodedata

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

TODAY = datetime.date(2026, 8, 1)
NEW_IDS = set(range(3572, 3622))

h = open(r"C:\Users\user\oshinavi\index.html", "rb").read().decode("utf-8")
evs = json.loads(re.search(r"  const EVENTS = (\[.*?\]);", h, re.S).group(1))
new = [e for e in evs if e["id"] in NEW_IDS]
old = [e for e in evs if e["id"] not in NEW_IDS]
print("新着 %d件 / 既存 %d件" % (len(new), len(old)))


def codes(e):
    out = set()
    urls = [(e.get("links") or {}).get("pia") or ""]
    urls += [t.get("url") or "" for t in (e.get("tickets") or [])]
    for u in urls:
        for m in re.finditer(r"(?:eventCd|eventBundleCd)=([A-Za-z0-9]+)", u):
            out.add(m.group(1))
    return out


def norm(s):
    return unicodedata.normalize("NFKC", (s or "")).replace(" ", "").lower()


# ① 重複
old_codes = {}
for e in old:
    for c in codes(e):
        old_codes.setdefault(c, []).append(e["id"])
old_names = {}
for e in old:
    old_names.setdefault(norm(e.get("artist")), []).append(e["id"])

print("\n=== ① 重複チェック ===")
dup_code, dup_name = [], []
for e in new:
    for c in codes(e):
        if c in old_codes:
            dup_code.append((e["id"], c, old_codes[c]))
    n = norm(e.get("artist"))
    if n in old_names:
        dup_name.append((e["id"], e.get("artist"), old_names[n]))
if dup_code:
    print("🚨 ぴあコードが既存と一致（確実な重複）:")
    for i, c, o in dup_code:
        print("   id=%s code=%s ← 既存 %s" % (i, c, o))
else:
    print("  ぴあコードの重複: なし ✅")
if dup_name:
    print("⚠️ アーティスト名が既存と一致（別公演の可能性・要目視）:")
    for i, a, o in dup_name:
        print("   id=%s %s ← 既存 %s" % (i, a, o))
else:
    print("  アーティスト名の重複: なし ✅")

# ② 全角残り
print("\n=== ② 全角ラテン/数字の残り ===")
FW = re.compile(r"[Ａ-Ｚａ-ｚ０-９]")
bad = []
for e in new:
    fields = [("artist", e.get("artist")), ("name", e.get("name")),
              ("venue", e.get("venue")), ("dateLabel", e.get("dateLabel"))]
    fields += [("ticket", t.get("type")) for t in (e.get("tickets") or [])]
    for k, v in fields:
        if v and FW.search(v):
            bad.append((e["id"], k, v))
if bad:
    print("🚨 全角が残っている:")
    for i, k, v in bad:
        print("   id=%s %s: %s" % (i, k, v))
else:
    print("  全角の残り: なし ✅")

# ③ バッジ潰れ（同一type重複）
print("\n=== ③ 同じバッジ文字列が2枚以上（席種潰れの疑い） ===")
crush = []
for e in new:
    ts = [t.get("type") for t in (e.get("tickets") or [])]
    for t in set(ts):
        if ts.count(t) > 1:
            crush.append((e["id"], t, ts.count(t)))
if crush:
    print("🚨 潰れている疑い:")
    for i, t, n in crush:
        print("   id=%s ×%d: %s" % (i, n, t))
else:
    print("  同一バッジの重複: なし ✅")

# ④ カウントダウン価値
print("\n=== ④ 発売開始までの日数（4日未満が混じっていないか） ===")
near = []
for e in new:
    for t in (e.get("tickets") or []):
        sd = t.get("startDate")
        if not sd:
            continue
        d = (datetime.date.fromisoformat(sd) - TODAY).days
        if d < 4:
            near.append((e["id"], e.get("name"), t.get("type"), d))
if near:
    print("⚠️ 発売まで4日未満の枠:")
    for i, n, t, d in near:
        print("   id=%s (%+d日) %s | %s" % (i, d, (n or "")[:30], t))
else:
    print("  全枠が発売まで4日以上 ✅")

# ⑤ 県と会場の整合
print("\n=== ⑤ prefecture と venue の整合 ===")
odd = []
for e in new:
    p, v = e.get("prefecture") or "", e.get("venue") or ""
    if p == "全国" and "／" not in v and "全国ツアー" not in v:
        odd.append((e["id"], p, v))
if odd:
    print("⚠️ pref=全国なのに会場が単一に見える:")
    for i, p, v in odd:
        print("   id=%s %s | %s" % (i, p, v))
else:
    print("  整合: 問題なし ✅")
