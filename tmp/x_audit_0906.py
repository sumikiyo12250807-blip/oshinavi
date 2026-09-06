# -*- coding: utf-8 -*-
"""今夜のX投稿に名前を出す組を、ぴあのキーワード検索で総ざらいして取りこぼしを炙り出す。
🚨ツアーまとめページ(bundle)だけ見ない＝そこに出てこない公演がある（feedback_pia_bundle_hides_shows）。
ぴあを叩きすぎると429でゲートが静かに壊れるので、キーワード間に5秒空ける。
"""
import json
import re
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")

NAMES = ["wacci", "古内東子", "esq", "山本彩", "WILD BLUE", "chilldspot",
         "log you", "CHAPTERHOUSE", "LiLi", "めろめろぱんち"]

h = open("index.html", encoding="utf-8").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))

# 登録済みの eventCd / eventBundleCd を全部集める（links.pia も ticket.url も見る）
known = set()
blob = json.dumps(EVENTS, ensure_ascii=False)
for mm in re.finditer(r"event(?:Bundle)?Cd=([A-Za-z0-9]+)", blob):
    known.add(mm.group(1))
print("登録済みのぴあコード %d本" % len(known))

out = open("tmp/x_audit_0906.txt", "w", encoding="utf-8")
for n in NAMES:
    path = "tmp/kw_%s.txt" % re.sub(r"[^A-Za-z0-9]", "_", n)
    r = subprocess.run([sys.executable, "tools/pia_kw_search.py", n, "--out", path],
                       capture_output=True)
    try:
        body = open(path, encoding="utf-8").read()
    except OSError:
        out.write("\n=== %s : 取得できなかった ===\n" % n)
        continue
    codes = set(re.findall(r"event(?:Bundle)?Cd=([A-Za-z0-9]+)", body))
    missing = sorted(codes - known)
    out.write("\n=== %s : ぴあのヒット %d本 / 未登録 %d本 ===\n" % (n, len(codes), len(missing)))
    for c in missing:
        # そのコードの行を拾って中身を見せる
        for line in body.splitlines():
            if c in line:
                out.write("   %s\n" % line.strip())
                break
    time.sleep(5)
out.close()
print("→ tmp/x_audit_0906.txt")
