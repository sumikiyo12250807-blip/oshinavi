# -*- coding: utf-8 -*-
"""削除候補15件の独立再検証（2026-09-08）"""
import json, re, io, os

TODAY = "2026-09-08"
TARGET = [16, 271, 858, 1833, 2430, 2773, 3936, 5698, 5712, 6177, 6183, 6184, 6234, 6265, 6545]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "index.html")
OUT = os.path.join(ROOT, "tmp", "verify_del_0908.txt")

with io.open(SRC, encoding="utf-8") as f:
    html = f.read()

start = html.index("const EVENTS = [")
bstart = html.index("[", start)
# ブラケットの対応を数えて配列末尾を探す（文字列内は無視）
i = bstart
depth = 0
in_str = False
quote = ""
esc = False
while i < len(html):
    c = html[i]
    if in_str:
        if esc:
            esc = False
        elif c == "\\":
            esc = True
        elif c == quote:
            in_str = False
    else:
        if c in "\"'":
            in_str = True
            quote = c
        elif c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                break
    i += 1
arr_text = html[bstart:i+1]
events = json.loads(arr_text)

by_id = {}
for e in events:
    by_id.setdefault(e.get("id"), []).append(e)


def visible(t, today=TODAY):
    if t.get("saleUntilSoldOut") or t.get("soldout"):
        return True
    sd, d = t.get("startDate"), t.get("date")
    if d is None:
        return True  # 販売終了日が無い＝消えない扱い（判断不能マーク用）
    return not ((not sd or sd <= today) and d < today)


STREAM_KW = ["配信", "視聴", "オンライン", "アーカイブ", "ライブビューイング", "ライビュ"]


def domain(u):
    if not u:
        return "(url無し)"
    m = re.match(r"https?://([^/]+)", u)
    return m.group(1) if m else u[:40]


lines = []
summary = []
for tid in TARGET:
    ents = by_id.get(tid)
    lines.append("=" * 78)
    if not ents:
        lines.append("id=%s : ★index.html に存在しない（既に削除済みか元から無い）" % tid)
        summary.append((tid, "(データ無し)", "-", 0, "❓判断不能"))
        continue
    if len(ents) > 1:
        lines.append("id=%s : ★同じidのエントリが %d 件ある" % (tid, len(ents)))
    for e in ents:
        name = "%s / %s" % (e.get("artist", ""), e.get("title", ""))
        ed = e.get("date")
        past = "過去" if (ed and ed < TODAY) else ("本日" if ed == TODAY else "未来")
        lines.append("id=%s  %s" % (tid, name))
        lines.append("  会場: %s" % e.get("venue"))
        lines.append("  公演日 date=%s  → 今日(%s)基準: %s" % (ed, TODAY, past))
        lines.append("  genre=%s  verified=%s" % (e.get("genre"), e.get("verified")))
        tks = e.get("tickets") or []
        lines.append("  tickets 件数: %d" % len(tks))
        vis = 0
        stream_hits = []
        doms = {}
        for n, t in enumerate(tks, 1):
            v = visible(t)
            if v:
                vis += 1
            ttype = t.get("type", "")
            for kw in STREAM_KW:
                if kw in str(ttype) or kw in str(t.get("note", "")) or kw in str(t.get("dateLabel", "")):
                    stream_hits.append("#%d %s (%s)" % (n, ttype, kw))
                    break
            d = domain(t.get("url"))
            doms[d] = doms.get(d, 0) + 1
            lines.append("    #%d type=%r" % (n, ttype))
            lines.append("        startDate=%s  date(販売終了)=%s  soldout=%s  saleUntilSoldOut=%s"
                         % (t.get("startDate"), t.get("date"), t.get("soldout"), t.get("saleUntilSoldOut")))
            lines.append("        dateLabel=%r" % t.get("dateLabel"))
            lines.append("        url=%s" % (t.get("url") or "(無し)"))
            lines.append("        → 今日表示される? %s" % ("はい(visible=True)" if v else "いいえ(visible=False)"))
        lines.append("  ---- 表示される枠: %d / %d" % (vis, len(tks)))
        lines.append("  ---- 配信系券種: %s" % (", ".join(stream_hits) if stream_hits else "なし"))
        lines.append("  ---- URLドメイン内訳: %s" % ", ".join("%s x%d" % (k, v2) for k, v2 in sorted(doms.items())))
        # 判定
        if ed is None:
            verdict = "❓判断不能（公演日dateがデータに無い）"
        elif stream_hits:
            verdict = "⚠️保留（配信系券種あり）"
        elif vis > 0:
            verdict = "⚠️保留（表示される枠が %d 件ある）" % vis
        elif ed >= TODAY:
            verdict = "⚠️保留（公演日が今日以降）"
        else:
            verdict = "✅削除OK"
        lines.append("  ==== 判定: %s" % verdict)
        summary.append((tid, name, ed, vis, verdict))

lines.append("=" * 78)
lines.append("【一覧】")
lines.append("id / 公演名 / 公演日 / 表示される枠 / 判定")
for tid, name, ed, vis, verdict in summary:
    lines.append("%-5s | %s | %s | %s枠 | %s" % (tid, name, ed, vis, verdict))
ok = sum(1 for s in summary if s[4].startswith("✅"))
hold = sum(1 for s in summary if s[4].startswith("⚠️"))
ng = sum(1 for s in summary if s[4].startswith("❓"))
lines.append("")
lines.append("✅削除OK=%d件 / ⚠️保留=%d件 / ❓判断不能=%d件（対象%d件）" % (ok, hold, ng, len(TARGET)))

with io.open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
print("wrote", OUT, "events=", len(events))
