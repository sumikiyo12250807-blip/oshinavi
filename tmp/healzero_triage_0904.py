# -*- coding: utf-8 -*-
"""ヒールが「買える枠ゼロ」と言ったエントリを仕分ける。

🚨いちばん大事な除外＝**今日これから発売の枠**。
   ぴあは発売時刻を過ぎるまで枠を出さないので、朝に見ると0枠に見える（DELETE_GATE 2-4）。
   これを削除候補に混ぜると、その日の主役を消すことになる。

出力3群：
  X 今日これから発売の枠を持つ（朝は判定できない＝昼/夜のヒールへ）
  Y 公演が今日以前（＝もう終わっている。削除ルートの正常な入口）
  Z それ以外（＝本当に要確認）
"""
import json, re, io, datetime

TODAY = "2026-09-04"
NOW = datetime.datetime.now().strftime("%H:%M")

log = io.open("tmp/heal_build_0904.txt", encoding="utf-8").read()
zero_ids = [int(m) for m in re.findall(r"^\[\d+/\d+\] (\d+) 買える枠ゼロ", log, re.M)]

html = io.open("index.html", encoding="utf-8", newline="").read()
events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", html, re.S).group(1))
by_id = {e.get("id"): e for e in events}

X, Y, Z = [], [], []
for i in zero_ids:
    e = by_id.get(i)
    if not e:
        continue
    ts = e.get("tickets", [])
    # 今日これから発売＝type に「M/D HH:MM発売」があって、その日付が今日で時刻が今より後
    future_today = []
    for t in ts:
        m = re.search(r"(\d{1,2})/(\d{1,2})\s+(\d{1,2}):(\d{2})発売", t.get("type", ""))
        if not m:
            continue
        d = "2026-%02d-%02d" % (int(m.group(1)), int(m.group(2)))
        hhmm = "%02d:%s" % (int(m.group(3)), m.group(4))
        if d == TODAY and hhmm > NOW:
            future_today.append(hhmm)
    if future_today:
        X.append((i, e.get("name"), sorted(future_today)))
    elif (e.get("date") or "") <= TODAY:
        Y.append((i, e.get("name"), e.get("date")))
    else:
        Z.append((i, e.get("name"), e.get("date"), len(ts)))

buf = ["ヒール「買える枠ゼロ」の仕分け（today=%s now=%s）" % (TODAY, NOW), ""]
for tag, g in (("X 今日これから発売＝朝は判定できない（昼/夜へ）", X),
               ("Y 公演が今日以前＝削除ルートへ", Y),
               ("Z それ以外＝要確認", Z)):
    buf.append("=" * 70)
    buf.append("【%s】 %d件" % (tag, len(g)))
    for row in g:
        buf.append("  id=%-5s %s  %s" % (row[0], (row[1] or "")[:44], row[2]))
io.open("tmp/healzero_triage_0904.txt", "w", encoding="utf-8").write("\n".join(buf))

print("ZERO_TOTAL=%d" % len(zero_ids))
print("X_today_future_sale=%d  Y_past_show=%d  Z_need_check=%d" % (len(X), len(Y), len(Z)))
print("Z_IDS=" + ",".join(str(r[0]) for r in Z))
