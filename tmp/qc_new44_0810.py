# -*- coding: utf-8 -*-
"""2026-08-10 新着44件(id3927-3973)の投入後チェック。
reconcile_pia（登録⇄ぴあ実ページ）は別途OK済み。ここは reconcile が気づけない型を潰す
（[[feedback_zero_error_pipeline]] / [[feedback_newpool_fullwidth_halfwidth]]）：
 ①全角ラテン/数字の残り ②同一バッジ文字列の重複（席種落ち） ③cap逆転（販売終了日>公演日）
 ④県名欠落・会場に県名が入る罠 ⑤R9年表記（2027公演）⑥_genre下書きの妥当性
 ⑦発売前なのに saleUntilSoldOut ⑧バッジ公演日の形（M/D完全形）⑨ticket.url の要否
"""
import json
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

src = open("index.html", "rb").read().decode("utf-8")
EVENTS = json.loads(re.search(r"  const EVENTS = (\[.*?\]);", src, re.S).group(1))
new = [e for e in EVENTS if 3927 <= e["id"] <= 3973]
print("対象 %d件" % len(new))

FW = re.compile(r"[Ａ-Ｚａ-ｚ０-９]")
GENRE_KW = {
    "owarai": ["落語", "寄席", "二人会", "独演会", "漫才", "ものまね", "お笑い", "喜劇"],
    "dento": ["狂言", "能", "文楽", "歌舞伎", "日本舞踊", "舞踊", "邦楽"],
    "classic": ["交響", "管弦", "オーケストラ", "フィル", "リサイタル", "バレエ", "オペラ", "室内楽", "合唱"],
    "musical": ["ミュージカル"],
}
ng = 0


def warn(e, msg):
    global ng
    ng += 1
    print("  ⚠️ id=%d %s … %s" % (e["id"], (e.get("name") or "")[:30], msg))


print("\n--- ①全角ラテン/数字の残り ---")
for e in new:
    for k in ("artist", "name", "venue", "dateLabel"):
        if FW.search(e.get(k) or ""):
            warn(e, "%s に全角: %s" % (k, e[k][:40]))
    for t in e["tickets"]:
        if FW.search(t.get("type") or ""):
            warn(e, "ticket.type に全角: %s" % t["type"][:40])

print("\n--- ②同じバッジ文字列が2枚以上（席種落ちの疑い） ---")
for e in new:
    seen = {}
    for t in e["tickets"]:
        seen[t["type"]] = seen.get(t["type"], 0) + 1
    for k, v in seen.items():
        if v > 1:
            warn(e, "同一バッジ%d枚: %s" % (v, k[:40]))

print("\n--- ③cap逆転（販売終了日が公演日より後） ---")
for e in new:
    for t in e["tickets"]:
        if t["date"] > e["date"]:
            warn(e, "締切%s > 公演日%s : %s" % (t["date"], e["date"], t["type"][:30]))

print("\n--- ④県名・会場 ---")
PREFS = "北海道|青森|岩手|宮城|秋田|山形|福島|茨城|栃木|群馬|埼玉|千葉|東京|神奈川|新潟|富山|石川|福井|山梨|長野|岐阜|静岡|愛知|三重|滋賀|京都|大阪|兵庫|奈良|和歌山|鳥取|島根|岡山|広島|山口|徳島|香川|愛媛|高知|福岡|佐賀|長崎|熊本|大分|宮崎|鹿児島|沖縄|全国"
for e in new:
    if not re.match(r"^(%s)" % PREFS, e.get("prefecture") or ""):
        warn(e, "prefecture が変: %r" % e.get("prefecture"))
    if not (e.get("venue") or "").strip():
        warn(e, "venue が空")

print("\n--- ⑤2027年公演のR9年表記 ---")
for e in new:
    if e["date"] >= "2027-01-01":
        for t in e["tickets"]:
            if re.search(r"\d+/\d+", t["type"]) and "R9年" not in t["type"]:
                warn(e, "2027公演なのにR9年表記なし: %s" % t["type"][:44])

print("\n--- ⑥_genre下書きの妥当性 ---")
for e in new:
    g = e.get("_genre") or ""
    txt = (e.get("name") or "") + (e.get("artist") or "")
    for gen, kws in GENRE_KW.items():
        if any(k in txt for k in kws) and g != gen:
            warn(e, "_genre=%s だが「%s」を含む→%s では？" % (g, [k for k in kws if k in txt][0], gen))
            break
    if not g or g == "その他":
        warn(e, "_genre 未確定(%r) ＝人の判断が要る" % g)

print("\n--- ⑦発売前(startDate==date)にsaleUntilSoldOut ---")
for e in new:
    for t in e["tickets"]:
        if t.get("saleUntilSoldOut") and t.get("startDate") == t.get("date"):
            warn(e, "発売前枠にsaleUntilSoldOut: %s" % t["type"][:30])

print("\n--- ⑧バッジの公演日が完全M/D形か ---")
for e in new:
    for t in e["tickets"]:
        m = re.search(r"（([^（）]*?)公演）", t["type"])
        if not m:
            warn(e, "バッジに（…公演）が無い: %s" % t["type"][:44])
            continue
        inner = m.group(1)
        if not re.search(r"\d+/\d+", inner):
            warn(e, "バッジ公演日が不完全: %s" % t["type"][:44])

print("\n--- ⑨複数URLのエントリでticket.urlが付いているか ---")
for e in new:
    urls = {t.get("url") for t in e["tickets"] if t.get("url")}
    if len(e["tickets"]) > 1 and not urls and "eventBundleCd" not in (e["links"].get("pia") or ""):
        codes = set(re.findall(r"eventCd=(\d+)", json.dumps(e, ensure_ascii=False)))
        if len(codes) > 1:
            warn(e, "会場別URLが複数あるのにticket.urlが無い")

print("\n=== 引っかかり %d件 ===" % ng)
