# -*- coding: utf-8 -*-
"""同じ名前で複数エントリに分裂しているものを1エントリに畳む。

方針＝[[feedback_tour_consolidate]]「複数会場のツアー・同じ内容の複数公演は1エントリにまとめる」
  venue＝全国ツアー（会場を全部列挙）／prefecture＝県を列挙（5県以上は「全国」）
  date＝最遅（千秋楽）／tickets＝全部集めて重複を除く（**枠は1つも捨てない**）

🚫触らないもの
  - スポーツ（主催・座席種で売り場が違う＝[[feedback_sports_home_away_never_merge]]）
  - オーケストラ／交響楽団／フィル（1公演1エントリが多数派）
  - 名前に ≪ ＜ 【 が入っている（座席種・券種が名前に入っている）
  - ジャンルが揃っていない組

🚨安全弁
  - 畳む前後で「画面に出る枠」の数が減ったら中止
  - 枠のURLは1つも落とさない（そのまま持ってくる）
  - id は「いちばん枠が多いエントリ」のものを残す（新しいidを作らない）

  python tmp/fold_splits_0904.py          # 下見
  python tmp/fold_splits_0904.py --apply  # 実行
"""
import json, re, io, sys, shutil, unicodedata, datetime
from collections import defaultdict

PATH = "index.html"
TODAY = "2026-09-04"
APPLY = "--apply" in sys.argv

raw = io.open(PATH, encoding="utf-8", newline="").read()
m = re.search(r"const EVENTS = (\[.*?\]);\r?\n", raw, re.S)
src_text = m.group(1)
events = json.loads(src_text)


def dump(evs):
    return json.dumps(evs, ensure_ascii=False, indent=2)


if dump(events) != src_text.replace("\r\n", "\n"):
    print("ABORT: 書式の往復チェックに落ちた"); sys.exit(1)


def norm(s):
    s = unicodedata.normalize("NFKC", s or "")
    return re.sub(r"[\s　・／/＜＞<>「」『』（）()【】’'\"!！\-—]", "", s).lower()


def visible(t):
    """画面に出る枠か（[[feedback_heal_flattens_ticket_types]]の突合と同じ式）"""
    if t.get("saleUntilSoldOut") or t.get("soldout"):
        return True
    sd, d = t.get("startDate"), (t.get("date") or "")
    return not ((not sd or sd <= TODAY) and d < TODAY)


def uniq_vis(evs):
    """🚨重複（同じ type+date+url が別エントリにまたがっている分）を除いた、画面に出る枠の数。
       素の合計で比べると、畳んで重複が消えただけで『枠が減った』と誤検知する
       （実測＝来生たかお・ONE PARK HANGOUTFES など11本がエントリをまたいだ二重登録だった）。"""
    seen = set()
    for e in evs:
        for t in e.get("tickets", []):
            if visible(t):
                seen.add((norm(e.get("name")), t.get("type"), t.get("date"), t.get("url") or ""))
    return len(seen)


before_vis = uniq_vis(events)
before_raw = sum(1 for e in events for t in e.get("tickets", []) if visible(t))
before_n = len(events)

g = defaultdict(list)
for e in events:
    if e.get("genre") == "new":
        continue
    k = norm(e.get("name"))
    if k:
        g[k].append(e)

WD = "月火水木金土日"


def jp(d):
    y, mo, da = (int(x) for x in d.split("-"))
    s = "%d年%d月%d日(%s)" % (y, mo, da, WD[datetime.date(y, mo, da).weekday()])
    return s


def halls(v):
    """会場名のリスト。🚨「全国ツアー」だけの venue は会場名ではないので空を返す
       （括弧なしの "全国ツアー" を会場名として拾うと
         「全国ツアー（全国ツアー／◯◯ホール）」という表記になる）"""
    v = (v or "").strip()
    mm = re.match(r"全国ツアー（(.+)）$", v)
    if mm:
        return [x.strip() for x in mm.group(1).split("／") if x.strip() and x.strip() != "全国ツアー"]
    if not v or v == "全国ツアー":
        return []
    return [v]


folded, skipped = [], []
drop_ids = set()
for k, es in g.items():
    if len(es) < 2:
        continue
    nm = " ".join(e.get("name") or "" for e in es)
    gens = set(e.get("genre") for e in es)
    if "sports" in gens:
        skipped.append((es, "スポーツ")); continue
    if any(x in nm for x in ("オーケストラ", "交響楽団", "フィル")):
        skipped.append((es, "オーケストラ")); continue
    if re.search(r"[≪＜<【]", nm):
        skipped.append((es, "名前に券種・座席種")); continue
    if len(gens) > 1:
        skipped.append((es, "ジャンルが揃っていない %s" % gens)); continue

    es_sorted = sorted(es, key=lambda e: -len(e.get("tickets", [])))
    keep = es_sorted[0]
    others = es_sorted[1:]

    # 枠を集める（同じ type+date+url は1つに）
    seen = set()
    merged = []
    for e in es_sorted:
        for t in e.get("tickets", []):
            key = (t.get("type"), t.get("date"), t.get("url") or "")
            if key in seen:
                continue
            seen.add(key); merged.append(dict(t))
    merged.sort(key=lambda t: (t.get("date") or ""))

    # 会場・県・日付
    hs = []
    for e in es_sorted:
        for h in halls(e.get("venue")):
            if h and h not in hs:
                hs.append(h)
    prefs = []
    for e in es_sorted:
        for p in (e.get("prefecture") or "").split("・"):
            p = p.strip()
            if p and p != "全国" and p not in prefs:
                prefs.append(p)
    dates = sorted(x for x in (e.get("date") for e in es_sorted) if x)
    first = min(dates); last = max(dates)

    folded.append({
        "keep": keep, "others": others, "tickets": merged,
        "venue": ("全国ツアー（%s）" % "／".join(hs)) if len(hs) > 1 else (hs[0] if hs else keep.get("venue")),
        "prefecture": ("全国" if len(prefs) >= 5 else "・".join(prefs)) if prefs else keep.get("prefecture"),
        "date": last,
        "dateLabel": ("%s〜%s %s" % (jp(first), jp(last),
                                    ("全国ツアー" if len(prefs) >= 5 else "・".join(prefs)))
                      if first != last else keep.get("dateLabel")),
    })
    drop_ids.update(e.get("id") for e in others)

print("分裂している組=%d" % sum(1 for k, v in g.items() if len(v) > 1))
print("  畳む=%d組（消えるエントリ %d件）" % (len(folded), len(drop_ids)))
print("  触らない=%d組" % len(skipped))

buf = ["エントリの分裂を畳む 2026-09-04", ""]
for f in folded:
    k = f["keep"]
    buf.append("=" * 70)
    buf.append("■ %s → id%s に寄せる（%s を消す）" % (
        k.get("name"), k.get("id"), "／".join("id%s" % e.get("id") for e in f["others"])))
    buf.append("   枠 %d → %d" % (sum(len(e.get("tickets", [])) for e in [k] + f["others"]), len(f["tickets"])))
    buf.append("   会場 %s" % f["venue"][:100])
    buf.append("   期間 %s" % f["dateLabel"])
buf.append("")
buf.append("【触らなかった組】")
for es, why in skipped:
    buf.append("  %s（%s）… %s" % ((es[0].get("name") or "")[:40], why,
                                   "／".join("id%s" % e.get("id") for e in es)))
io.open("tmp/fold_splits_0904.txt", "w", encoding="utf-8").write("\n".join(buf))

# 適用（メモリ上で組み替えて安全弁）
by_id = {e.get("id"): e for e in events}
for f in folded:
    k = by_id[f["keep"].get("id")]
    k["tickets"] = f["tickets"]
    k["venue"] = f["venue"]
    k["prefecture"] = f["prefecture"]
    k["date"] = f["date"]
    if f["dateLabel"]:
        k["dateLabel"] = f["dateLabel"]
    # links は欠けているものだけ補う
    for e in f["others"]:
        for kk, vv in (e.get("links") or {}).items():
            if vv and not (k.get("links") or {}).get(kk):
                k.setdefault("links", {})[kk] = vv
new_events = [e for e in events if e.get("id") not in drop_ids]

after_vis = uniq_vis(new_events)
after_raw = sum(1 for e in new_events for t in e.get("tickets", []) if visible(t))
print("画面に出る枠（生の合計） %d → %d  ＝差は重複が消えたぶん" % (before_raw, after_raw))
print("画面に出る枠（重複を除く） %d → %d  ← ここが減ったら中止" % (before_vis, after_vis))
print("エントリ %d → %d" % (before_n, len(new_events)))
if after_vis < before_vis:
    print("🚨ABORT: 画面に出る枠が減った（%d本）" % (before_vis - after_vis)); sys.exit(2)

if not APPLY:
    print("(下見のみ。--apply で書き込み)  詳細 -> tmp/fold_splits_0904.txt"); sys.exit(0)

shutil.copy(PATH, PATH + ".bak_0904_fold")
out = raw[:m.start(1)] + dump(new_events).replace("\n", "\r\n") + raw[m.end(1):]
io.open(PATH, "w", encoding="utf-8", newline="").write(out)
print("WROTE index.html (backup: index.html.bak_0904_fold)")
