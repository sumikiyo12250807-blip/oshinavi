# -*- coding: utf-8 -*-
"""スキマスイッチ2本目の点検（字数・3点・CTA・「。」改行・1本目との言い回し重複）。"""
import io
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

new = io.open(r"C:\Users\user\oshinavi\tmp\x_post_0808_sukima2.txt", encoding="utf-8").read().strip()
old_all = io.open(r"C:\Users\user\oshinavi\tmp\x_posts_20260808.txt", encoding="utf-8").read()
old = [p.strip() for p in re.split(r"^=== .*? ===$", old_all, flags=re.M) if p.strip()][2]

print("字数: %d" % len(new))
print("冒頭ピックアップ : %s" % ("OK" if new.startswith('OSHINAVIの"本日発売"ピックアップ🎫') else "🚨"))
print("署名             : %s" % ("OK" if '推しの"発売日"見逃さない｜OSHINAVI' in new else "🚨"))
print("タグ             : %s" % " ".join(re.findall(r"#\S+", new)))
print("CTA固定文        : %s" % ("OK" if "▼チケット情報はこちら → https://oshinavi.jp" in new else "🚨"))
print("「。」のあとに続き: %s" % ("🚨あり" if re.search(r"。(?=[^\s])", new) else "OK（全部改行済み）"))
print("内輪語           : %s" % ("🚨カウントダウン" if "カウントダウン" in new else "OK"))

print("\n--- 1本目(6:29投稿済み)と同じ言い回しが無いか ---")
dup = []
for w in ["そろって解禁", "畳みかけ", "ずるいわ", "唇噛んだ", "指を構えて", "何回聴いても", "1週間のうちに"]:
    if w in new and w in old:
        dup.append(w)
print("  重複: %s" % (" / ".join(dup) if dup else "なし＝ちゃんと別の文章になっている"))
