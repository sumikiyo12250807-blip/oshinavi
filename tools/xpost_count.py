# -*- coding: utf-8 -*-
"""X投稿の文字数と3点チェックを機械で確かめる（目分量で数えない）。

3点＝①冒頭のピックアップ行 ②末尾の署名 ③ハッシュタグ。手直しすると落ちやすい。
＋本文に https://oshinavi.jp が入っているか（2026-08-01のルール反転で全投稿必須）。
"""
import argparse
import os
import re


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    args = ap.parse_args()

    with open(args.path, encoding="utf-8-sig") as f:
        text = f.read().rstrip("\n")

    n = len(text)
    print("文字数: %d  （目標 250〜330）" % n)
    checks = [
        ("①冒頭ピックアップ", bool(re.match(r'OSHINAVIの"\d+日発売"ピックアップ🎫', text))),
        ("②末尾署名", '推しの"発売日"見逃さない｜OSHINAVI' in text),
        ("③ハッシュタグ", text.count("#") >= 1),
        ("④oshinavi.jp", "https://oshinavi.jp" in text),
        ("⑤パラメータ無し", "oshinavi.jp/?" not in text),
        ("⑥字数レンジ", 250 <= n <= 330),
    ]
    for name, ok in checks:
        print("%s %s" % ("OK " if ok else "NG ", name))
    print("判定:", "全部OK" if all(c[1] for c in checks) else "要直し")


main()
