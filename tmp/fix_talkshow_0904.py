# -*- coding: utf-8 -*-
"""_piaSub と genre が食い違う6件を、ぴあのカテゴリどおり talkshow に直す。
（[[feedback_genre_pia_asis_and_other]]＝ジャンルはぴあの言うとおりに機械で写す。
  2026-09-03に「トークショー」を新設した時の移動漏れ）

  python tmp/fix_talkshow_0904.py          # 下見
  python tmp/fix_talkshow_0904.py --apply  # 実行
"""
import json, re, io, sys, shutil

PATH = "index.html"
IDS = [3311, 3314, 3436, 3454, 3655, 3715]
TO = "talkshow"
APPLY = "--apply" in sys.argv

raw = io.open(PATH, encoding="utf-8", newline="").read()
m = re.search(r"const EVENTS = (\[.*?\]);\r?\n", raw, re.S)
src_text = m.group(1)
events = json.loads(src_text)


def dump(evs):
    return json.dumps(evs, ensure_ascii=False, indent=2)


if dump(events) != src_text.replace("\r\n", "\n"):
    print("ABORT: 書式の往復チェックに落ちた"); sys.exit(1)

n = 0
for e in events:
    if e.get("id") in IDS:
        print("id=%s  %s -> %s   piaSub=%s" % (e.get("id"), e.get("genre"), TO, e.get("_piaSub")))
        if e.get("genre") == TO:
            print("   （すでに %s。触らない）" % TO); continue
        e["genre"] = TO
        n += 1
print("CHANGED=%d" % n)

if not APPLY:
    print("(下見のみ。--apply で書き込み)"); sys.exit(0)

shutil.copy(PATH, PATH + ".bak_0904_talkshow")
out = raw[:m.start(1)] + dump(events).replace("\n", "\r\n") + raw[m.end(1):]
io.open(PATH, "w", encoding="utf-8", newline="").write(out)
print("WROTE index.html")
