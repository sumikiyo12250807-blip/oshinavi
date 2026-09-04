# -*- coding: utf-8 -*-
"""会場一覧（venue）の取りこぼしを直す。**venue だけ**更新して tickets には一切触らない。

枠は追加されているのに venue の文字列が古いままで、
「その県の公演があるのに会場名が画面に出ない」状態になっていた3件。

🚨tickets は絶対に置換しない（build は受付中と発売前しか取らないので、
   置き換えると終了済みの枠が消える＝[[feedback_build_pia_multiurl_loses_ticket_url]]の二次事故）。
🚨新しい venue が古いものを**包含している**時だけ更新する（会場が減る更新はしない）。

  python tmp/apply_venue_0904.py          # 下見
  python tmp/apply_venue_0904.py --apply  # 実行
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
built = json.load(io.open("tmp/venue_built_0904.json", encoding="utf-8"))


def halls(v):
    m2 = re.match(r"全国ツアー（(.+)）$", v or "")
    return set(x.strip() for x in m2.group(1).split("／")) if m2 else set()


n = 0
for b in built:
    e = by_id.get(b["id"])
    if not e:
        print("ABORT: id=%s が無い" % b["id"]); sys.exit(1)
    old, new = e.get("venue") or "", b.get("venue") or ""
    o, nw = halls(old), halls(new)
    lost = o - nw
    add = nw - o
    print("id=%s  会場 %d -> %d  （増える%d／消える%d）" % (b["id"], len(o), len(nw), len(add), len(lost)))
    if lost:
        print("   🚨消える会場があるので触らない: %s" % "／".join(sorted(lost)))
        continue
    if not add:
        print("   変化なし＝触らない")
        continue
    print("   ＋%s" % "／".join(sorted(add)))
    e["venue"] = new
    if b.get("prefecture"):
        e["prefecture"] = b["prefecture"]
    n += 1

print("UPDATED=%d" % n)
if not APPLY:
    print("(下見のみ。--apply で書き込み)"); sys.exit(0)
if n == 0:
    print("更新なし"); sys.exit(0)

shutil.copy(PATH, PATH + ".bak_0904_venue")
out = raw[:m.start(1)] + dump(events).replace("\n", "\r\n") + raw[m.end(1):]
io.open(PATH, "w", encoding="utf-8", newline="").write(out)
print("WROTE index.html")
