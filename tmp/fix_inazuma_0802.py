# -*- coding: utf-8 -*-
"""id2428 宝塚月組の表記ゆれ修正：稲妻開花譚 → 稲妻開化譚（公式表記）。
index.html はバイナリで読み書きして改行(CRLF)に一切触らない。"""
import io
import os
import shutil
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

P = r"C:\Users\user\oshinavi\index.html"
BAK = r"C:\Users\user\oshinavi\index.html.bak_0802_inazuma"
OLD = "稲妻開花譚".encode("utf-8")
NEW = "稲妻開化譚".encode("utf-8")

b = open(P, "rb").read()

crlf_before = b.count(b"\r\n")
lf_before = b.count(b"\n")
stray_lf_before = lf_before - crlf_before
hits = b.count(OLD)

print("修正前: 一致 %d件 / CRLF %d / 単独LF %d / サイズ %d" % (hits, crlf_before, stray_lf_before, len(b)))

if hits == 0:
    print("対象なし。中止。")
    sys.exit(1)

if not os.path.exists(BAK):
    shutil.copyfile(P, BAK)
    print("バックアップ作成: %s" % BAK)
else:
    print("バックアップ既存: %s" % BAK)

nb = b.replace(OLD, NEW)

crlf_after = nb.count(b"\r\n")
lf_after = nb.count(b"\n")
stray_lf_after = lf_after - crlf_after

# 改行が1本も動いていないことを確認してから書く
assert crlf_after == crlf_before, "CRLF数が変化した"
assert stray_lf_after == stray_lf_before, "単独LF数が変化した"
assert len(nb) == len(b), "バイト長が変化した(同じ字数のはず)"
assert nb.count(OLD) == 0, "誤字が残っている"

open(P, "wb").write(nb)

print("修正後: 残存誤字 %d件 / 正表記 %d件 / CRLF %d / 単独LF %d" % (
    nb.count(OLD), nb.count(NEW), crlf_after, stray_lf_after))
print("改行は1本も変化なし。OK")
