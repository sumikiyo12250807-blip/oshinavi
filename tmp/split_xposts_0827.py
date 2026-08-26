# -*- coding: utf-8 -*-
"""X投稿を1本ずつ別ファイルに割る。
Set-Clipboard で貼る運用（SendKeysで日本語を打つと化ける＝feedback_x_browser_operation）。"""
import io
import sys

sys.stdout.reconfigure(encoding="utf-8")

posts = io.open("tmp/xposts_0827.txt", encoding="utf-8").read().split("\n---\n")
for i, p in enumerate(posts, 1):
    p = p.strip("\n")
    path = "tmp/xp0827_%d.txt" % i
    io.open(path, "w", encoding="utf-8", newline="\n").write(p)
    print("%s  %d字  先頭: %s" % (path, len(p), p.split("\n")[0][:28]))
