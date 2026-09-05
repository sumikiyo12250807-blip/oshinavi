# -*- coding: utf-8 -*-
"""【記事の取りこぼしチェック】現物 → 本文 の向きで照合する。

🚨 `verify_draft.py` は「本文に書いたことが現物にあるか」（本文→現物）しか見ない。
   **現物にあるのに本文に書いていない枠**＝取りこぼしは、その向きでは絶対に見つからない。
   2026-08-30 の事故がこれ（「6公演」と書いた横に7つ目の枠が登録済みだった）。

やること＝記事に出てくる各アーティストについて、
  ① 今週（FROM〜TO）に**発売が始まる枠**を現物から全部拾う
  ② その枠の券種名に入っている「（県 M/D公演）」を、本文の文字列と突き合わせる
  ③ 本文に出てこない枠を「🚨本文に無い」として並べる
あわせて、記事が「◯公演」「◯つ」「◯枠」と数を書いている箇所も拾って、実数と比べる。
"""
import json, re, io, datetime

FROM, TO = "2026-09-07", "2026-09-13"
MAIN = {"MONO NO AWARE": 4500, "ASKA": 4489, "東京スカパラダイスオーケストラ": 4236,
        "佐藤竹善": 668, "湖月わたる": 4246}
TILES = [6060, 6003, 950, 4228, 4235, 4227, 5993, 6009, 4103, 6141, 4230, 4490]

html = io.open("index.html", encoding="utf-8", newline="").read()
events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", html, re.S).group(1))
by_id = {e.get("id"): e for e in events}
draft = io.open("tmp/pickup0906/draft.md", encoding="utf-8").read()

RE_START = re.compile(r"(\d{1,2})/(\d{1,2})(?:\s*(\d{1,2}:\d{2}))?\s*発売\s*$")


def sale_start(t):
    """その枠の発売開始日（startDate があればそれ、無ければ券種名の「M/D発売」から）"""
    if t.get("startDate"):
        return t["startDate"]
    m = RE_START.search(t.get("type") or "")
    if m:
        y = 2026 if int(m.group(1)) >= 9 else 2027
        return "%04d-%02d-%02d" % (y, int(m.group(1)), int(m.group(2)))
    return None


def scope(ty):
    """券種名の「（…公演）」の中身＝県と公演日"""
    m = re.search(r"（([^（）]*公演[^（）]*)）", ty or "")
    return m.group(1) if m else ""


buf, miss_total = [], 0
for label, ids in (("主役", list(MAIN.items())), ("タイル", [(None, i) for i in TILES])):
    buf.append("=" * 64)
    buf.append("【%s】" % label)
    for name, i in ids:
        e = by_id.get(i)
        if not e:
            buf.append("  id=%s は現物に無い" % i)
            continue
        nm = name or e.get("artist") or e.get("name", "")
        week = []
        for t in e.get("tickets") or []:
            sd = sale_start(t)
            if sd and FROM <= sd <= TO:
                week.append(t)
        buf.append("")
        buf.append("■ id=%-5s %s   今週発売になる枠 %d本" % (i, nm[:36], len(week)))
        for t in week:
            sc = scope(t.get("type"))
            # 本文に出ているか＝「（…公演）」の中身がそのまま本文にあるか
            hit = bool(sc) and sc in draft
            if not hit and sc:
                # 県と日付が別々に書かれている形も許す
                mm = re.search(r"(\d{1,2})/(\d{1,2})", sc)
                if mm and ("%s/%s公演" % (mm.group(1), mm.group(2))) in draft:
                    hit = True
            mark = "  " if hit else "🚨"
            if not hit:
                miss_total += 1
            buf.append("   %s %s" % (mark, t.get("type")))
        if week and all(scope(t.get("type")) and scope(t.get("type")) in draft for t in week):
            buf.append("      → 全部そろっている")

buf.append("")
buf.append("=" * 64)
buf.append("本文に出てこない枠: %d本" % miss_total)
buf.append("")
buf.append("【記事に書いてある「数」】※実数と見比べる")
for m in re.finditer(r"(.{0,40}?)([0-9０-９一二三四五六七八九十]+)\s*(公演|つ|枠|都市|本)", draft):
    line = re.sub(r"\s+", " ", m.group(0)).strip()
    buf.append("   " + line)

io.open("tmp/article_coverage_0906.txt", "w", encoding="utf-8").write("\n".join(buf))
print("MISS=%d -> tmp/article_coverage_0906.txt" % miss_total)
