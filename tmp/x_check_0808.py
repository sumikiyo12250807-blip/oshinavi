# -*- coding: utf-8 -*-
"""明日8/8ぶんのX投稿3本を機械チェック（字数・3点チェック・言い回しの重複）。"""
import collections
import io
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

raw = io.open(r"C:\Users\user\oshinavi\tmp\x_posts_20260808.txt", encoding="utf-8").read()
posts = [p.strip() for p in re.split(r"^=== .*? ===$", raw, flags=re.M) if p.strip()]
names = re.findall(r"^=== (.*?) ===$", raw, flags=re.M)

for name, body in zip(names, posts):
    n = len(body)
    print("■ %s … %d字" % (name, n))
    print("   冒頭ピックアップ : %s" % ("OK" if body.startswith('OSHINAVIの"本日発売"ピックアップ🎫') else "🚨無い"))
    print("   署名             : %s" % ("OK" if '推しの"発売日"見逃さない｜OSHINAVI' in body else "🚨無い"))
    print("   ハッシュタグ     : %s" % ("OK " + " ".join(re.findall(r"#\S+", body)) if "#" in body else "🚨無い"))
    print("   CTA固定文        : %s" % ("OK" if "▼チケット情報はこちら → https://oshinavi.jp" in body else "🚨違う"))
    print("   URL              : %s" % ("素のoshinavi.jp OK" if "https://oshinavi.jp\n" in body + "\n" and "?x=" not in body else "🚨?x=が付いている"))
    print("   内輪語チェック   : %s" % ("🚨カウントダウン混入" if "カウントダウン" in body else "OK"))

# 3本の間で使い回している特徴語（手癖チェック）
words = ["浴び", "指を構え", "いっせい", "畳みかけ", "震え", "唇", "ずるい", "埋まって"]
print("\n--- 言い回しの重複チェック ---")
for w in words:
    c = sum(1 for b in posts if w in b)
    if c >= 2:
        print("  ⚠️ 「%s」が %d本で重複" % (w, c))
print("  （⚠️が出ていなければ散らせている）")
