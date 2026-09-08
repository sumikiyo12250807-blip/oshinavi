# -*- coding: utf-8 -*-
"""
X投稿を「OSHINAVIに人が流れ込んだか」だけで並べ直す。
指標はインプではなく URL Clicks（＝サイトへ来た人数）と Profile visits。
出力は tmp/x_deepdive_0908b.md（UTF-8）。コンソールには日本語を出さない。
"""
import csv, io, re, datetime, statistics, collections

CSV = "tmp/x_content_0908.csv"
OUT = "tmp/x_deepdive_0908b.md"
TODAY = datetime.date(2026, 9, 8)
MIN_AGE_DAYS = 2  # 2日たっていない投稿は判定に入れない

rows = []
with io.open(CSV, encoding="utf-8-sig", newline="") as f:
    for r in csv.DictReader(f):
        d = (r.get("Date") or "").strip()
        dt = None
        hh = 0
        hm = re.search(r"(\d{1,2}):(\d{2})", d)
        if hm:
            hh = int(hm.group(1))
        # 形1: "Sun, Sep 6, 2026"
        MON = {m: i + 1 for i, m in enumerate(
            ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])}
        m1 = re.search(r"([A-Z][a-z]{2})\s+(\d{1,2}),\s*(\d{4})", d)
        m2 = re.match(r"(\d{4})-(\d{2})-(\d{2})", d)
        m3 = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})", d)
        try:
            if m1 and m1.group(1) in MON:
                dt = datetime.date(int(m1.group(3)), MON[m1.group(1)], int(m1.group(2)))
            elif m2:
                dt = datetime.date(int(m2.group(1)), int(m2.group(2)), int(m2.group(3)))
            elif m3:
                dt = datetime.date(int(m3.group(3)), int(m3.group(1)), int(m3.group(2)))
        except Exception:
            dt = None
        if dt is None:
            continue
        if (TODAY - dt).days < MIN_AGE_DAYS:
            continue

        def num(k):
            v = (r.get(k) or "0").replace(",", "").strip()
            try: return int(float(v))
            except Exception: return 0

        rows.append({
            "date": dt, "hour": hh,
            "text": (r.get("Post text") or "").strip(),
            "imp": num("Impressions"),
            "clk": num("URL Clicks"),
            "perm": num("Permalink Clicks"),
            "det": num("Detail Expands"),
            "prof": num("Profile visits"),
            "like": num("Likes"),
            "rt": num("Reposts"),
            "share": num("Shares"),
            "follow": num("New follows"),
            "eng": num("Engagements"),
        })

rows.sort(key=lambda x: (x["date"], x["hour"]))
o = io.open(OUT, "w", encoding="utf-8")
W = o.write

W("# Xの投稿を「サイトに人が来たか」だけで並べ直す（%s 時点）\n\n" % TODAY)
W("- 対象＝投稿から2日以上たった **%d本**\n" % len(rows))
tot_imp = sum(r["imp"] for r in rows)
tot_clk = sum(r["clk"] for r in rows)
tot_prof = sum(r["prof"] for r in rows)
tot_fol = sum(r["follow"] for r in rows)
W("- 合計インプ **%s** ／ サイトへのクリック **%d** ／ プロフィール訪問 **%d** ／ 新規フォロー **%d**\n"
  % ("{:,}".format(tot_imp), tot_clk, tot_prof, tot_fol))
W("- **表示1万回あたりのサイト流入＝%.1f人**\n\n" % (tot_clk / tot_imp * 10000 if tot_imp else 0))

# ---- 1. クリックの偏り ----
W("## 1. クリックはどこに集まっているか\n\n")
cl = sorted(rows, key=lambda x: -x["clk"])
nonzero = [r for r in rows if r["clk"] > 0]
W("- クリックが1以上ついた投稿＝**%d本／%d本（%.0f%%）**\n" % (len(nonzero), len(rows), len(nonzero)/len(rows)*100))
top10 = cl[:10]
W("- 上位10本で全クリックの **%.0f%%**（%d／%d）を稼いでいる\n\n"
  % (sum(r["clk"] for r in top10)/tot_clk*100 if tot_clk else 0, sum(r["clk"] for r in top10), tot_clk))

W("### クリック上位20本（＝実際にOSHINAVIへ人を運んだ投稿）\n\n")
W("（CSVに時刻が入っていないので時間帯の列は出さない）\n\n")
W("| 日付 | インプ | クリック | CTR | RT | いいね | 冒頭40字 |\n|---|---|---|---|---|---|---|\n")
for r in cl[:20]:
    if r["clk"] == 0: break
    head = r["text"].replace("\n", " ").replace("|", "｜")[:40]
    W("| %s | %d | **%d** | %.2f%% | %d | %d | %s |\n"
      % (r["date"].strftime("%m/%d"), r["imp"], r["clk"],
         r["clk"]/r["imp"]*100 if r["imp"] else 0, r["rt"], r["like"], head))

# ---- 2. インプが大きいのにクリック0 ----
W("\n## 2. 「たくさん見られたのに1人も来なかった」投稿\n\n")
big0 = sorted([r for r in rows if r["clk"] == 0 and r["imp"] >= 1000], key=lambda x: -x["imp"])
W("- インプ1000以上でクリック0＝**%d本**（合計インプ %s＝**丸ごと取りこぼし**）\n\n"
  % (len(big0), "{:,}".format(sum(r["imp"] for r in big0))))
W("| 日付 | インプ | RT | いいね | 冒頭40字 |\n|---|---|---|---|---|\n")
for r in big0[:15]:
    head = r["text"].replace("\n", " ").replace("|", "｜")[:40]
    W("| %s | %d | %d | %d | %s |\n" % (r["date"].strftime("%m/%d"), r["imp"], r["rt"], r["like"], head))

# ---- 3. 冒頭の型 ----
def head_type(t):
    first = t.split("\n")[0]
    if "ピックアップ" in first:
        return "A テンプレ見出し（OSHINAVIの〜ピックアップ🎫）"
    if re.match(r"^\s*[【\[]", first):
        return "B 【】で始まる告知"
    return "C 話し言葉で始まる"

W("\n## 3. 1行目の型で分ける\n\n")
W("| 型 | 本数 | 中央インプ | 合計クリック | 1本あたりクリック | CTR |\n|---|---|---|---|---|---|\n")
g = collections.defaultdict(list)
for r in rows: g[head_type(r["text"])].append(r)
for k in sorted(g):
    v = g[k]
    imps = [x["imp"] for x in v]
    sc, si = sum(x["clk"] for x in v), sum(imps)
    W("| %s | %d | %.0f | %d | **%.2f** | %.2f%% |\n"
      % (k, len(v), statistics.median(imps), sc, sc/len(v), sc/si*100 if si else 0))

# ---- 4. 本数と1日あたりの流入 ----
W("\n## 4. 1日に何本出した日が、いちばん人を運んだか\n\n")
byday = collections.defaultdict(list)
for r in rows: byday[r["date"]].append(r)
buckets = collections.defaultdict(list)
for d, v in byday.items():
    n = len(v)
    b = "1〜2本" if n <= 2 else ("3〜5本" if n <= 5 else ("6〜8本" if n <= 8 else "9本以上"))
    buckets[b].append((sum(x["clk"] for x in v), sum(x["imp"] for x in v), n))
W("| 1日の本数 | 日数 | その日の合計クリック(中央) | 合計インプ(中央) |\n|---|---|---|---|\n")
for k in ["1〜2本", "3〜5本", "6〜8本", "9本以上"]:
    if k not in buckets: continue
    v = buckets[k]
    W("| %s | %d日 | %.1f | %.0f |\n" % (k, len(v), statistics.median([x[0] for x in v]), statistics.median([x[1] for x in v])))

# ---- 5. 時系列（週ごと） ----
W("\n## 5. 週ごとの流入（伸びているのか止まっているのか）\n\n")
wk = collections.defaultdict(lambda: [0, 0, 0, 0])
for r in rows:
    k = (r["date"] - datetime.timedelta(days=r["date"].weekday()))
    wk[k][0] += r["imp"]; wk[k][1] += r["clk"]; wk[k][2] += 1; wk[k][3] += r["follow"]
W("| 週(月曜) | 本数 | インプ | サイトへのクリック | 1万インプあたり流入 | 新規フォロー |\n|---|---|---|---|---|---|\n")
for k in sorted(wk):
    imp, clk, n, fol = wk[k]
    W("| %s | %d | %s | **%d** | %.1f | %d |\n"
      % (k.strftime("%m/%d"), n, "{:,}".format(imp), clk, clk/imp*10000 if imp else 0, fol))

# ---- 6. RT・いいねとクリックの関係 ----
W("\n## 6. 拡散（RT/いいね）とサイト流入は連動しているか\n\n")
with_rt = [r for r in rows if r["rt"] > 0]
no_rt = [r for r in rows if r["rt"] == 0]
for label, v in [("RTがついた投稿", with_rt), ("RT 0の投稿", no_rt)]:
    if not v: continue
    si = sum(x["imp"] for x in v); sc = sum(x["clk"] for x in v)
    W("- %s＝%d本／中央インプ %.0f／1本あたりクリック **%.2f**／CTR %.2f%%\n"
      % (label, len(v), statistics.median([x["imp"] for x in v]), sc/len(v), sc/si*100 if si else 0))

o.close()
print("wrote %s  rows=%d  total_clicks=%d" % (OUT, len(rows), tot_clk))
