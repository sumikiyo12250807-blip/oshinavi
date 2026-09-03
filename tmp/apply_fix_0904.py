# -*- coding: utf-8 -*-
"""照合で出た取りこぼし 6410 / 6412 の tickets を、ぴあから取り直した内容へ差し替える。

安全弁＝差し替えで「締切が今日以降＝まだ買える枠」が減るなら適用しない
（[[reference_pia_rate_limit_429]] の heal --apply と同じ考え方）。

  python tmp/apply_fix_0904.py          # 下見
  python tmp/apply_fix_0904.py --apply  # 実行
"""
import json, re, io, sys, shutil

PATH = "index.html"
TODAY = "2026-09-04"
APPLY = "--apply" in sys.argv

raw = io.open(PATH, encoding="utf-8", newline="").read()
m = re.search(r"const EVENTS = (\[.*?\]);\r?\n", raw, re.S)
src_text = m.group(1)
events = json.loads(src_text)


def dump(evs):
    return json.dumps(evs, ensure_ascii=False, indent=2)


if dump(events) != src_text.replace("\r\n", "\n"):
    print("ABORT: 書式の往復チェックに落ちた"); sys.exit(1)

by_id = {e.get("id"): e for e in events}
built = {b["id"]: b for b in json.load(io.open("tmp/fix_built_0904.json", encoding="utf-8"))}


def alive(ts):
    """まだ買える枠＝締切が今日以降、または soldout/売り切れまで販売"""
    n = 0
    for t in ts:
        if t.get("soldout") or t.get("saleUntilSoldOut"):
            n += 1
        elif (t.get("date") or "") >= TODAY:
            n += 1
    return n


ok = True
for i, b in built.items():
    e = by_id.get(i)
    if not e:
        print("ABORT: id=%s が無い" % i); sys.exit(1)
    a0, a1 = alive(e.get("tickets", [])), alive(b.get("tickets", []))
    print("id=%s  枠 %d -> %d  / 生きた枠 %d -> %d  %s" % (
        i, len(e.get("tickets", [])), len(b.get("tickets", [])), a0, a1,
        "OK" if a1 >= a0 else "🚨生きた枠が減る＝適用しない"))
    if a1 < a0:
        ok = False

if not ok:
    print("ABORT: 生きた枠が減るので適用しない"); sys.exit(1)
if not APPLY:
    print("(下見のみ。--apply で書き込み)"); sys.exit(0)

for i, b in built.items():
    by_id[i]["tickets"] = b["tickets"]

shutil.copy(PATH, PATH + ".bak_0904_fix")
out = raw[:m.start(1)] + dump(events).replace("\n", "\r\n") + raw[m.end(1):]
io.open(PATH, "w", encoding="utf-8", newline="").write(out)
print("WROTE index.html (backup: index.html.bak_0904_fix)")
