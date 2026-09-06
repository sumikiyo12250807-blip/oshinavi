# -*- coding: utf-8 -*-
"""2026-09-07 時点で削除してよいエントリを index.html だけから独立に洗い出す。
ネットワークアクセスは一切しない。"""
import re, json, io, os, sys

BASE = r"C:\Users\user\oshinavi"
TODAY = "2026-09-07"

h = open(os.path.join(BASE, "index.html"), encoding="utf-8").read()
m = re.search(r"const EVENTS = (\[.*?\]);\n", h, re.S)
EV = json.loads(m.group(1))

out = io.StringIO()
W = lambda s="": out.write(s + "\n")

# ---- 構造の下調べ ----
keys = {}
tkeys = {}
for e in EV:
    for k in e:
        keys[k] = keys.get(k, 0) + 1
    for t in (e.get("tickets") or []):
        for k in t:
            tkeys[k] = tkeys.get(k, 0) + 1

W("=" * 70)
W("OSHINAVI 削除候補 独立洗い出し  基準日 %s" % TODAY)
W("（index.html のみ・ネットワーク未使用）")
W("=" * 70)
W()
W("[0] 下調べ")
W("  エントリ総数: %d" % len(EV))
W("  エントリのキー出現数: %s" % json.dumps(keys, ensure_ascii=False, sort_keys=True))
W("  ticket のキー出現数: %s" % json.dumps(tkeys, ensure_ascii=False, sort_keys=True))
W()


def norm_date(d):
    """日付文字列を YYYY-MM-DD 比較用に整える。不明なら None。"""
    if not d or not isinstance(d, str):
        return None
    s = d.strip()
    mm = re.match(r"^(\d{4})[-/](\d{1,2})[-/](\d{1,2})", s)
    if mm:
        return "%04d-%02d-%02d" % (int(mm.group(1)), int(mm.group(2)), int(mm.group(3)))
    return None


def extract_urls(e):
    """links から機械的にURLを抜く（手組み厳禁）。"""
    urls = []
    lk = e.get("links")
    if isinstance(lk, dict):
        for k, v in lk.items():
            if isinstance(v, str) and v.startswith("http"):
                urls.append((k, v))
            elif isinstance(v, list):
                for x in v:
                    if isinstance(x, str) and x.startswith("http"):
                        urls.append((k, x))
                    elif isinstance(x, dict):
                        for kk, vv in x.items():
                            if isinstance(vv, str) and vv.startswith("http"):
                                urls.append((k + "." + kk, vv))
            elif isinstance(v, dict):
                for kk, vv in v.items():
                    if isinstance(vv, str) and vv.startswith("http"):
                        urls.append((k + "." + kk, vv))
    elif isinstance(lk, list):
        for x in lk:
            if isinstance(x, str) and x.startswith("http"):
                urls.append(("link", x))
            elif isinstance(x, dict):
                for kk, vv in x.items():
                    if isinstance(vv, str) and vv.startswith("http"):
                        urls.append((kk, vv))
    elif isinstance(lk, str) and lk.startswith("http"):
        urls.append(("link", lk))
    return urls


def pick_url(e):
    """報告用に1本だけ選ぶ。優先: official > pia > rakuten > その他 > ticket.url"""
    urls = extract_urls(e)
    pref = ["official", "pia", "rakuten", "eplus", "lawson", "ticket"]
    for p in pref:
        for k, v in urls:
            if p in k.lower():
                return v
    if urls:
        return urls[0][1]
    for t in (e.get("tickets") or []):
        u = t.get("url")
        if isinstance(u, str) and u.startswith("http"):
            return u
    return "(URLなし)"


A, B, C = [], [], []

# 公演日が未来 or 解析不能なものは除外集計
future = 0
baddate = []

for e in EV:
    eid = e.get("id")
    ed = norm_date(e.get("date"))
    name = e.get("name", "")
    tickets = e.get("tickets") or []

    if ed is None:
        baddate.append(e)
        continue
    if ed >= TODAY:
        future += 1
        continue

    # --- ここから先は公演日が過去（date < 2026-09-07）のみ ---

    # ルール4: saleEndUnknown を持つ枠があれば要再確認（C）
    # 券種側だけでなくエントリ直下の saleEndUnknown も見る
    unk = [t for t in tickets if t.get("saleEndUnknown")]
    ent_unk = bool(e.get("saleEndUnknown"))

    # 生きた枠 = 券種 date >= TODAY
    alive = []
    unparsed = []
    for t in tickets:
        td = norm_date(t.get("date"))
        if td is None:
            unparsed.append(t)
        elif td >= TODAY:
            alive.append((t, td))

    if unk or ent_unk:
        why = []
        if ent_unk:
            why.append("エントリ直下に saleEndUnknown=true")
        if unk:
            why.append("saleEndUnknown の枠が %d 件" % len(unk))
        C.append((e, ed, "／".join(why) + "（ルール4: 削除候補に出さず要再確認）",
                  alive, unparsed))
        continue

    if unparsed:
        C.append((e, ed, "販売終了日が解析できない枠が %d 件: %s" % (
            len(unparsed),
            " / ".join(repr(t.get("date")) + " [" + str(t.get("type", ""))[:24] + "]" for t in unparsed[:4])),
                  alive, unparsed))
        continue

    if alive:
        B.append((e, ed, alive))
        continue

    if not tickets:
        C.append((e, ed, "tickets が空（生死を判定する材料がない）", [], []))
        continue

    A.append((e, ed))


# ---------------- 出力 ----------------
W("[集計] 公演日が %s 以降（削除対象外）: %d 件 / 公演日が過去: %d 件 / 日付解析不能: %d 件"
  % (TODAY, future, len(EV) - future - len(baddate), len(baddate)))
W()

W("=" * 70)
W("(A) 削除してよい … 公演終了済み かつ 生きた販売枠ゼロ かつ saleEndUnknown なし")
W("=" * 70)
W("件数: %d" % len(A))
W()
for e, ed in sorted(A, key=lambda x: (x[1], str(x[0].get("id")))):
    W("- id=%s  公演日=%s  %s" % (e.get("id"), ed, e.get("name", "")))
    W("    会場: %s / ジャンル: %s" % (e.get("venue", ""), e.get("genre", "")))
    tds = []
    for t in (e.get("tickets") or []):
        fl = [k for k in ("soldout", "saleEnded", "saleUntilSoldOut", "saleEndUnknown") if t.get(k)]
        tds.append("%s→%s%s" % (str(t.get("type", ""))[:20], t.get("date"),
                                ("[" + ",".join(fl) + "]") if fl else ""))
    W("    枠(%d): %s" % (len(e.get("tickets") or []), " | ".join(tds)))
    W("    URL: %s" % pick_url(e))
W()
W("--- (A) の id カンマ区切り ---")
W(",".join(str(e.get("id")) for e, ed in sorted(A, key=lambda x: (x[1], str(x[0].get("id"))))))
W()

W("=" * 70)
W("(B) 公演は終わっているが消してはいけない … 販売終了日が %s 以降の生きた枠あり" % TODAY)
W("=" * 70)
W("件数: %d" % len(B))
W()
for e, ed, alive in sorted(B, key=lambda x: (x[1], str(x[0].get("id")))):
    W("- id=%s  公演日=%s  %s" % (e.get("id"), ed, e.get("name", "")))
    W("    会場: %s / ジャンル: %s" % (e.get("venue", ""), e.get("genre", "")))
    for t, td in alive:
        fl = [k for k in ("soldout", "saleEnded", "saleUntilSoldOut", "saleEndUnknown") if t.get(k)]
        W("    生きた枠: 「%s」 販売終了=%s%s" % (t.get("type", ""), td,
                                          ("  flags=" + ",".join(fl)) if fl else ""))
    W("    理由: 公演後も販売終了日が未来の枠が残っている（ルール3）")
    W("    URL: %s" % pick_url(e))
W()

W("=" * 70)
W("(C) 判断に迷った")
W("=" * 70)
W("件数: %d" % (len(C) + len(baddate)))
W()
for e, ed, why, alive, unparsed in sorted(C, key=lambda x: (x[1], str(x[0].get("id")))):
    W("- id=%s  公演日=%s  %s" % (e.get("id"), ed, e.get("name", "")))
    W("    会場: %s / ジャンル: %s" % (e.get("venue", ""), e.get("genre", "")))
    W("    引っかかり: %s" % why)
    tds = []
    for t in (e.get("tickets") or []):
        fl = [k for k in ("soldout", "saleEnded", "saleUntilSoldOut", "saleEndUnknown") if t.get(k)]
        tds.append("%s→%s%s" % (str(t.get("type", ""))[:20], t.get("date"),
                                ("[" + ",".join(fl) + "]") if fl else ""))
    W("    枠(%d): %s" % (len(e.get("tickets") or []), " | ".join(tds)))
    W("    URL: %s" % pick_url(e))
for e in baddate:
    W("- id=%s  公演日=%r（解析不能）  %s" % (e.get("id"), e.get("date"), e.get("name", "")))
    W("    引っかかり: エントリの date が YYYY-MM-DD として読めない")
    W("    URL: %s" % pick_url(e))
W()

W("=" * 70)
W("最終集計: (A)=%d件  (B)=%d件  (C)=%d件" % (len(A), len(B), len(C) + len(baddate)))
W("=" * 70)

with open(os.path.join(BASE, "tmp", "agent_delcheck_0907.txt"), "w", encoding="utf-8") as f:
    f.write(out.getvalue())

print("A=%d B=%d C=%d future=%d baddate=%d total=%d"
      % (len(A), len(B), len(C), future, len(baddate), len(EV)))
