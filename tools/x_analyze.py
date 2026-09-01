# -*- coding: utf-8 -*-
"""X投稿の実測CSVを読んで「どの書き方が効いたか」を出す。

使い方:
    python tools/x_analyze.py tmp/x_content_0901.csv
    python tools/x_analyze.py tmp/x_content_0901.csv --min-age 2

前提と決まりごと（memory由来・勝手に変えない）:
  - 判定は投稿の2日後（当日の数字で結論を出さない）＝ --min-age 2 が既定
  - 母数15未満の群では勝ち負けを言わない（「まだ判定しない」と出す）
  - 跳ねた1本で群が持ち上がるので、必ず「全体」と「最大値を1本外した後」の両方を出す
  - CSVの Post text は204字で切れる。タグ数・字数はローカルの全文が見つかった投稿だけで数える
  - CSVの Date 列はUTC。日付と時刻は Post id（Snowflake）から復元したJSTを使う
"""
from __future__ import print_function
import argparse
import csv
import glob
import io
import json
import os
import re
import sys
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRUNC_LEN = 204
TWITTER_EPOCH_MS = 1288834974657
JST = timedelta(hours=9)

# 見出しは `OSHINAVIの"M/D発売"ピックアップ🎫` と `OSHINAVIの"明日発売"ピックアップ🎫` の両方の形がある
HEADING_RE = re.compile(u'OSHINAVIの["“]?[^"”\\n]{1,12}["”]?\\s*ピックアップ')
# 【…】は本来ジャンル見出しだが「【明日8/25(火) 10:00発売】」のような日付見出しにも使われている
NOT_GENRE_RE = re.compile(u'\\d|発売')
SLOT_RE = re.compile(u'^\\s*(\\d{1,2}):(\\d{2})\\s')
GENRE_RE = re.compile(u'【([^】]+)】')
MONTHS = {m: i + 1 for i, m in enumerate(
    "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split())}


def read_text(path):
    with io.open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def norm_key(text):
    """本文の頭を突き合わせ用に正規化する（空白・改行を落として60字）。"""
    t = re.sub(r"\s+", "", text)
    return t[:60]


def load_local_texts():
    """ローカルに残した投稿全文を「頭60字 -> 本文」で引けるようにする。"""
    index = {}
    patterns = [
        os.path.join(ROOT, "tmp", "x*", "post*.txt"),
        os.path.join(ROOT, "tmp", "x*", "*.txt"),
        os.path.join(ROOT, "tmp", "x_*.txt"),
    ]
    for pat in patterns:
        for path in glob.glob(pat):
            try:
                text = read_text(path)
            except Exception:
                continue
            if len(text.strip()) < 40:
                continue
            key = norm_key(text)
            if key and key not in index:
                index[key] = text
    return index


def snowflake_time(post_id):
    """Post id から投稿時刻(JST)を割り出す。"""
    try:
        n = int(post_id)
    except (TypeError, ValueError):
        return None
    ms = (n >> 22) + TWITTER_EPOCH_MS
    return datetime(1970, 1, 1) + timedelta(milliseconds=ms) + JST


def parse_date(s):
    """'Sun, Aug 30, 2026' を date にする。"""
    m = re.search(r"([A-Z][a-z]{2})\s+(\d{1,2}),\s*(\d{4})", s or "")
    if not m:
        return None
    mon = MONTHS.get(m.group(1))
    if not mon:
        return None
    return datetime(int(m.group(3)), mon, int(m.group(2)))


def to_int(v):
    try:
        return int(str(v).replace(",", "").strip() or 0)
    except ValueError:
        return 0


def kind_of(body, list_lines):
    """主役 / まとめ / その他 を本文から見分ける。"""
    if list_lines >= 3:
        return u"まとめ"
    if GENRE_RE.search(body):
        return u"まとめ"
    return u"主役"


def build_rows(csv_path, local):
    rows = []
    with io.open(csv_path, encoding="utf-8", newline="") as f:
        for raw in csv.DictReader(f):
            text = raw.get("Post text") or ""
            truncated = len(text) >= TRUNC_LEN
            full = local.get(norm_key(text))
            body = full if full else text
            lines = body.splitlines()
            list_lines = sum(1 for ln in lines if SLOT_RE.match(ln))
            genres = [g for g in GENRE_RE.findall(body) if not NOT_GENRE_RE.search(g)]
            imp = to_int(raw.get("Impressions"))
            clicks = to_int(raw.get("URL Clicks"))
            ts = snowflake_time(raw.get("Post id"))
            # 🚨CSVの Date 列は UTC（朝7時台の投稿が前日扱いで入る）。
            # Post id から復元したJSTの日付を正とし、idが読めない時だけ Date 列に落とす。
            date = datetime(ts.year, ts.month, ts.day) if ts else parse_date(raw.get("Date"))
            rows.append({
                "id": raw.get("Post id"),
                "date": date,
                "ts": ts,
                "hour": ts.hour if ts else None,
                "text": text,
                "full": bool(full),
                "truncated": truncated and not full,
                "heading": bool(HEADING_RE.search(text[:120])),
                "tags": body.count(u"#") if (full or not truncated) else None,
                "chars": len(body) if full else None,
                "list_lines": list_lines,
                "genre": genres[0] if genres else None,
                "kind": kind_of(body, list_lines),
                "opening": re.sub(r"\s+", u" ", text.lstrip())[:40],
                "imp": imp,
                "clicks": clicks,
                "engagements": to_int(raw.get("Engagements")),
                "reposts": to_int(raw.get("Reposts")),
                "likes": to_int(raw.get("Likes")),
                "follows": to_int(raw.get("New follows")),
                "expands": to_int(raw.get("Detail Expands")),
                "ctr": (clicks / float(imp)) if imp else 0.0,
            })
    return rows


def median(values):
    vs = sorted(values)
    if not vs:
        return 0
    n = len(vs)
    mid = n // 2
    return vs[mid] if n % 2 else (vs[mid - 1] + vs[mid]) / 2.0


def stats(group):
    imps = [r["imp"] for r in group]
    clicks = sum(r["clicks"] for r in group)
    imp_sum = sum(imps)
    return {
        "n": len(group),
        "imp_median": median(imps),
        "imp_mean": (imp_sum / float(len(group))) if group else 0,
        "clicks": clicks,
        "ctr": (clicks / float(imp_sum)) if imp_sum else 0.0,
        "clicks_per_post": (clicks / float(len(group))) if group else 0.0,
        "reposts": sum(r["reposts"] for r in group),
        "follows": sum(r["follows"] for r in group),
    }


def drop_top(group, key="clicks"):
    """いちばん跳ねた1本を外す（外れ値1本で群が持ち上がる罠の検算）。"""
    if len(group) <= 1:
        return group
    top = max(group, key=lambda r: r[key])
    return [r for r in group if r is not top]


def compare(name, groups, min_n, out):
    """groups = [(ラベル, [row,...]), ...] を全体と外れ値除きの両方で並べる。"""
    out.append(u"")
    out.append(u"### %s" % name)
    thin = [label for label, g in groups if len(g) < min_n]
    header = u"| 群 | 本数 | 中央インプ | CTR | 1本あたりclk | 外れ値1本を外した中央インプ |"
    out.append(header)
    out.append(u"|---|---|---|---|---|---|")
    for label, g in groups:
        if not g:
            continue
        s = stats(g)
        s2 = stats(drop_top(g, "imp"))
        out.append(u"| %s | %d | %s | %.2f%% | %.2f | %s |" % (
            label, s["n"], fmt(s["imp_median"]), s["ctr"] * 100,
            s["clicks_per_post"], fmt(s2["imp_median"])))
    if thin:
        out.append(u"")
        out.append(u"🚨**まだ判定しない**（母数%d本未満）＝ %s" % (min_n, u"／".join(thin)))
    return out


def fmt(v):
    if isinstance(v, float) and abs(v - round(v)) > 1e-9:
        return u"%.1f" % v
    return u"%d" % int(round(v))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--min-age", type=int, default=2,
                    help=u"何日たった投稿から数えるか（既定2＝2日後に判定）")
    ap.add_argument("--min-n", type=int, default=15,
                    help=u"この本数未満の群では勝ち負けを言わない（既定15）")
    ap.add_argument("--out", help=u"日本語レポートの書き出し先（既定 tmp/x_analysis_MMDD.md）")
    ap.add_argument("--json", help=u"機械可読の結果を書き出す先")
    args = ap.parse_args()

    local = load_local_texts()
    rows = build_rows(args.csv, local)
    if not rows:
        print(u"CSVに行が無いわ")
        return 1

    latest = max(r["date"] for r in rows if r["date"])
    cutoff = latest - timedelta(days=args.min_age)
    ripe = [r for r in rows if r["date"] and r["date"] <= cutoff]
    fresh = len(rows) - len(ripe)

    out = []
    out.append(u"# X投稿の実測（%s 時点）" % latest.strftime("%Y-%m-%d"))
    out.append(u"")
    out.append(u"- 対象＝**%d本**（投稿から%d日以上たったもの）／まだ数えない分＝%d本" % (
        len(ripe), args.min_age, fresh))
    out.append(u"- 全文が手元にある投稿＝%d本／CSVで切れている分＝%d本（字数とタグ数はこの分を除いて数える）" % (
        sum(1 for r in ripe if r["full"]), sum(1 for r in ripe if r["truncated"])))
    total = stats(ripe)
    out.append(u"- 合計＝インプ中央 **%s**／リンククリック **%d**／RT %d／新規フォロー **%d**" % (
        fmt(total["imp_median"]), total["clicks"], total["reposts"], total["follows"]))

    compare(u"見出し「ピックアップ🎫」の有無", [
        (u"見出しあり", [r for r in ripe if r["heading"]]),
        (u"見出しなし", [r for r in ripe if not r["heading"]]),
    ], args.min_n, out)

    compare(u"投稿の型", [
        (u"まとめ", [r for r in ripe if r["kind"] == u"まとめ"]),
        (u"主役1組", [r for r in ripe if r["kind"] == u"主役"]),
    ], args.min_n, out)

    buckets = [(u"7-9時", 7, 9), (u"10-16時", 10, 16), (u"17-19時", 17, 19),
               (u"20-23時", 20, 23), (u"0-6時", 0, 6)]
    compare(u"投稿した時間帯", [
        (label, [r for r in ripe if r["hour"] is not None and lo <= r["hour"] <= hi])
        for label, lo, hi in buckets
    ], args.min_n, out)

    week = u"月火水木金土日"
    compare(u"曜日", [
        (week[i] + u"曜", [r for r in ripe if r["date"] and r["date"].weekday() == i])
        for i in range(7)
    ], args.min_n, out)

    genres = {}
    for r in ripe:
        if r["genre"]:
            genres.setdefault(r["genre"], []).append(r)
    top_genres = sorted(genres.items(), key=lambda kv: -len(kv[1]))[:8]
    if top_genres:
        compare(u"ジャンル別まとめ", top_genres, args.min_n, out)

    sized = [r for r in ripe if r["chars"]]
    if sized:
        compare(u"字数（全文が手元にある分だけ）", [
            (u"〜500字", [r for r in sized if r["chars"] <= 500]),
            (u"501〜1200字", [r for r in sized if 500 < r["chars"] <= 1200]),
            (u"1201字〜", [r for r in sized if r["chars"] > 1200]),
        ], args.min_n, out)

    out.append(u"")
    out.append(u"## 伸びた順トップ10（この期間の実物）")
    out.append(u"")
    out.append(u"| 日付 | 時刻 | 型 | インプ | clk | RT | 冒頭 |")
    out.append(u"|---|---|---|---|---|---|---|")
    for r in sorted(ripe, key=lambda x: -x["imp"])[:10]:
        out.append(u"| %s | %s | %s | %d | %d | %d | %s |" % (
            r["date"].strftime("%m/%d"),
            r["ts"].strftime("%H:%M") if r["ts"] else u"-",
            r["kind"], r["imp"], r["clicks"], r["reposts"],
            r["opening"].replace(u"|", u"｜")[:28]))

    out.append(u"")
    out.append(u"## クリックが付いた投稿（0でないものだけ）")
    out.append(u"")
    clicked = sorted([r for r in ripe if r["clicks"] > 0], key=lambda x: -x["clicks"])
    if clicked:
        out.append(u"| 日付 | 型 | インプ | clk | CTR | 冒頭 |")
        out.append(u"|---|---|---|---|---|---|")
        for r in clicked[:15]:
            out.append(u"| %s | %s | %d | %d | %.2f%% | %s |" % (
                r["date"].strftime("%m/%d"), r["kind"], r["imp"], r["clicks"],
                r["ctr"] * 100, r["opening"].replace(u"|", u"｜")[:28]))
        out.append(u"")
        out.append(u"- クリック0の投稿＝**%d本／%d本**" % (
            len(ripe) - len(clicked), len(ripe)))
    else:
        out.append(u"この期間はクリック0だったわ。")

    report = u"\n".join(out) + u"\n"
    out_path = args.out or os.path.join(
        ROOT, "tmp", "x_analysis_%s.md" % latest.strftime("%m%d"))
    with io.open(out_path, "w", encoding="utf-8") as f:
        f.write(report)
    print("OK wrote %s (%d posts, %d ripe)" % (out_path, len(rows), len(ripe)))

    if args.json:
        with io.open(args.json, "w", encoding="utf-8") as f:
            f.write(json.dumps({
                "latest": latest.strftime("%Y-%m-%d"),
                "n_ripe": len(ripe),
                "total": total,
                "rows": [{k: (v.strftime("%Y-%m-%d %H:%M") if isinstance(v, datetime) else v)
                          for k, v in r.items() if k != "text"} for r in ripe],
            }, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
