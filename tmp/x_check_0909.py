# -*- coding: utf-8 -*-
"""X投稿の下書きを機械で検品する（X_SCRIPT.md の決まりに照らす）。
   🚨字数の上限判定は入れない（上限は無い）。"""
import io, re, sys, datetime

sys.stdout.reconfigure(encoding="utf-8")
src = io.open("tmp/x_drafts_0909.md", encoding="utf-8").read()
posts = re.findall(r"```(?:text)?\n(.*?)\n```", src, re.S)

BAN = ["あんた", "生で浴びる", "押さえる", "https://oshinavi", "?x="]
WD = "月火水木金土日"
o = io.open("tmp/x_check_0909.md", "w", encoding="utf-8")
o.write("# X投稿の機械検品（%d本）\n\n" % len(posts))
o.write("| # | 見出し | タグ | CTA | URL形 | 「。」改行 | 禁止語 | 曜日 | 実数件数 | 字数 |\n")
o.write("|---|---|---|---|---|---|---|---|---|---|\n")

ng_total = 0
for i, p in enumerate(posts, 1):
    head = "OK" if p.lstrip().startswith('OSHINAVIの"9/9チケット発売"ピックアップ🎫') else "🚨NG"
    tag = "OK" if ("#OSHINAVI" in p and "#明日発売" in p and "#チケット" in p) else "🚨NG"
    cta = "OK" if "▼チケット情報はこちら" in p else "🚨NG"

    urls = re.findall(r"oshinavi\.jp[^\s\n]*", p)
    url_ok = bool(urls) and all(u.startswith("oshinavi.jp") for u in urls)
    urlkind = ("?q=" if any("?q=" in u for u in urls) else
               ("?genre=" if any("?genre=" in u for u in urls) else "素"))
    url = ("OK(%s)" % urlkind) if url_ok else "🚨NG"

    # 「。」の直後は改行（例外＝モーニング娘。）
    bad_kuten = []
    for m in re.finditer(r"。(?!\n)(.)", p):
        before = p[max(0, m.start() - 8):m.start() + 1]
        if before.endswith("モーニング娘。"):
            continue
        bad_kuten.append(before[-6:] + "|" + m.group(1))
    kuten = "OK" if not bad_kuten else "🚨%d" % len(bad_kuten)

    ban = [w for w in BAN if w in p]
    banr = "OK" if not ban else "🚨" + "/".join(ban)

    # 曜日を実カレンダーと照合
    wd_ng = []
    for m in re.finditer(r"(\d{1,2})/(\d{1,2})\((.)\)", p):
        mo, d, w = int(m.group(1)), int(m.group(2)), m.group(3)
        y = 2026 if mo >= 9 else 2027
        try:
            real = WD[datetime.date(y, mo, d).weekday()]
        except Exception:
            continue
        if real != w:
            wd_ng.append("%d/%d(%s)→%s" % (mo, d, w, real))
    wd = "OK" if not wd_ng else "🚨" + ",".join(wd_ng[:2])

    cnt = re.findall(r"(?<![\d/])\d{1,3}\s*件", p)
    cntr = "OK" if not cnt else "🚨" + ",".join(cnt[:2])

    row_ng = any(x.startswith("🚨") for x in (head, tag, cta, url, kuten, banr, wd, cntr))
    ng_total += 1 if row_ng else 0
    o.write("| %d | %s | %s | %s | %s | %s | %s | %s | %s | %d |\n"
            % (i, head, tag, cta, url, kuten, banr, wd, cntr, len(p)))

    if bad_kuten:
        o.write("\n**#%d の「。」改行もれ**: %s\n\n" % (i, " / ".join(bad_kuten[:5])))
    if wd_ng:
        o.write("\n**#%d の曜日ちがい**: %s\n\n" % (i, ", ".join(wd_ng)))

o.write("\n## まとめ\n\n- 投稿 %d本 / 引っかかった本 **%d本**\n" % (len(posts), ng_total))
o.close()
print("posts=%d ng=%d -> tmp/x_check_0909.md" % (len(posts), ng_total))
