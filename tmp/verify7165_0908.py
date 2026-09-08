# -*- coding: utf-8 -*-
"""id7165 のぴあ生HTMLから公演日と販売状態を自分で数え直す（エージェントの結論は使わない）"""
import io, re, collections

h = io.open("tmp/pia0908/7165.html", encoding="utf-8", errors="replace").read()

# 日付らしき文字列を全部拾う
dates = re.findall(r"20\d{2}[/-]\d{1,2}[/-]\d{1,2}", h)
norm = []
for d in dates:
    y, m, dd = re.split(r"[/-]", d)
    norm.append("%04d-%02d-%02d" % (int(y), int(m), int(dd)))
cnt = collections.Counter(norm)

# 状態の文言
states = collections.Counter(re.findall(r"予定枚数終了|販売終了|受付終了|一般発売|発売前", h))

o = io.open("tmp/verify7165_0908.txt", "w", encoding="utf-8")
o.write("=== tmp/pia0908/7165.html を自分で数え直した ===\n\n")
o.write("HTMLの長さ: %d文字\n\n" % len(h))
o.write("--- 出てくる日付（10月・11月だけ・多い順）---\n")
for d, n in sorted(cnt.items()):
    if d.startswith("2026-10") or d.startswith("2026-11"):
        o.write("  %s  %d回\n" % (d, n))
o.write("\n--- 販売状態の文言の数 ---\n")
for s, n in states.most_common():
    o.write("  %s  %d回\n" % (s, n))

# 公演日らしい行（会場と日付が近くにある塊）を抜く
o.write("\n--- 「YYYY/M/D(曜)」形の並び（先頭40件）---\n")
for m in re.finditer(r"20\d{2}/\d{1,2}/\d{1,2}\([日月火水木金土]\)", h):
    o.write("  %s\n" % m.group(0))
o.close()
print("wrote tmp/verify7165_0908.txt")
