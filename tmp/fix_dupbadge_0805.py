# -*- coding: utf-8 -*-
"""新着プール点検で見つかった「同一エントリ内で表記が完全に同じ枠」を直す（2026-08-05）。

ぴあの実ページで正体を確認した結果:
  3710 コンサドーレ×大分  2626908=通常 ／ 2626913=車いす・シニア・手帳割引・U-23他 ／ 2629184=駐車券
  3711 コンサドーレ×栃木  2626742=通常 ／ 2626910=車いす・シニア・手帳割引・U-23他
  3676 福岡謎解き街歩き   各月2枠は【引換場所】違い（リアル脱出ゲーム福岡店 ／ SPACE on the Station）
                          ※ぴあHTMLの出現順は各月とも「リアル脱出ゲーム福岡店→SPACE on the Station」

画面で見分けがつかない枠を放置しない（[[feedback_same_day_show_time_badge]]と同じ趣旨・
過去にもTOMAKOMAI MIRAI FESTを【入場券】【駐車券】に分けた実績）。
index.html は newline='' で読み書きしCRLFを保つ。
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
BAK = os.path.join(ROOT, "index.html.bak_0805_dupbadge")

# url末尾のeventCd → 差し込むラベル
BY_URL = {
    "2626913": "【車いす・シニア・手帳割引・U-23他】",
    "2629184": "【駐車券】",
    "2626910": "【車いす・シニア・手帳割引・U-23他】",
}
PLACES = ["【リアル脱出ゲーム福岡店 引換】", "【SPACE on the Station 引換】"]

h = io.open(IDX, encoding="utf-8", newline="").read()
NL = "\r\n" if "\r\n" in h else "\n"
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))
changed = []

for e in EVENTS:
    if e["id"] in (3710, 3711):
        for t in e.get("tickets", []):
            cd = re.search(r"eventCd=(\d+)", t.get("url") or "")
            lab = BY_URL.get(cd.group(1)) if cd else None
            if lab and lab not in t["type"]:
                old = t["type"]
                t["type"] = t["type"].replace("一般発売", "一般発売" + lab, 1)
                changed.append((e["id"], old, t["type"]))
    if e["id"] == 3676:
        # 同じ表記のペアごとに、出現順でラベルを振る
        cnt = {}
        for t in e.get("tickets", []):
            base = re.sub(r"【(リアル脱出|SPACE).*?】", "", t["type"])
            i = cnt.get(base, 0)
            cnt[base] = i + 1
            if i < len(PLACES) and "引換】" not in t["type"]:
                old = t["type"]
                t["type"] = t["type"].replace("（福岡", PLACES[i] + "（福岡", 1)
                changed.append((e["id"], old, t["type"]))

if not changed:
    print("直すものが無い")
    sys.exit(0)

shutil.copyfile(IDX, BAK)
arr = json.dumps(EVENTS, ensure_ascii=False, indent=2).replace("\n", NL)
io.open(IDX, "w", encoding="utf-8", newline="").write(h[:m.start()] + m.group(1) + arr + m.group(3) + h[m.end():])
print("修正 %d枠（backup %s）\n" % (len(changed), os.path.basename(BAK)))
for eid, o, n in changed:
    print("id%-5d %s" % (eid, o))
    print("      → %s" % n)
