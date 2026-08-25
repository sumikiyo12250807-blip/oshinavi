# -*- coding: utf-8 -*-
"""削除候補の「本当の最終公演日」を dateLabel / バッジ文言の M/D から独立に再導出し、
エントリの date（千秋楽）より後ろの公演が隠れていないかを検査する。"""
import json, io, re, datetime

SRC = r"C:\Users\user\oshinavi\index.html"
OUT = r"C:\Users\user\oshinavi\tmp\crosscheck_out.txt"
TODAY = datetime.date(2026, 8, 24)

CAND = [68,275,292,407,427,460,536,600,826,999,1009,1021,1026,1041,1043,1105,1197,1487,1626,1796,
        1907,2019,2036,2049,2385,2534,2550,2672,2737,2846,2931,3078,3103,3296,3313,3391,3650,3790,
        3797,4013,4072,4130,4132,4243,4470,4473,4485,4818]

def load_events(path):
    s = io.open(path, "r", encoding="utf-8").read()
    key = "const EVENTS = ["
    i = s.index(key); start = i + len(key) - 1
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
            if depth == 0: end = j; break
    return json.loads(s[start:end+1])

# 「（… M/D公演）」「（… M/D〜M/D公演）」「（… M/D-M/D公演）」から公演日を拾う。
SHOW_RE = re.compile(r"(\d{1,2})/(\d{1,2})(?:\s*[〜~\-]\s*(?:(\d{1,2})/)?(\d{1,2}))?\s*(?:[^）)]{0,6})?公演")
# dateLabel の「2026年8月23日(日)」形
LBL_RE = re.compile(r"(\d{4})年(\d{1,2})月(\d{1,2})日")

def md_to_date(m, d, base_year=2026):
    try:
        return datetime.date(base_year, m, d)
    except ValueError:
        return None

ev = load_events(SRC)
L = []
flag = []
for e in ev:
    if e.get("id") not in CAND:
        continue
    entry_date = datetime.datetime.strptime(e["date"], "%Y-%m-%d").date()
    found = []
    # dateLabel の年月日
    for y, m, d in LBL_RE.findall(e.get("dateLabel") or ""):
        try:
            found.append(("dateLabel", datetime.date(int(y), int(m), int(d))))
        except ValueError:
            pass
    # チケット種別の M/D公演
    for t in (e.get("tickets") or []):
        txt = t.get("type") or ""
        for m1, d1, m2, d2 in SHOW_RE.findall(txt):
            a = md_to_date(int(m1), int(d1))
            if a: found.append(("badge", a))
            if d2:
                b = md_to_date(int(m2) if m2 else int(m1), int(d2))
                if b: found.append(("badge", b))
    mx = max([d for _, d in found], default=None)
    line = "id=%s | date=%s | 文言から拾った最終公演日=%s | 拾えた日付数=%d | %s" % (
        e["id"], e["date"], mx, len(found), (e.get("name") or "")[:40])
    if mx and mx > entry_date:
        line = "★ズレ " + line
        flag.append(e["id"])
    elif mx is None:
        line = "?日付拾えず " + line
    L.append(line)

L.append("")
L.append("date より後ろの公演日が文言に出てくる候補: %s" % (flag or "なし"))
L.append("検査した候補数: %d" % len(CAND))
io.open(OUT, "w", encoding="utf-8").write("\n".join(L))
print("ok")
