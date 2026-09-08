# -*- coding: utf-8 -*-
"""統合(merge_apply)が date/dateLabel/venue/prefecture を「再ビルドの値」で上書きするせいで、
**買える枠が残っている会場だけに会期と会場一覧が縮む**のを直す。

🚨公演日は「事実の会期」で書く＝買える範囲に縮めない（feedback_show_true_dates_not_sellable_range）。
やること＝統合前(HEAD)と現物を比べて、
  ・date は遅いほう（千秋楽が後ろのほう）を採る
  ・venue の「全国ツアー（…／…）」の中身は和集合
  ・prefecture も和集合
  ・dateLabel は date を採ったほうの側の表記をそのまま使う（作文しない）
使い方: python tmp/merge_restore_range_0909.py [--apply]
"""
import subprocess, sys, os, re, json, io

sys.stdout.reconfigure(encoding="utf-8")
REPO = os.getcwd()
head = subprocess.run(["git", "show", "HEAD:index.html"], capture_output=True).stdout.decode("utf-8", "replace")
old = {e["id"]: e for e in json.loads(re.search(r"const EVENTS = (\[.*?\]);\n", head, re.S).group(1))}

h = io.open("index.html", encoding="utf-8", newline="").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
events = json.loads(m.group(2))

VEN = re.compile(r"^(.*?)（(.*)）$")


def venues(v):
    v = v or ""
    mm = VEN.match(v)
    return (mm.group(1), [x for x in mm.group(2).split("／") if x]) if mm else (None, [v] if v else [])


fixed = []
for e in events:
    o = old.get(e["id"])
    if not o:
        continue
    ch = []
    # ① 千秋楽は遅いほう。dateLabel は採ったほうの表記をそのまま使う（作文しない）
    if (o.get("date") or "") > (e.get("date") or ""):
        ch.append("date %s→%s" % (e.get("date"), o.get("date")))
        e["date"] = o["date"]
        if o.get("dateLabel"):
            e["dateLabel"] = o["dateLabel"]
    # ② 会場は和集合（順は旧→新で、重複は落とす）
    ph_o, vo = venues(o.get("venue"))
    ph_n, vn = venues(e.get("venue"))
    if ph_o or ph_n:
        u = list(dict.fromkeys(vo + vn))
        if len(u) > len(vn):
            ph = ph_o or ph_n
            e["venue"] = "%s（%s）" % (ph, "／".join(u))
            ch.append("会場 %d→%d" % (len(vn), len(u)))
    elif vo and not set(vo) <= set(vn):
        u = list(dict.fromkeys(vo + vn))
        if len(u) > 1:
            e["venue"] = "全国ツアー（%s）" % "／".join(u)
            ch.append("会場 %d→%d" % (len(vn), len(u)))
    # ③ 県も和集合
    po = [x for x in (o.get("prefecture") or "").split("・") if x]
    pn = [x for x in (e.get("prefecture") or "").split("・") if x]
    up = list(dict.fromkeys(po + pn))
    if len(up) > len(pn):
        e["prefecture"] = "・".join(up)
        ch.append("県 %d→%d" % (len(pn), len(up)))
    if ch:
        fixed.append((e["id"], e.get("name", "")[:32], " / ".join(ch)))

print("直す対象: %d件" % len(fixed))
for i, n, c in fixed:
    print("  id%-6d %-32s %s" % (i, n, c))
if "--apply" not in sys.argv:
    print("(--apply で書き込み)")
    sys.exit(0)
out = h[:m.start(2)] + json.dumps(events, ensure_ascii=False, indent=2).replace("\n", "\r\n") + h[m.end(2):]
io.open("index.html", "w", encoding="utf-8", newline="").write(out)
print("書き込み完了")
