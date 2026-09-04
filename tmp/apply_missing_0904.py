# -*- coding: utf-8 -*-
"""保留していた 6401 藤原大祐 / 6402 fripSide に、大阪公演の枠を足す。

🚨tickets は「追加と補完」だけ。置換しない（[[feedback_build_pia_multiurl_loses_ticket_url]]
  ＝置換で id72 劇団四季の生きた6枠を落とした前例がある）。
  ①既存の枠で url が空なら build 側の url を補完
  ②build にしか無い枠を足す
  ③dateLabel / venue / prefecture / links.pia は build の値に更新（会場が増えたため）
  ④date は「既存と build の遅いほう」

  python tmp/apply_held_0904.py          # 下見
  python tmp/apply_held_0904.py --apply  # 実行
"""
import json, re, io, sys, shutil

PATH = "index.html"
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
built = json.load(io.open("tmp/missing_ok_0904.json", encoding="utf-8"))


def key(t):
    return (t.get("type"), t.get("date"))


added = filled = 0
for b in built:
    e = by_id.get(b["id"])
    if not e:
        print("ABORT: id=%s が無い" % b["id"]); sys.exit(1)
    before = len(e.get("tickets", []))
    idx = {key(t): t for t in e.get("tickets", [])}
    for t in b.get("tickets", []):
        k = key(t)
        if k in idx:
            if t.get("url") and not idx[k].get("url"):
                idx[k]["url"] = t["url"]; filled += 1
        else:
            e.setdefault("tickets", []).append(dict(t)); added += 1
    # 見出し・会場は build の値へ（会場が増えたので古いままだと実態と合わない）
    for f in ("dateLabel", "venue", "prefecture"):
        if b.get(f):
            e[f] = b[f]
    if b.get("date") and b["date"] > (e.get("date") or ""):
        e["date"] = b["date"]
    if (b.get("links") or {}).get("pia"):
        e.setdefault("links", {})["pia"] = b["links"]["pia"]
    print("id=%s 枠 %d -> %d  date=%s" % (b["id"], before, len(e.get("tickets", [])), e.get("date")))

print("ADDED=%d  URL_FILLED=%d" % (added, filled))

if not APPLY:
    print("(下見のみ。--apply で書き込み)"); sys.exit(0)

shutil.copy(PATH, PATH + ".bak_0904_held")
out = raw[:m.start(1)] + dump(events).replace("\n", "\r\n") + raw[m.end(1):]
io.open(PATH, "w", encoding="utf-8", newline="").write(out)
print("WROTE index.html")
