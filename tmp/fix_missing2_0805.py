# -*- coding: utf-8 -*-
"""新着プールの再照合で出た取りこぼし2件を足す（2026-08-05夕）。

投入後にぴあが先行を足した分＝[[feedback_deadline_extended_after_register]]の実例。
  3738 小山田壮平        プレリザーブ[東北]  8/7 11:00 〜 8/12 11:00（宮城・秋田・福島 9/12〜10/25公演）
  3760 爆笑!お笑いエンタメライブ in 岐阜  プレリザーブ  8/8 11:00 〜 8/16 23:59（岐阜 11/29公演）
どちらも発売前なので startDate=発売日 / date=締切（[[feedback_ticket_date]]）。
"""
import io
import json
import os
import re
import shutil
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = r"C:\Users\user\oshinavi"
IDX = os.path.join(ROOT, "index.html")
BAK = os.path.join(ROOT, "index.html.bak_0805_missing2")

ADD = {
    3738: {"type": "プレリザーブ【東北】（宮城・秋田・福島 9/12〜10/25公演）8/7 11:00発売",
           "date": "2026-08-12", "startDate": "2026-08-07"},
    3760: {"type": "プレリザーブ（岐阜 11/29公演）8/8 11:00発売",
           "date": "2026-08-16", "startDate": "2026-08-08"},
}

h = io.open(IDX, encoding="utf-8", newline="").read()
NL = "\r\n" if "\r\n" in h else "\n"
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))

done = []
for e in EVENTS:
    if e["id"] in ADD:
        t = ADD[e["id"]]
        if any(x.get("type") == t["type"] for x in e["tickets"]):
            continue
        e["tickets"].insert(0, dict(t))       # 先行なので先頭へ
        done.append((e["id"], (e.get("artist") or "")[:36], t["type"]))

assert len(done) == len(ADD), "足せなかった: %s" % ADD.keys()
shutil.copyfile(IDX, BAK)
arr = json.dumps(EVENTS, ensure_ascii=False, indent=2).replace("\n", NL)
io.open(IDX, "w", encoding="utf-8", newline="").write(h[:m.start()] + m.group(1) + arr + m.group(3) + h[m.end():])
for eid, art, ty in done:
    print("id%-5d %-36s ＋ %s" % (eid, art, ty))
print("\n✅ %d枠を追加（backup %s）" % (len(done), os.path.basename(BAK)))
