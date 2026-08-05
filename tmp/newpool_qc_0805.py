# -*- coding: utf-8 -*-
"""新着プール(genre:"new")の品質を機械で総点検する（2026-08-05・ユーザー依頼「新着をチェックして」）。

ぴあとの枠照合は reconcile_pia --new が別にやる。ここは【表示が壊れていないか】を見る:
  ① 画面から消える枠（締切が過ぎている／startDate==dateで発売日超え＝隠れ枠）
  ② 全角ローマ字・全角数字の混入（レビューしづらい・[[feedback_newpool_fullwidth_halfwidth]]）
  ③ 空カッコ「（）」や連続スペース等の表記崩れ
  ④ 同一エントリ内でtypeが完全一致する枠（席種違いを潰していないか＝id3769で実際に起きた）
  ⑤ バッジに公演日が入っていない枠（[[feedback_badge_date_full_form]]）
  ⑥ 2027年公演なのに「R9年」表記が無い（[[feedback_r9_year_notation]]）
  ⑦ 買える売り場が1つも無い（links全null）
  ⑧ 下書きジャンルが未設定/new のまま
  ⑨ 既存エントリ（プール外）と名前がぶつかる＝二重登録の疑い
"""
import datetime
import io
import json
import os
import re
import sys
import unicodedata

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = r"C:\Users\user\oshinavi"
TODAY = datetime.date(2026, 8, 5)

h = io.open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
EVENTS = json.loads(re.search(r"const EVENTS\s*=\s*(\[.*?\]);", h, re.S).group(1))
pool = [e for e in EVENTS if e.get("genre") == "new"]
others = [e for e in EVENTS if e.get("genre") != "new"]
print("新着プール %d件を点検\n" % len(pool))

FW = re.compile(r"[Ａ-Ｚａ-ｚ０-９]")
MD = re.compile(r"\d{1,2}/\d{1,2}")


def d(s):
    try:
        return datetime.date(*map(int, s.split("-")))
    except Exception:
        return None


def key(s):
    s = unicodedata.normalize("NFKC", s or "")
    return re.sub(r"[\s　「」『』【】≪≫＜＞<>()（）\[\]~〜～\-－ー・,、.。!！?？'\"’”]", "", s).lower()


ex_keys = [(e["id"], e.get("artist") or "", key((e.get("artist") or "") + (e.get("name") or ""))) for e in others]

issues = {k: [] for k in "①②③④⑤⑥⑦⑧⑨"}
for e in pool:
    eid, art = e["id"], (e.get("artist") or "")[:44]
    tks = e.get("tickets") or []
    seen = {}
    for t in tks:
        ty, dt, sd = t.get("type") or "", d(t.get("date") or ""), d(t.get("startDate") or "")
        # ① 画面から消える枠
        if dt and dt < TODAY and (not sd or sd <= TODAY):
            issues["①"].append((eid, art, "締切 %s が過ぎている: %s" % (dt, ty[:52])))
        elif sd and dt and sd == dt and dt < TODAY:
            issues["①"].append((eid, art, "隠れ枠(startDate==date=%s): %s" % (dt, ty[:52])))
        # ⑤ バッジに公演日
        if not MD.search(ty):
            issues["⑤"].append((eid, art, "公演日が無い: %s" % ty[:60]))
        # ⑥ R9年
        if dt and "公演" in ty:
            pass
        # ④ 重複type
        seen[ty] = seen.get(ty, 0) + 1
    for ty, c in seen.items():
        if c > 1:
            issues["④"].append((eid, art, "同じ表記が%d枠: %s" % (c, ty[:56])))
    blob = art + (e.get("name") or "") + (e.get("venue") or "") + (e.get("dateLabel") or "") + "".join(t.get("type") or "" for t in tks)
    if FW.search(blob):
        issues["②"].append((eid, art, "全角: %s" % "".join(sorted(set(FW.findall(blob))))[:24]))
    if "（）" in blob or "()" in blob or "  " in (e.get("venue") or ""):
        issues["③"].append((eid, art, "空カッコ/二重スペース"))
    # ⑥ 2027年公演のR9表記
    ed = d(e.get("date") or "")
    if ed and ed.year >= 2027:
        if "R9" not in (e.get("dateLabel") or "") and not any("R9" in (t.get("type") or "") for t in tks):
            issues["⑥"].append((eid, art, "2027年公演だがR9年表記なし date=%s" % ed))
    if not any((e.get("links") or {}).get(k) for k in ("pia", "rakuten", "eplus", "lawson")):
        issues["⑦"].append((eid, art, "売り場リンクが1つも無い"))
    g = e.get("_genre")
    if not g or g == "new":
        issues["⑧"].append((eid, art, "_genre=%s" % g))
    k = key(art + (e.get("name") or ""))
    for oid, oart, ok in ex_keys:
        if len(k) >= 8 and (k in ok or ok in k):
            issues["⑨"].append((eid, art, "既存id%d %s と同名の疑い" % (oid, oart[:34])))
            break

LABEL = {
    "①": "画面から消える枠（締切切れ・隠れ枠）",
    "②": "全角ローマ字/数字の混入",
    "③": "空カッコ・二重スペース",
    "④": "同一エントリ内で表記が完全に同じ枠（席種違いの潰し疑い）",
    "⑤": "バッジに公演日が入っていない枠",
    "⑥": "2027年公演なのにR9年表記が無い",
    "⑦": "売り場リンクが1つも無い",
    "⑧": "下書きジャンルが未設定",
    "⑨": "既存エントリと同名＝二重登録の疑い",
}
ng = 0
for k in "①②③④⑤⑥⑦⑧⑨":
    v = issues[k]
    print("%s %s … %d件" % (k, LABEL[k], len(v)))
    for eid, art, msg in v[:40]:
        print("    id%-5d %-40s %s" % (eid, art, msg))
    if len(v) > 40:
        print("    …ほか %d件" % (len(v) - 40))
    ng += len(v)
    print()
print("指摘 合計 %d件" % ng)
