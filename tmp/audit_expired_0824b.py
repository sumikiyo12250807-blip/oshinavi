# -*- coding: utf-8 -*-
"""2026-08-24 独立点検（第2版）: レポートを UTF-8 ファイルに出す。index.html は読み取り専用。"""
import json, re, io

SRC = r"C:\Users\user\oshinavi\index.html"
OUT = r"C:\Users\user\oshinavi\tmp\audit_expired_0824_report.txt"
TODAY = "2026-08-24"

def load_events(path):
    with io.open(path, "r", encoding="utf-8") as f:
        s = f.read()
    key = "const EVENTS = ["
    i = s.index(key)
    start = i + len(key) - 1
    depth = 0; in_str = False; esc = False; end = None
    for j in range(start, len(s)):
        c = s[j]
        if in_str:
            if esc: esc = False
            elif c == "\\": esc = True
            elif c == '"': in_str = False
            continue
        if c == '"': in_str = True
        elif c in "[{": depth += 1
        elif c in "]}":
            depth -= 1
            if depth == 0:
                end = j; break
    return json.loads(s[start:end + 1])

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

def ok(x):
    return bool(x) and bool(DATE_RE.match(str(x)))

def tstate(t):
    td, sd = t.get("date"), t.get("startDate")
    if t.get("soldout"): return "soldout"
    if ok(sd) and sd > TODAY: return "presale"
    if t.get("saleUntilSoldOut"): return "untilsold"
    if not ok(td): return "unknown"
    if td >= TODAY: return "open"
    return "expired"

def main():
    ev = load_events(SRC)
    L = []
    def p(s=""): L.append(s)

    p("OSHINAVI 独立点検 / 基準日 %s / index.html は読み取りのみ・ネットワーク未使用" % TODAY)
    p("エントリ総数 %d 件（verified=true %d / false %d）" % (
        len(ev), sum(1 for e in ev if e.get("verified") is True),
        sum(1 for e in ev if e.get("verified") is not True)))

    A, B, C = [], [], []
    weird_start = []
    for e in ev:
        ts = e.get("tickets") or []
        st = [tstate(t) for t in ts]
        for t in ts:
            if ok(t.get("startDate")) and ok(t.get("date")) and t["startDate"] == TODAY and t["date"] < TODAY:
                weird_start.append((e.get("id"), t.get("type")))
        ed = e.get("date")
        info = {
            "id": e.get("id"), "name": e.get("name") or e.get("artist"),
            "artist": e.get("artist"), "date": ed, "verified": e.get("verified"),
            "dates": sorted(set(str(t.get("date")) for t in ts)),
            "states": st, "n": len(ts),
            "soldout_n": st.count("soldout"),
            "saleEnded_n": sum(1 for t in ts if t.get("saleEnded")),
            "saleEndUnknown_n": sum(1 for t in ts if t.get("saleEndUnknown")),
            "links": {k: v for k, v in (e.get("links") or {}).items() if v and k != "amazon"},
            "genre": e.get("genre"),
        }
        if not ok(ed):
            info["why"] = "エントリの date が不正"
            B.append(info); continue
        over = ed < TODAY
        keep = []
        if "presale" in st: keep.append("発売前の枠あり")
        if "open" in st: keep.append("締切が今日以降の枠あり")
        if "untilsold" in st: keep.append("saleUntilSoldOut枠あり")
        if "unknown" in st: keep.append("日付不明の枠あり")
        if over:
            if keep:
                info["why"] = "公演終了(%s)なのに %s ＝データ矛盾" % (ed, "・".join(keep))
                B.append(info)
            else:
                info["why"] = "千秋楽 %s が過去／全枠の締切も過去(最終 %s)%s" % (
                    ed, max(info["dates"]) if info["dates"] else "枠なし",
                    "／売切枠 %d 本含む" % info["soldout_n"] if info["soldout_n"] else "")
                A.append(info)
        else:
            if not keep and info["soldout_n"] == 0:
                info["why"] = "公演日 %s は未来だが買える枠ゼロ(最終締切 %s)" % (
                    ed, max(info["dates"]) if info["dates"] else "枠なし")
                C.append(info)

    def fmt(r):
        vend = "/".join(sorted(r["links"].keys())) or "リンク無"
        return "id=%s | %s | %s | date=%s | 締切=%s | 枠%d(売切%d) | %s | %s" % (
            r["id"], r["artist"], (r["name"] or "")[:60], r["date"],
            ",".join(r["dates"]) or "なし", r["n"], r["soldout_n"], vend, r["why"])

    p("")
    p("========== A. 削除すべき（千秋楽が過去＋買える枠ゼロ）: %d 件 ==========" % len(A))
    for r in sorted(A, key=lambda x: (x["date"], x["id"])):
        p(fmt(r))
    p("")
    p("削除id: " + ",".join(str(r["id"]) for r in sorted(A, key=lambda x: x["id"])))

    p("")
    p("========== B. 要相談（公演終了だが除外条件/日付矛盾）: %d 件 ==========" % len(B))
    for r in sorted(B, key=lambda x: (str(x["date"]), x["id"])):
        p(fmt(r))
        for t, s in zip([], []):
            pass
    p("")
    p("--- B の枠明細 ---")
    for r in sorted(B, key=lambda x: (str(x["date"]), x["id"])):
        p("id=%s %s" % (r["id"], r["name"]))
        for s, dd in zip(r["states"], r["dates"]):
            pass
    p("")
    p("========== C. 公演日は未来だが買える枠ゼロ（除外条件3で削除せず・要相談）: %d 件 ==========" % len(C))
    for r in sorted(C, key=lambda x: (x["date"], x["id"])):
        p(fmt(r))

    p("")
    p("========== 補足 ==========")
    p("startDate=今日 かつ 締切が過去 の異常枠: %d 件" % len(weird_start))
    for wid, wt in weird_start[:20]:
        p("  id=%s %s" % (wid, wt))
    # 公演日が過去のエントリ総数
    past = [e for e in ev if ok(e.get("date")) and e["date"] < TODAY]
    p("公演日が %s より前のエントリ: %d 件（= A %d + B %d）" % (TODAY, len(past), len(A), len(B)))
    from collections import Counter
    p("その date 分布: %s" % dict(Counter(e["date"] for e in past)))
    # C のうち販売終了フラグ持ち
    p("C のうち saleEndUnknown 枠を持つもの: %d 件" % sum(1 for r in C if r["saleEndUnknown_n"]))

    with io.open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    print("written %d lines -> %s" % (len(L), OUT))

main()
