# -*- coding: utf-8 -*-
import re, json, io, sys, datetime

SRC = r"C:\Users\user\oshinavi\index.html"
OUT = r"C:\Users\user\oshinavi\tmp\_agentA_report.txt"
TODAY = "2026-08-31"

with io.open(SRC, "r", encoding="utf-8") as f:
    html = f.read()

m = re.search(r"const EVENTS\s*=\s*(\[.*?\]);", html, re.S)
if not m:
    print("EVENTS not found"); sys.exit(1)
EVENTS = json.loads(m.group(1))

DATE_RE = re.compile(r"(20\d{2})[-/](\d{1,2})[-/](\d{1,2})")
# 日本語表記 M/D や M月D日
MD_RE = re.compile(r"(\d{1,2})\s*[/月]\s*(\d{1,2})\s*日?")

def norm(d):
    if not d: return None
    mm = DATE_RE.search(str(d))
    if mm:
        return "%04d-%02d-%02d" % (int(mm.group(1)), int(mm.group(2)), int(mm.group(3)))
    return None

def collect_text(o, acc):
    if isinstance(o, dict):
        for k, v in o.items():
            collect_text(v, acc)
    elif isinstance(o, list):
        for v in o:
            collect_text(v, acc)
    elif isinstance(o, str):
        acc.append(o)

lines = []
def W(s):
    lines.append(s)

past = []
for e in EVENTS:
    d = norm(e.get("date"))
    if d and d < TODAY:
        past.append(e)

W("=== 公演日(date)が %s より前のエントリ: %d 件 / 全 %d 件 ===" % (TODAY, len(past), len(EVENTS)))
W("")

clean = []
flagged = []

for e in past:
    eid = e.get("id")
    artist = e.get("artist") or ""
    title = e.get("title") or ""
    edate = norm(e.get("date"))
    tickets = e.get("tickets") or []

    reasons = []
    tk_end_dates = []
    tk_rows = []
    for i, t in enumerate(tickets):
        td = norm(t.get("date"))          # 販売終了日
        tsd = norm(t.get("startDate"))    # 販売開始日
        if td: tk_end_dates.append(td)
        tk_rows.append((i, tsd, td, t.get("type") or "", t.get("dateLabel") or "",
                        t.get("soldOut"), t.get("saleEnded"), t.get("status"),
                        (t.get("url") or "")[:0]))
        # まだ買える枠 (販売終了日が今日以降)
        if td and td >= TODAY:
            reasons.append("枠#%d 販売終了日 %s が今日以降（まだ買える枠）: type=%r dateLabel=%r" % (i, td, t.get("type"), t.get("dateLabel")))
        if tsd and tsd >= TODAY:
            reasons.append("枠#%d 販売開始日 %s が今日以降（これから発売）: type=%r dateLabel=%r" % (i, tsd, t.get("type"), t.get("dateLabel")))

    # 文言中の 9月以降の日付（M/D, M月D日）を探す
    texts = []
    for t in tickets:
        for key in ("type", "dateLabel", "name", "note"):
            v = t.get(key)
            if isinstance(v, str): texts.append((key, v))
    for key in ("title", "subtitle", "note", "venue", "description"):
        v = e.get(key)
        if isinstance(v, str): texts.append((key, v))

    future_mentions = []
    for key, v in texts:
        for mm in MD_RE.finditer(v):
            mo, da = int(mm.group(1)), int(mm.group(2))
            if not (1 <= mo <= 12 and 1 <= da <= 31): continue
            # 年を推定: 9-12月は2026、1-8月は2027の可能性もあるが、まずは2026年として比較
            cand = "2026-%02d-%02d" % (mo, da)
            if mo >= 9:  # 9月以降の言及
                future_mentions.append("%s=%r に %d/%d" % (key, v[:60], mo, da))
                break
    if future_mentions:
        reasons.append("9月以降の日付が文言にある: " + " | ".join(sorted(set(future_mentions))[:4]))

    # dateが初日で、ticketsにもっと先の公演日がある可能性 -> 上の文言チェックでカバー
    last_end = max(tk_end_dates) if tk_end_dates else None

    rec = {
        "id": eid, "artist": artist, "title": title, "date": edate,
        "last_ticket_end": last_end, "n_tickets": len(tickets),
        "reasons": reasons, "rows": tk_rows,
    }
    if reasons:
        flagged.append(rec)
    else:
        clean.append(rec)

W("--- 一覧 (id / artist / title / date / 枠の最終締切日) ---")
for r in sorted(past, key=lambda x: norm(x.get("date")) or ""):
    tks = r.get("tickets") or []
    ends = [norm(t.get("date")) for t in tks if norm(t.get("date"))]
    W("%s\t%s\t%s\t%s\t%s" % (r.get("id"), (r.get("artist") or "")[:30], (r.get("title") or "")[:50],
                              norm(r.get("date")), max(ends) if ends else "-"))
W("")
W("=== 問題なく削除できると判断 (%d 件) ===" % len(clean))
for r in clean:
    W("%s\t%s\t%s\tdate=%s\t最終締切=%s\t枠数=%d" % (r["id"], r["artist"][:26], r["title"][:44], r["date"], r["last_ticket_end"], r["n_tickets"]))
W("")
W("=== 削除に疑義あり (%d 件) ===" % len(flagged))
for r in flagged:
    W("%s\t%s\t%s\tdate=%s\t最終締切=%s" % (r["id"], r["artist"][:26], r["title"][:44], r["date"], r["last_ticket_end"]))
    for rs in r["reasons"]:
        W("      - " + rs)
    for row in r["rows"]:
        W("      枠#%d start=%s end=%s type=%r label=%r soldOut=%r saleEnded=%r" % (row[0], row[1], row[2], row[3][:60], row[4][:60], row[5], row[6]))
W("")

with io.open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("wrote", OUT, "past=", len(past), "clean=", len(clean), "flagged=", len(flagged))
