# -*- coding: utf-8 -*-
"""Xに実際に貼られた本文（read_pageで読み取ったもの）を、手元の下書きと突き合わせる。

🚨区切って入力しているので、途中の1ブロックが落ちても気づけない。
   「下書きと素材が一致している」だけでは足りず、**Xの画面の実物**と照合する必要がある。

  python tmp/x0905/verify_onx.py 2   # post2 を照合
"""
import io, re, sys

n = sys.argv[1] if len(sys.argv) > 1 else "2"
draft = io.open("tmp/x0905/post%s.txt" % n, encoding="utf-8").read()
onx = io.open("tmp/x0905/onx_post%s.txt" % n, encoding="utf-8").read()

LINE = re.compile(r"^(\d{1,2}:\d{2}) (.+)$")


def rows(t):
    out = []
    for ln in t.split("\n"):
        m = LINE.match(ln.strip())
        if m:
            out.append(ln.strip())
    return out


d, x = rows(draft), rows(onx)
print("下書きのリスト行=%d  Xに入っている行=%d" % (len(d), len(x)))

ds, xs = set(d), set(x)
missing = [r for r in d if r not in xs]
extra = [r for r in x if r not in ds]

print("Xに入っていない（落ちた）=%d" % len(missing))
for r in missing:
    print("   - %s" % r)
print("Xにあるが下書きに無い（化けた/重複）=%d" % len(extra))
for r in extra:
    print("   + %s" % r)

# 重複の数も見る（同じ行が2回入っていないか）
from collections import Counter
dup = [r for r, c in Counter(x).items() if c > Counter(d).get(r, 0)]
print("Xで多く出ている行=%d" % len(dup))
for r in dup:
    print("   x%d %s" % (Counter(x)[r], r))

if not missing and not extra and not dup:
    print("\n✅完全一致：落ちも化けも重複もなし")
    sys.exit(0)
sys.exit(2)
