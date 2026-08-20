# -*- coding: utf-8 -*-
"""8/8〜8/10ぶんのX投稿5本をまとめて機械チェック（字数・3点・CTA・言い回し重複）。"""
import io
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

FILES = [r"C:\Users\user\oshinavi\tmp\x_posts_20260808.txt",
         r"C:\Users\user\oshinavi\tmp\x_posts_20260809_10.txt"]
names, posts = [], []
for f in FILES:
    raw = io.open(f, encoding="utf-8").read()
    names += re.findall(r"^=== (.*?) ===$", raw, flags=re.M)
    posts += [p.strip() for p in re.split(r"^=== .*? ===$", raw, flags=re.M) if p.strip()]

ng = 0
for name, body in zip(names, posts):
    head_ok = body.startswith('OSHINAVIの"本日発売"ピックアップ🎫') or body.startswith('OSHINAVIの"明日発売"ピックアップ🎫')
    sign_ok = '推しの"発売日"見逃さない｜OSHINAVI' in body
    tag_ok = "#" in body
    cta_ok = "▼チケット情報はこちら → https://oshinavi.jp" in body
    url_ok = "?x=" not in body
    naiwa_ok = "カウントダウン" not in body
    bad = [k for k, v in [("冒頭", head_ok), ("署名", sign_ok), ("タグ", tag_ok),
                          ("CTA", cta_ok), ("素URL", url_ok), ("内輪語", naiwa_ok)] if not v]
    ng += len(bad)
    print("■ %s … %d字 %s" % (name[:34], len(body), "OK" if not bad else "🚨" + "/".join(bad)))

print("\n--- 5本の間で使い回している言い回し ---")
cnt = {}
for w in ["浴び", "指を構え", "いっせい", "いちどき", "そろって", "畳みかけ", "震え", "唇",
          "ずるい", "埋まって", "距離", "食らう", "動くわ", "動く", "最後の"]:
    c = sum(1 for b in posts if w in b)
    if c >= 2:
        cnt[w] = c
for w, c in cnt.items():
    print("  ⚠️ 「%s」が %d本" % (w, c))
if not cnt:
    print("  重複なし＝ちゃんと散らせている")
print("\n=== 3点チェックの不備 %d件 ===" % ng)
