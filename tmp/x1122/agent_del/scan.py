# 削除の独立チェック（読むだけ）。前提＝削除は誤り。言い切れるものだけ delete。
import json, re, os, datetime as dt
from collections import Counter

SRC = r"C:\Users\user\oshinavi\index.html"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "result.json")
TODAY = dt.date(2026, 11, 22)
CUT = dt.date(2026, 11, 21)

LONG_WORDS = ["配信", "見逃し", "アーカイブ", "展", "会期", "ロングラン", "常設", "開催中",
              "期間", "上映", "ストリーミング", "オンライン", "通年", "年間", "シーズン",
              "延長", "追加", "随時", "毎日", "毎週", "定期", "パス", "未定"]

s = open(SRC, encoding="utf-8").read()
i = s.index("const EVENTS = [") + len("const EVENTS = ")
events, _ = json.JSONDecoder().raw_decode(s, i)


def pdate(v):
    if not isinstance(v, str):
        return None
    m = re.match(r"\s*(\d{4})[-/](\d{1,2})[-/](\d{1,2})", v)
    if not m:
        return None
    try:
        return dt.date(int(m[1]), int(m[2]), int(m[3]))
    except ValueError:
        return None


def text_dates(t, ev_date):
    """文字列から読める日付のうち『今日以降かもしれない』ものの理由を返す"""
    out = []
    t = t.translate(str.maketrans("０１２３４５６７８９／", "0123456789/"))
    if re.search(r"20(2[7-9]|[3-9]\d)", t):
        out.append("text_year_2027+")
    if re.search(r"(R|令和)\s*(9|1\d)\s*年?", t):
        out.append("text_reiwa9+")
    # 年つき
    for m in re.finditer(r"(20\d\d)\s*[年/\-.]\s*(\d{1,2})\s*[月/\-.]\s*(\d{1,2})", t):
        try:
            d = dt.date(int(m[1]), int(m[2]), int(m[3]))
            if d >= TODAY:
                out.append("text_date_future")
        except ValueError:
            out.append("text_date_unreadable")
    # 年なし M/D・M月D日
    t2 = re.sub(r"(20\d\d)\s*[年/\-.]\s*(\d{1,2})\s*[月/\-.]\s*(\d{1,2})", " ", t)
    for m in re.finditer(r"(?<![\d/])(\d{1,2})\s*(?:/|月)\s*(\d{1,2})(?!\d)", t2):
        mo, da = int(m[1]), int(m[2])
        if not (1 <= mo <= 12 and 1 <= da <= 31):
            continue
        try:
            d = dt.date(2026, mo, da)
        except ValueError:
            continue
        if d >= TODAY:
            out.append("text_md_future")
        elif ev_date and d < ev_date - dt.timedelta(days=120):
            out.append("text_md_year_ambiguous")
    return out


def walk_strings(o, skip=("url", "links")):
    if isinstance(o, str):
        yield o
    elif isinstance(o, list):
        for x in o:
            yield from walk_strings(x, skip)
    elif isinstance(o, dict):
        for k, v in o.items():
            if k in skip:
                continue
            yield from walk_strings(v, skip)


delete, keep = [], {}
rc_all, rc_primary = Counter(), Counter()

for e in events:
    eid = e.get("id")
    ed = pdate(e.get("date"))
    if ed is None:
        # date が読めない＝対象外に見えても念のため残す（keep には date<=11/6 のみ載せる指示なので記録だけ）
        continue
    if ed > CUT:
        continue
    reasons = []
    for flag in ("saleEndUnknown", "longrun", "saleUntilSoldOut", "showSalePeriod"):
        if e.get(flag):
            reasons.append("entry_flag_" + flag)
    texts = [e.get("name") or "", e.get("artist") or "", e.get("dateLabel") or "", e.get("venue") or ""]
    for k in ("_parts", "_fanyEvents"):
        if k in e:
            texts.extend(walk_strings(e[k]))
    for t in texts:
        if not isinstance(t, str):
            continue
        for w in LONG_WORDS:
            if w in t:
                reasons.append("longrun_word")
                break
        reasons.extend(text_dates(t, ed))
    tickets = e.get("tickets")
    if not isinstance(tickets, list):
        reasons.append("tickets_unreadable")
        tickets = []
    for tk in tickets:
        if not isinstance(tk, dict):
            reasons.append("ticket_unreadable")
            continue
        for flag in ("saleUntilSoldOut", "saleEndUnknown", "_alive"):
            if tk.get(flag):
                reasons.append("ticket_flag_" + flag)
        td = pdate(tk.get("date"))
        if td is None:
            reasons.append("ticket_deadline_unreadable")
        elif td >= TODAY:
            reasons.append("ticket_deadline_future_soldout" if tk.get("soldout") else "ticket_deadline_future")
        if tk.get("startDate") is not None:
            sd = pdate(tk.get("startDate"))
            if sd is None:
                reasons.append("ticket_start_unreadable")
            elif sd >= TODAY:
                reasons.append("ticket_start_future")
        ty = tk.get("type") or ""
        for w in LONG_WORDS:
            if w in ty:
                reasons.append("longrun_word_in_ticket")
                break
        reasons.extend(r.replace("text_", "ticket_text_") for r in text_dates(ty, ed))
    # 重複を順序を保って除く
    seen, uniq = set(), []
    for r in reasons:
        if r not in seen:
            seen.add(r)
            uniq.append(r)
    if uniq:
        keep[str(eid)] = " / ".join(uniq)
        rc_primary[uniq[0]] += 1
        for r in uniq:
            rc_all[r] += 1
    else:
        delete.append(eid)

res = {
    "today": str(TODAY),
    "total_events": len(events),
    "delete": delete,
    "keep": keep,
    "reason_counts": dict(rc_all.most_common()),
    "reason_counts_primary": dict(rc_primary.most_common()),
}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
print("events", len(events), "delete", len(delete), "keep", len(keep))
print("reasons(all)", json.dumps(dict(rc_all.most_common())))
print("reasons(primary)", json.dumps(dict(rc_primary.most_common())))
