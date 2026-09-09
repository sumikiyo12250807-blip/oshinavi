# -*- coding: utf-8 -*-
"""9/11・9/12の発売枠を、投稿の束ね方に合わせてジャンル別に数える。
   丸め方＝X_SCRIPT.md の決まり（18→「20件近く」／23→「20件以上」／10未満は実数）。"""
import io, re, json, collections, sys
sys.stdout.reconfigure(encoding='utf-8')

DAYS = ["2026-09-11", "2026-09-12"]
BUNDLE = {
    "クラシック(classic)": ["classic"],
    "お笑い(owarai)": ["owarai"],
    "JPOP＋演歌(jpop)": ["jpop", "enka"],
    "スポーツ(sports)": ["sports"],
    "伝統＋邦楽(dento)": ["dento", "hougaku"],
    "演劇＋キッズ(engeki)": ["engeki", "kids"],
    "トークショー＋学園祭＋舞台挨拶(talkshow)": ["talkshow", "gakusai", "aisatsu"],
}

h = io.open("index.html", encoding="utf-8", newline="").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", h, re.S).group(1))

cnt = {d: collections.Counter() for d in DAYS}
for e in EV:
    if e.get("genre") == "new":
        continue
    for t in e.get("tickets") or []:
        if t.get("startDate") in cnt and not t.get("soldout"):
            cnt[t["startDate"]][e.get("genre") or "?"] += 1


def marume(n):
    if n < 10:
        return "%d件" % n
    ten = round(n / 10.0) * 10
    if n <= ten:
        return "%d件近く" % ten
    return "%d件以上" % ten


print("%-40s %-22s %s" % ("束", "9/11", "9/12"))
for label, gs in BUNDLE.items():
    out = []
    for d in DAYS:
        tot = sum(cnt[d][g] for g in gs)
        out.append("全%d枠" % tot)
    print("%-40s %-22s %s" % (label, out[0], out[1]))

print("\n=== 5件を載せたあとの『他にも』の数（丸めた形） ===")
for label, gs in BUNDLE.items():
    for d in DAYS:
        tot = sum(cnt[d][g] for g in gs)
        for shown in (1, 2, 4, 5, 7, 10):
            pass
        print("  %-40s %s 全%2d枠  → 5件載せたら残り%2d＝「%s」"
              % (label, d[5:], tot, max(tot - 5, 0), marume(max(tot - 5, 0))))
