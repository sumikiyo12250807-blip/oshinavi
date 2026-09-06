# -*- coding: utf-8 -*-
"""公演日が過去のエントリについて、dateLabel / 券種名の中に 9/7 以降の日付が
書かれていないかを機械で点検する（date の付け間違いを炙る）。ネットワーク未使用。"""
import re, json, io, os

BASE = r"C:\Users\user\oshinavi"
TODAY = (2026, 9, 7)
h = open(os.path.join(BASE, "index.html"), encoding="utf-8").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\n", h, re.S).group(1))

def nd(d):
    if not d or not isinstance(d, str):
        return None
    mm = re.match(r"^(\d{4})[-/](\d{1,2})[-/](\d{1,2})", d.strip())
    return "%04d-%02d-%02d" % tuple(map(int, mm.groups())) if mm else None

past = [e for e in EV if nd(e.get("date")) and nd(e["date"]) < "2026-09-07"]

out = io.StringIO()
W = lambda s="": out.write(s + "\n")
W("### dateLabel 点検：公演日が過去のエントリに 9/7 以降の日付表記が残っていないか")
W()

# 全角も半角に寄せてから M/D を拾う
Z2H = str.maketrans("０１２３４５６７８９／", "0123456789/")
pat = re.compile(r"(\d{1,2})/(\d{1,2})")

hit = 0
for e in past:
    lab = (e.get("dateLabel") or "").translate(Z2H)
    fut = []
    for mo, da in pat.findall(lab):
        mo, da = int(mo), int(da)
        if not (1 <= mo <= 12 and 1 <= da <= 31):
            continue
        # 年は 2026 とみなす（サイトの掲載範囲）
        if (2026, mo, da) >= TODAY:
            fut.append("%d/%d" % (mo, da))
    if fut:
        hit += 1
        W("- id=%s  date=%s  %s" % (e.get("id"), e.get("date"), e.get("name")))
        W("    dateLabel: %s" % e.get("dateLabel"))
        W("    9/7以降と読める表記: %s" % ", ".join(fut))
W()
W("該当 %d 件 / 公演日が過去 %d 件" % (hit, len(past)))
W()

# 参考：公演日が過去のエントリの dateLabel 一覧（目視用ではなく記録用）
W("### 参考：公演日が過去のエントリの id / date / dateLabel")
for e in sorted(past, key=lambda x: (nd(x["date"]), str(x.get("id")))):
    W("  id=%-6s date=%s  label=%-34s  %s"
      % (e.get("id"), e.get("date"), (e.get("dateLabel") or "")[:34], e.get("name")))

with open(os.path.join(BASE, "tmp", "agent_delcheck_0907_label.txt"), "w", encoding="utf-8") as f:
    f.write(out.getvalue())
print("label check done hit=%d past=%d" % (hit, len(past)))
