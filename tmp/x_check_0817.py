# -*- coding: utf-8 -*-
"""X投稿ドラフトの機械検品。
①字数(改行込み) ②「。」直後に文字が続かない ③冒頭ピックアップ行 ④CTA ⑤署名 ⑥ハッシュタグ
⑦5本横串で2回以上出る特徴語（手癖チェック）"""
import re, sys, unicodedata
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')

raw = open('tmp/x_posts_0817.txt', encoding='utf-8').read()
blocks = re.split(r'^===(.+?)===$', raw, flags=re.M)[1:]
posts = [(blocks[i].strip(), blocks[i + 1].strip()) for i in range(0, len(blocks), 2)]

HEAD = 'OSHINAVIの"明日発売"ピックアップ🎫'
CTA = '▼チケット情報はこちら → https://oshinavi.jp'
SIGN = '推しの"発売日"見逃さない｜OSHINAVI'

ng = 0
for name, body in posts:
    n = len(body)
    kuten = re.findall(r'。(?=[^\s])', body)
    tags = re.findall(r'#\S+', body)
    checks = [
        ("字数250-330", 250 <= n <= 330, n),
        ("句点の直後に文字なし", not kuten, len(kuten)),
        ("冒頭ピックアップ", body.startswith(HEAD), body.split('\n')[0][:24]),
        ("CTA", CTA in body, CTA in body),
        ("署名", SIGN in body, SIGN in body),
        ("タグ2つ以上", len(tags) >= 2, tags),
        ("URLはoshinavi.jpのみ", not re.search(r'https?://(?!oshinavi\.jp)', body), True),
    ]
    bad = [c for c in checks if not c[1]]
    print("【%s】字数%d %s" % (name, n, "OK" if not bad else "🚨NG"))
    for c in checks:
        if not c[1]:
            print("    🚨 %s ← %s" % (c[0], c[2]))
            ng += 1

# 横串＝2回以上出る語（2文字以上の漢字/カタカナ列）
words = []
for _, body in posts:
    core = body.replace(HEAD, '').replace(CTA, '').replace(SIGN, '')
    core = re.sub(r'#\S+', '', core)
    words.append(set(re.findall(r'[一-龥ァ-ヶー]{2,}', core)))
c = Counter()
for w in words:
    c.update(w)
dup = [(k, v) for k, v in c.items() if v >= 3]
print()
print("3本以上に出る語（手癖の疑い）:", sorted(dup, key=lambda x: -x[1])[:12] or "なし")
print()
print("=== NG合計 %d ===" % ng)
