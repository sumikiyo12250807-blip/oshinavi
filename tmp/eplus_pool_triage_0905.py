# -*- coding: utf-8 -*-
"""e+の未登録プール（tmp/_word_pool_miss_0901.json・326件）を
「これから発売」「受付中」「終了済み」に仕分ける。夜にユーザーへ見せる表の下ごしらえ。
🚨 ネットは叩かない。json に入っている windows（販売期間）の日付だけで判定する。"""
import json, io, re, datetime

SRC = "tmp/_word_pool_miss_0901.json"
OUT = "tmp/eplus_pool_triage_0905.txt"
TODAY = datetime.date.today()

pool = json.load(io.open(SRC, encoding="utf-8"))

def parse(s):
    m = re.search(r"(\d{4})[/-](\d{1,2})[/-](\d{1,2})", s or "")
    if not m:
        return None
    try:
        return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None

pre, live, dead, unknown = [], [], [], []
for it in pool:
    # windows は [枠名, 開始日, 終了日] の配列
    starts, ends, slots = [], [], []
    for w in (it.get("windows") or []):
        if isinstance(w, (list, tuple)) and len(w) >= 3:
            nm, s, e = str(w[0]), parse(str(w[1])), parse(str(w[2]))
        else:
            nm = ""
            ds = re.findall(r"\d{4}[/-]\d{1,2}[/-]\d{1,2}", str(w))
            s = parse(ds[0]) if ds else None
            e = parse(ds[-1]) if len(ds) > 1 else None
        slots.append((nm, s, e))
        if s:
            starts.append(s)
        if e:
            ends.append(e)
    it["_slots"] = slots
    if starts and min(starts) > TODAY:
        pre.append((it, min(starts), max(ends) if ends else None))
    elif ends and max(ends) >= TODAY:
        live.append((it, min(starts) if starts else None, max(ends)))
    elif ends:
        dead.append((it, None, max(ends)))
    else:
        unknown.append((it, None, None))

def fmt(rows, label):
    out = ["=== %s … %d件 ===" % (label, len(rows))]
    for it, s, e in sorted(rows, key=lambda r: (r[1] or datetime.date(2099, 1, 1), r[0].get("date") or "")):
        out.append("%s | %s | %s(%s) | 公演%s %s開演"
                   % (it.get("eid", "-"), it.get("name", ""), it.get("venue", ""),
                      it.get("pref", ""), it.get("date", ""), it.get("time", "")))
        for nm, ws, we in it.get("_slots", []):
            out.append("        枠: %s | 受付 %s〜%s"
                       % (nm, ws.isoformat() if ws else "?", we.isoformat() if we else "?"))
        out.append("        %s" % (it.get("url") or "-"))
    out.append("")
    return out

buf = ["e+未登録プール %d件の仕分け（today=%s・ローカル判定のみ）" % (len(pool), TODAY), "",
       "  これから発売 … %d件" % len(pre),
       "  受付中       … %d件" % len(live),
       "  終了済み     … %d件" % len(dead),
       "  判定不能     … %d件" % len(unknown), ""]
buf += fmt(pre, "これから発売（夜にユーザーへ見せる候補）")
io.open(OUT, "w", encoding="utf-8").write("\n".join(buf))
print("PRE=%d LIVE=%d DEAD=%d UNKNOWN=%d -> %s" % (len(pre), len(live), len(dead), len(unknown), OUT))
