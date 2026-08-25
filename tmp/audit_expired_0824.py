# -*- coding: utf-8 -*-
"""2026-08-24 朝の独立点検: EVENTS 配列から「削除すべきエントリ」を機械的に洗い出す。
index.html は読み取り専用。ネットワークアクセスなし。日付判定のみ。
"""
import json, re, io, sys, os

SRC = r"C:\Users\user\oshinavi\index.html"
TODAY = "2026-08-24"

def load_events(path):
    with io.open(path, "r", encoding="utf-8") as f:
        s = f.read()
    key = "const EVENTS = ["
    i = s.index(key)
    start = i + len(key) - 1  # '[' の位置
    # 文字列リテラルを考慮した括弧バランスで終端を探す
    depth = 0
    in_str = False
    esc = False
    end = None
    for j in range(start, len(s)):
        c = s[j]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
            continue
        if c == '"':
            in_str = True
        elif c in "[{":
            depth += 1
        elif c in "]}":
            depth -= 1
            if depth == 0:
                end = j
                break
    if end is None:
        raise RuntimeError("EVENTS 配列の終端が見つからない")
    raw = s[start:end + 1]
    return json.loads(raw), raw

def d(x):
    """YYYY-MM-DD 文字列比較（辞書順＝時系列順）。None は None のまま。"""
    if not x:
        return None
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", x):
        return "BAD:" + str(x)
    return x

def ticket_state(t):
    """1枠の状態を返す。
    presale : 発売日がまだ来ていない（明日以降）
    open    : 締切が今日以降＝まだ買える
    soldout : 売切マーク
    untilsold: 予定枚数終了まで（無期限）
    expired : 締切が過去
    unknown : 日付が読めない
    """
    td = d(t.get("date"))
    sd = d(t.get("startDate"))
    if t.get("soldout"):
        return "soldout"
    if sd and not str(sd).startswith("BAD") and sd > TODAY:
        return "presale"
    if t.get("saleUntilSoldOut"):
        return "untilsold"
    if td is None or str(td).startswith("BAD"):
        return "unknown"
    if td >= TODAY:
        return "open"
    return "expired"

def main():
    events, raw = load_events(SRC)
    print("エントリ総数: %d" % len(events))
    ids = [e.get("id") for e in events]
    print("id重複: %d" % (len(ids) - len(set(ids))))

    delete = []      # 公演終了かつ買える枠ゼロ
    consult = []     # 要相談
    zero_future = [] # 公演日は未来だが買える枠ゼロ

    for e in events:
        eid = e.get("id")
        name = e.get("name") or e.get("artist")
        ed = d(e.get("date"))
        tickets = e.get("tickets") or []
        states = [ticket_state(t) for t in tickets]
        tdates = [str(t.get("date")) for t in tickets]
        has_presale = "presale" in states
        has_open = "open" in states
        has_soldout = "soldout" in states
        has_untilsold = "untilsold" in states
        has_unknown = "unknown" in states
        rec = {
            "id": eid, "name": name, "artist": e.get("artist"), "date": e.get("date"),
            "verified": e.get("verified"), "genre": e.get("genre"),
            "ticket_dates": tdates, "states": states,
            "n_tickets": len(tickets),
            "soldoutSince": e.get("soldoutSince"),
            "saleEnded": any(t.get("saleEnded") for t in tickets),
            "saleEndUnknown": any(t.get("saleEndUnknown") for t in tickets) or e.get("saleEndUnknown"),
            "longrun": e.get("longrun"),
            "pia": (e.get("links") or {}).get("pia"),
            "rakuten": (e.get("links") or {}).get("rakuten"),
            "eplus": (e.get("links") or {}).get("eplus"),
            "lawson": (e.get("links") or {}).get("lawson"),
        }

        if ed is None or str(ed).startswith("BAD"):
            rec["why"] = "エントリの date が読めない"
            consult.append(rec)
            continue

        show_over = ed < TODAY

        if show_over:
            # 除外条件の確認
            reasons_keep = []
            if has_presale:
                reasons_keep.append("発売日が未来の枠あり（※公演は終わっているのに発売前＝データ矛盾）")
            if has_open:
                reasons_keep.append("締切が今日以降の枠あり（※公演終了後の締切＝データ矛盾）")
            if has_untilsold:
                reasons_keep.append("saleUntilSoldOut 枠あり")
            if has_unknown:
                reasons_keep.append("日付が読めない枠あり")
            if reasons_keep:
                rec["why"] = "公演終了(%s)だが: %s" % (ed, " / ".join(reasons_keep))
                consult.append(rec)
            else:
                # soldout は公演日が来ていない時だけ保護 → ここは公演終了なので保護対象外
                rec["why"] = "千秋楽 %s が過去。全枠の締切も過去（最終締切 %s）＝もう買えない" % (
                    ed, max(tdates) if tdates else "枠なし")
                if not tickets:
                    rec["why"] = "千秋楽 %s が過去。tickets 配列が空" % ed
                delete.append(rec)
        else:
            # 公演日が今日以降 → 除外条件3で削除しない
            if not (has_presale or has_open or has_untilsold or has_soldout or has_unknown):
                rec["why"] = "公演日 %s は未来だが、買える枠がゼロ（全締切が過去・最終 %s）" % (
                    ed, max(tdates) if tdates else "枠なし")
                zero_future.append(rec)

    def line(r):
        return u"id=%s | %s | date=%s | 締切=%s | %s | verified=%s" % (
            r["id"], (r["name"] or "")[:48], r["date"],
            ",".join(sorted(set(r["ticket_dates"]))) or "なし",
            r["why"], r["verified"])

    print("\n===== A. 削除すべき（公演終了＋買える枠ゼロ）: %d 件 =====" % len(delete))
    for r in sorted(delete, key=lambda x: (x["date"] or "", x["id"])):
        print(line(r))

    print("\n===== B. 要相談（公演終了だが除外条件に当たる/日付異常）: %d 件 =====" % len(consult))
    for r in sorted(consult, key=lambda x: (x["date"] or "", x["id"])):
        print(line(r))

    print("\n===== C. 公演日は未来だが買える枠ゼロ（除外条件3で削除せず・要相談）: %d 件 =====" % len(zero_future))
    for r in sorted(zero_future, key=lambda x: (x["date"] or "", x["id"])):
        print(line(r))

    out = {
        "today": TODAY,
        "total": len(events),
        "delete": delete,
        "consult": consult,
        "zero_future": zero_future,
    }
    op = r"C:\Users\user\oshinavi\tmp\audit_expired_0824.json"
    with io.open(op, "w", encoding="utf-8") as f:
        f.write(json.dumps(out, ensure_ascii=False, indent=1))
    print("\n削除id一覧: %s" % ",".join(str(r["id"]) for r in sorted(delete, key=lambda x: x["id"])))
    print("JSON: %s" % op)

main()
