# -*- coding: utf-8 -*-
"""今夜のX投稿に出す組を、ぴあで**アーティスト名から**総ざらいして取りこぼしを洗う。

🚨 ツアーの bundle ページだけ見ていると、そこに出てこない公演を落とす
   （feedback_pia_bundle_hides_shows）。だから名前で引いて、登録済みの eventCd と突き合わせる。
🚨 叩きすぎると 429 でゲートが静かに壊れるので、1件ごとに間を置く（reference_pia_rate_limit_429）。

出力: tmp/kwsweep_0907.txt（未登録だけ）
"""
import subprocess, sys, io, re, json, time, os

# (検索語, このアーティストの登録id) ＝ x_pick_0907.txt から取った実物
TARGETS = [
    ("ゆきの&よしまさ", 5518),
    ("立川志の輔", 4839),
    ("三三・左龍の会", 6109),
    ("三遊亭遊雀", 6111),
    ("柳家喬太郎", 1772),
    ("喜楽館", 3997),
    ("東京バレエ団", 3905),
    ("ウィーン・ヨハン・シュトラウス管弦楽団", 4719),
    ("小林紀子バレエ・シアター", 5685),
    ("INAMORIミュージック・デイ", 3998),
    ("真夜中の音楽室", 6452),
    ("横浜国立大学管弦楽団", 7159),
    ("ラッパ屋", 5628),
    ("バーテックスフォース", 4984),
    ("メイドインアビス", 4992),
    ("石川文洋", 6431),
    ("麻木久仁子", 7089),
    ("花火甲子園", 7095),
]

h = io.open("index.html", encoding="utf-8", newline="").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", h, re.S).group(1))
have = set()
for e in EV:
    for u in [(e.get("links") or {}).get("pia")] + [t.get("url") for t in e.get("tickets", [])]:
        if u:
            for m in re.finditer(r"event(?:Bundle)?Cd=([a-zA-Z0-9]+)", u):
                have.add(m.group(1))

out = io.open("tmp/kwsweep_0907.txt", "w", encoding="utf-8")
out.write("=== X投稿に出す組の総ざらい（ぴあをアーティスト名で引く）===\n\n")
total_miss = 0

for kw, eid in TARGETS:
    r = subprocess.run([sys.executable, "tools/pia_kw_search.py", kw],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        out.write("■ %s … 🚨検索に失敗（%s）\n\n" % (kw, (r.stderr or "")[-120:]))
        out.flush()
        time.sleep(6)
        continue
    src = io.open("tmp/pia_kw_search.txt", encoding="utf-8").read()
    blocks = re.split(r"\n(?=\[)", src)
    hits, miss = 0, []
    for b in blocks:
        m = re.search(r"URL   : (\S+)", b)
        if not m:
            continue
        cd = re.search(r"event(?:Bundle)?Cd=([a-zA-Z0-9]+)", m.group(1))
        if not cd:
            continue
        hits += 1
        if cd.group(1) not in have:
            name = b.split("\n")[0].strip()
            date = (re.search(r"公演日: (.*)", b) or [None, "-"])[1].strip()
            ven = (re.search(r"会場  : (.*)", b) or [None, "-"])[1].strip()
            miss.append((cd.group(1), name[:56], date[:38], ven[:44], m.group(1)))
    out.write("■ %s（登録id=%s）… ヒット%d / 未登録%d\n" % (kw, eid, hits, len(miss)))
    for cd, name, date, ven, url in miss:
        out.write("   🚨 %s\n      %s\n      %s ／ %s\n      %s\n" % (cd, name, date, ven, url))
    out.write("\n")
    out.flush()
    total_miss += len(miss)
    time.sleep(6)

out.write("=== 未登録の合計 %d件 ===\n" % total_miss)
out.close()
print("done / 未登録合計 %d" % total_miss)
