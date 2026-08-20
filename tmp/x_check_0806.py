# -*- coding: utf-8 -*-
"""X投稿の機械チェック＝文字数・3点チェック（冒頭/署名/タグ）・本文URL・手癖語の重複。"""
import io, re, sys, collections

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

raw = open("tmp/x_posts_20260806.txt", encoding="utf-8").read()
blocks = re.split(r"^===== (.+?) =====$", raw, flags=re.M)[1:]
posts = list(zip(blocks[0::2], [b.strip() for b in blocks[1::2]]))

for name, body in posts:
    n = len(body)
    head = body.startswith('OSHINAVIの"7日発売"ピックアップ🎫')
    sign = '推しの"発売日"見逃さない｜OSHINAVI' in body
    tag = bool(re.search(r"#\S+", body))
    url = "https://oshinavi.jp" in body
    print("== %s ： %d字" % (name, n))
    print("   冒頭%s ／ 署名%s ／ タグ%s ／ 本文URL%s" % (
        "OK" if head else "🚨NG", "OK" if sign else "🚨NG",
        "OK" if tag else "🚨NG", "OK" if url else "🚨NG"))

# 手癖チェック（2回以上出る特徴語）
words = ["浴び", "刻む", "震え", "スタンバイ", "当たり日", "指を", "狙", "箱", "並ぶ", "持っていく"]
cnt = collections.Counter()
for _, body in posts:
    for w in words:
        if w in body:
            cnt[w] += 1
dup = {w: c for w, c in cnt.items() if c >= 2}
print("\n2本以上で使っている言い回し:", dup or "なし")
