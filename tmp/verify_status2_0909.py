# -*- coding: utf-8 -*-
"""今日足された枠の「実際の飛び先URL」(t.url優先)を叩いて状態文言を読む。"""
import json
import re
import sys
import io
import time
from collections import Counter

sys.path.insert(0, r"C:\Users\user\oshinavi\tools")
from build_pia_entries import fetch          # noqa: E402
from pia_statustext import statuses          # noqa: E402

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


def load_events(path):
    lines = io.open(path, "r", encoding="utf-8").read().split("\n")
    start = next(i for i, ln in enumerate(lines) if ln.strip() == "const EVENTS = [")
    end = next(j for j in range(start + 1, len(lines)) if lines[j].rstrip("\r") == "];")
    body = "\n".join(lines[start:end + 1]).replace("const EVENTS = [", "[", 1).rstrip()
    return json.loads(body[:-1]), start, end


DATE_PATS = [re.compile(p) for p in [
    r"\d{4}-\d{1,2}-\d{1,2}", r"\d{1,2}\s*/\s*\d{1,2}", r"\d{1,2}\s*:\s*\d{2}",
    r"\d{4}\s*年", r"\d{1,2}\s*月\s*\d{1,2}\s*日", r"\d{1,2}\s*月", r"\d{1,2}\s*日"]]
NOISE = re.compile(r"(発売開始|発売予定|発売終了|販売開始|販売終了|受付開始|受付終了|申込開始|申込締切|締切|まで|発売|受付|より)")


def skel(s):
    s = s or ""
    for p in DATE_PATS:
        s = p.sub("#", s)
    s = NOISE.sub("", s)
    return re.sub(r"[#\s〜~\-－―（）\(\)・,、。／/]+", "", s)


NEW = r"C:\Users\user\oshinavi\index.html"
OLD = r"C:\Users\user\oshinavi\index.html.bak_0909_prenoonheal"

new_events, _, _ = load_events(NEW)
old_events, _, _ = load_events(OLD)
new_by_id = {e["id"]: e for e in new_events}
old_by_id = {e["id"]: e for e in old_events}

rows = []
for i in sorted(set(old_by_id) & set(new_by_id)):
    o, n = old_by_id[i], new_by_id[i]
    oc = Counter(skel(t.get("type")) for t in o.get("tickets", []))
    nc = Counter(skel(t.get("type")) for t in n.get("tickets", []))
    gain = nc - oc
    for k in gain:
        for t in n.get("tickets", []):
            if skel(t.get("type")) == k:
                url = t.get("url") or (n.get("links") or {}).get("pia")
                rows.append((i, n.get("artist"), n.get("name"), t, url))
                break

# 別々のエントリから最大8件、ぴあURLを持つものだけ
seen, picked = set(), []
for i, art, nm, t, url in rows:
    if i in seen or not url or "pia.jp" not in url:
        continue
    seen.add(i)
    picked.append((i, art, nm, t, url))
    if len(picked) >= 8:
        break

buf = []
buf.append("対象エントリ数(枠が足された)=%d / ぴあURLで抜き取り=%d" % (len(set(r[0] for r in rows)), len(picked)))
for i, art, nm, t, url in picked:
    buf.append("")
    buf.append("=== id=%s %s / %s" % (i, art, nm))
    buf.append("    type=%s" % t.get("type"))
    buf.append("    start=%s end=%s soldout=%s saleEnded=%s" % (
        t.get("startDate"), t.get("date"), t.get("soldout"), t.get("saleEnded")))
    buf.append("    URL=%s" % url)
    try:
        h = fetch(url)
    except Exception as e:
        buf.append("    取得できなかった: %s: %s" % (e.__class__.__name__, e))
        continue
    st = statuses(h)
    if not st:
        buf.append("    状態文言が1つも取れなかった(ページ形式が違う可能性)  len(html)=%d" % len(h))
    cnt = Counter(x[0] for x in st)
    buf.append("    状態集計: %s" % dict(cnt))
    for txt, cls, around in st:
        buf.append("      [%s] %s | …%s" % (txt, cls, around[-110:]))
    time.sleep(1.5)

out = r"C:\Users\user\oshinavi\tmp\verify_status2_0909.txt"
io.open(out, "w", encoding="utf-8").write("\n".join(buf) + "\n")
print("wrote %s (%d lines)" % (out, len(buf)))
