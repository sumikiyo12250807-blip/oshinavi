# -*- coding: utf-8 -*-
"""9/3から持ち越した統合候補を、既存エントリへ「枠を足す」形で統合する。

🚨足す枠には必ず ticket.url を付ける（新側の links.pia を使う）。
   付けないと「url有り/無しの二重登録」を自分で作ることになる
   （[[feedback_build_pia_multiurl_loses_ticket_url]]／今朝それを片づけたばかり）。
🚨判断が要る2件（6450 N響／6432 HelloKitty）は既定では触らない。

  python tmp/do_merge_0904.py          # 下見
  python tmp/do_merge_0904.py --apply  # 実行
"""
import json, re, io, sys, shutil

PATH = "index.html"
APPLY = "--apply" in sys.argv

# 自走してよい9件（新側id, 既存id）
PAIRS = [(6407, 3551), (6413, 2121), (6417, 2239), (6418, 450),
         (6436, 4223), (6438, 309), (6444, 2471), (6456, 4291)]
# 6406 は足す枠0（既存に同じ枠がある）＝新側を捨てるだけ
DISCARD = [6406]
# 判断が要る＝触らない
HOLD = [6450, 6432]

raw = io.open(PATH, encoding="utf-8", newline="").read()
m = re.search(r"const EVENTS = (\[.*?\]);\r?\n", raw, re.S)
src_text = m.group(1)
events = json.loads(src_text)


def dump(evs):
    return json.dumps(evs, ensure_ascii=False, indent=2)


if dump(events) != src_text.replace("\r\n", "\n"):
    print("ABORT: 書式の往復チェックに落ちた")
    sys.exit(1)
print("OK format roundtrip")

by_id = {e.get("id"): e for e in events}
pend = {e.get("id"): e for e in json.load(io.open("tmp/_merge_pending_0903.json", encoding="utf-8"))}


def key(t):
    ty = re.sub(r"\d{1,2}/\d{1,2}", "#", t.get("type", ""))
    ty = re.sub(r"\d{1,2}:\d{2}", "#", ty)
    return (ty, t.get("date"))


added_total = 0
report = []
for new_id, old_id in PAIRS:
    ne, oe = pend.get(new_id), by_id.get(old_id)
    if not ne or not oe:
        print("ABORT: id=%s/%s が見つからない" % (new_id, old_id))
        sys.exit(1)
    pia = (ne.get("links") or {}).get("pia")
    if not pia:
        print("ABORT: id=%s に links.pia が無い（url無しでは足さない）" % new_id)
        sys.exit(1)
    oldkeys = set(key(t) for t in oe.get("tickets", []))
    for t in ne.get("tickets", []):
        if key(t) in oldkeys:
            continue
        nt = dict(t)
        nt["url"] = pia          # 🚨飛び先URLを必ず付ける
        oe.setdefault("tickets", []).append(nt)
        added_total += 1
        report.append((old_id, new_id, t.get("type"), t.get("date"), pia))

print("ADDED_SLOTS=%d over %d entries" % (added_total, len(PAIRS)))
for old_id, new_id, ty, dt, u in report:
    print("  old=%s <- new=%s  until=%s" % (old_id, new_id, dt))
print("DISCARD(枠0で捨てるだけ)=%s" % DISCARD)
print("HOLD(判断待ちで触らない)=%s" % HOLD)

# 統合先の枠に url が全部付いているか点検
for _, old_id in PAIRS:
    pass
for old_id in sorted(set(o for _, o in PAIRS)):
    ts = by_id[old_id].get("tickets", [])
    nourl = sum(1 for t in ts if not t.get("url"))
    print("  CHECK old=%s slots=%d url無=%d" % (old_id, len(ts), nourl))

if not APPLY:
    print("(下見のみ。--apply で書き込み)")
    sys.exit(0)

shutil.copy(PATH, PATH + ".bak_0904_merge")
out = raw[:m.start(1)] + dump(events).replace("\n", "\r\n") + raw[m.end(1):]
io.open(PATH, "w", encoding="utf-8", newline="").write(out)
print("WROTE index.html (backup: index.html.bak_0904_merge)")
