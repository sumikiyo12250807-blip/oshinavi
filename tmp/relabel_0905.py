# -*- coding: utf-8 -*-
"""エントリの dateLabel を、そのエントリが実際に持っている tickets 全部から作り直す。

🚨 9/4に作った tmp/label_built_0904.json は **ぴあ再ビルドの産物なので非ぴあ枠を落とす**
   （id6065 は e+の京都11/26が消え、大阪12/24だけになっていた）。だから候補は当てずに、
   現物の tickets から組み直す。ロジックは build_pia_entries.py の dl 生成に合わせる：
     - 実質単日（最早の公演日 == 最遅の公演日）→ 「YYYY年M月D日(曜) 県 会場」
     - 複数日 → 「YYYY年M月D日(曜)〜YYYY年M月D日(曜) 県（5県以上なら"全国ツアー"）」
   年は ticket.type の「R9年」表記と、エントリの date（千秋楽）から復元する。

使い方:
  python tmp/relabel_0905.py --ids 608,620,...      # 差分を見るだけ
  python tmp/relabel_0905.py --ids ... --apply      # dateLabel 行だけを置換して当てる
"""
import json, re, io, sys, datetime

PATH = "index.html"
OUT = "tmp/relabel_0905.txt"
WD = "月火水木金土日"

# 「一般発売（茨城 9/5公演）〜8/27 23:59」「…（千葉 R9年 6/2〜6/30公演）…」
PERF = re.compile(r"（([^（）]*?)\s*(?:(R\d+)年\s*)?(\d{1,2})/(\d{1,2})(?:〜(?:(R\d+)年\s*)?(\d{1,2})/(\d{1,2}))?公演）")


def era_year(era, base_year):
    """R9年 → 2027。Rが無ければ base_year。"""
    if not era:
        return None
    return 2018 + int(era[1:])


def jp(d):
    return "%d年%d月%d日(%s)" % (d.year, d.month, d.day, WD[d.weekday()])


def perf_dates(ev):
    """tickets から (公演日リスト, 県リスト) を作る。年は R9年表記 → 無ければ推定。"""
    end = datetime.date.fromisoformat(ev["date"])
    dates, prefs = [], []
    for t in ev.get("tickets", []):
        m = PERF.search(t.get("type") or "")
        if not m:
            continue
        pref = (m.group(1) or "").strip()
        if pref and pref not in prefs:
            prefs.append(pref)
        for era, mm, dd in ((m.group(2), m.group(3), m.group(4)),
                            (m.group(5) or m.group(2), m.group(6), m.group(7))):
            if not mm:
                continue
            y = era_year(era, None)
            if y is None:
                # 年が書かれていない＝千秋楽の年か、その前年。千秋楽を超えるなら前年に倒す。
                y = end.year
                try:
                    if datetime.date(y, int(mm), int(dd)) > end:
                        y -= 1
                except ValueError:
                    continue
            try:
                d = datetime.date(y, int(mm), int(dd))
            except ValueError:
                continue
            if d not in dates:
                dates.append(d)
    return sorted(dates), prefs


def build_label(ev):
    dates, prefs = perf_dates(ev)
    if not dates:
        return None
    venues = []
    v = ev.get("venue") or ""
    mv = re.match(r"全国ツアー（(.*)）$", v)
    venues = mv.group(1).split("／") if mv else ([v] if v else [])
    if len(prefs) == 1:
        pref = prefs[0]
    elif 2 <= len(prefs) <= 4:
        pref = "・".join(prefs)
    else:
        pref = "全国"
    if dates[0] == dates[-1]:
        # 単日は会場まで出す（venue が「A／B」形なら会場は出さない＝どれか分からない）
        v = venues[0] if len(venues) == 1 else ""
        return ("%s %s %s" % (jp(dates[0]), pref, v)).strip()
    # 🚨 複数公演では会場名を出さない。venue フィールドが1会場のまま古いことがあり
    #    （id1119＝岐阜だけ／id608＝2会場の旧書式）、1つだけ書くと別会場の公演が隠れる。
    tail = "全国ツアー" if pref == "全国" else pref
    return ("%s〜%s %s" % (jp(dates[0]), jp(dates[-1]), tail)).strip()


def main():
    ids = []
    if "--ids" in sys.argv:
        ids = [int(x) for x in sys.argv[sys.argv.index("--ids") + 1].split(",")]
    lines = open(PATH, encoding="utf-8").read().split("\n")
    body = "\n".join(lines)
    events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\n", body, re.S).group(1))
    by = {e["id"]: e for e in events}

    buf, plan = [], {}
    for i in ids:
        e = by.get(i)
        if not e:
            buf.append("id=%s ⚠️現物に無い" % i)
            continue
        new = build_label(e)
        old = e.get("dateLabel") or ""
        if not new:
            buf.append("id=%-5s %s : 公演日を読めず（枠の書式が違う）" % (i, e.get("name", "")))
            continue
        if new == old:
            buf.append("id=%-5s %s : 差分なし" % (i, e.get("name", "")))
            continue
        plan[i] = new
        buf.append("id=%-5s %s" % (i, e.get("name", "")))
        buf.append("    現物: %s" % old)
        buf.append("    新案: %s" % new)
        for t in e.get("tickets", []):
            buf.append("      枠: %s" % t.get("type"))
        buf.append("")

    io.open(OUT, "w", encoding="utf-8").write("\n".join(buf))
    print("TARGETS=%d CHANGE=%d -> %s" % (len(ids), len(plan), OUT))

    if "--apply" in sys.argv and plan:
        # 🚨 値だけの書き換えなので行置換でやる（json.dumps で配列を作り直さない）
        cur = None
        n = 0
        for idx, ln in enumerate(lines):
            m = re.match(r'\s*"id": (\d+),', ln)
            if m:
                cur = int(m.group(1))
                continue
            if cur in plan:
                m2 = re.match(r'(\s*"dateLabel": )(".*?")(,?)$', ln)
                if m2:
                    lines[idx] = m2.group(1) + json.dumps(plan[cur], ensure_ascii=False) + m2.group(3)
                    n += 1
                    del plan[cur]
        bak = "index.html.bak_%s_relabel" % datetime.date.today().strftime("%m%d")
        open(bak, "w", encoding="utf-8").write(body)
        open(PATH, "w", encoding="utf-8").write("\n".join(lines))
        print("APPLIED=%d backup=%s remain=%s" % (n, bak, sorted(plan)))


main()
