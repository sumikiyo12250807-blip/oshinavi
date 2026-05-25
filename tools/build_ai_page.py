#!/usr/bin/env python3
"""AI / クローラ向け静的データページ ai.html を生成する。

OSHINAVI(index.html) のイベントデータは const EVENTS = [...] という
JavaScript 配列の中にあり、ブラウザが JS を実行して初めて画面に出る。
AI(Claude/ChatGPT 等) は JS を実行しないため、サイトを読んでも「0件」に見える。
→ JS 不要の静的 HTML を別途生成して、AI からデータが読めるようにする。

判定ロジックは index.html の renderCard / ticketKind / computeCardStatus /
EVENTS.sort と揃えてある（feedback_check_existing_logic: 自前判定の事故あり）。

使い方:
  python tools/build_ai_page.py              # ai.html を生成
  python tools/build_ai_page.py --today 2026-05-23
"""
import argparse
import html
import json
import re
from datetime import date, datetime

# index.html の GENRE_LABEL と同じ
GENRE_LABEL = {
    "new": "✨新着", "jpop": "J-POP", "rock": "ロック", "kpop": "K-POP",
    "yougaku": "洋楽", "hiphop": "HIP HOP", "anime": "アニソン", "idol": "アイドル",
    "youtuber": "YouTuber", "vtuber": "VTuber", "kids": "キッズ",
    "classic": "クラシック", "jazz": "ジャズ", "engeki": "演劇", "fes": "フェス",
    "sports": "スポーツ", "hanabi": "花火大会", "2.5ji": "2.5次元", "seiyuu": "声優",
    "owarai": "お笑い", "musical": "ミュージカル", "aisatsu": "舞台挨拶",
    "dinnershow": "ディナーショー",
}

# index.html の linkDefs 順（楽天 > ぴあ > e+ > ローチケ > その他）
VENDOR_ORDER = [
    ("rakuten", "楽天チケット"), ("pia", "チケットぴあ"), ("eplus", "e+"),
    ("lawson", "ローチケ"), ("fany", "FANY"), ("yoshimoto", "吉本オンライン"),
    ("tvasahi", "テレ朝チケット"), ("shochiku", "松竹チケット"), ("official", "公式"),
]


def extract_events_array(filepath: str):
    """check_expired.py と同じ方式で const EVENTS = [...] を抽出。"""
    with open(filepath, encoding="utf-8") as f:
        text = f.read()
    m = re.search(r"const\s+EVENTS\s*=\s*(\[)", text)
    if not m:
        raise RuntimeError(f"{filepath}: const EVENTS not found")
    start = m.start(1)
    depth = 0
    end = None
    for i in range(start, len(text)):
        c = text[i]
        if c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end is None:
        raise RuntimeError(f"{filepath}: array end not found")
    return json.loads(text[start:end])


def parse(s):
    return date.fromisoformat(s)


def days_from(s, today):
    return (parse(s) - today).days


def ticket_kind(t, today):
    """index.html の ticketKind() と同じ。soldout/終了は None。"""
    if t.get("soldout"):
        return None
    sd, d = t.get("startDate"), t.get("date")
    try:
        if sd and parse(sd) > today:
            n = days_from(sd, today)
            return "urgent" if n <= 7 else "soon" if n <= 31 else "normal"
        if sd and d and parse(d) >= today:
            return "selling"
        if not sd and d and parse(d) >= today:
            n = days_from(d, today)
            return "urgent" if n <= 7 else "soon" if n <= 31 else "normal"
    except ValueError:
        return None
    return None


def card_status(ev, today):
    """index.html の computeCardStatus() と同じ優先度。"""
    kinds = [ticket_kind(t, today) for t in (ev.get("tickets") or [])]
    kinds = [k for k in kinds if k]
    for p in ("urgent", "soon", "selling", "normal"):
        if p in kinds:
            return p
    return "passed"


def next_action(ev, today):
    """index.html の getSortDate() 相当。次アクション(日付, 種別, ticket)を返す。
    発売前は startDate、販売中は終了日 date。売切/終了は除外。"""
    cands = []
    for t in ev.get("tickets") or []:
        if t.get("soldout"):
            continue
        sd, d = t.get("startDate"), t.get("date")
        try:
            if sd and parse(sd) > today:
                cands.append((sd, "presale", t))
            elif d and parse(d) >= today:
                cands.append((d, "selling", t))
        except ValueError:
            continue
    if not cands:
        return None
    cands.sort(key=lambda x: x[0])
    return cands[0]


def buy_url(ev):
    links = ev.get("links") or {}
    for key, _ in VENDOR_ORDER:
        if links.get(key):
            return links[key], dict(VENDOR_ORDER)[key]
    return None, None


STATUS_EMOJI = {"urgent": "🔴", "soon": "🟠", "selling": "🟢", "normal": "🔵", "passed": "⚪"}


def status_text(ev, today):
    """AI/人が読む状態テキストを作る。"""
    na = next_action(ev, today)
    if na is None:
        return "⚪ 販売終了", "9999-99-99"
    d, kind, t = na
    n = days_from(d, today)
    emoji = STATUS_EMOJI[card_status(ev, today)]
    if kind == "presale":
        if n == 0:
            label = "本日発売"
        elif n == 1:
            label = "明日発売"
        else:
            label = f"発売開始まであと{n}日"
        return f"{emoji} {label}（{d}発売）", d
    # selling
    if t.get("saleUntilSoldOut"):
        return f"{emoji} 販売中（予定枚数に達し次第終了）", d
    if n == 0:
        ctxt = "本日締切"
    elif n == 1:
        ctxt = "明日締切"
    else:
        ctxt = f"締切まであと{n}日"
    return f"{emoji} 販売中・{ctxt}（〜{d}）", d


def genre_label(ev):
    g = GENRE_LABEL.get(ev.get("genre", ""), ev.get("genre", ""))
    extras = [GENRE_LABEL.get(x, x) for x in (ev.get("extraGenres") or [])]
    return "／".join([g] + extras)


def esc(s):
    return html.escape(str(s)) if s is not None else ""


PER_PAGE = 50


def page_name(idx):
    """0始まりのページ番号 → ファイル名。1ページ目は ai.html（既存互換）。"""
    return "ai.html" if idx == 0 else f"ai_{idx + 1}.html"


def pager_html(cur, npages, total):
    """全ページへのリンク（50件ずつの範囲ラベル）。現在ページは太字。"""
    parts = []
    for i in range(npages):
        lo = i * PER_PAGE + 1
        hi = min((i + 1) * PER_PAGE, total)
        label = f"{lo}〜{hi}件"
        if i == cur:
            parts.append(f"<strong>[{label}]</strong>")
        else:
            parts.append(f'<a href="/{page_name(i)}">{label}</a>')
    return " ｜ ".join(parts)


def build(today):
    events = [e for e in extract_events_array("index.html") if e.get("verified") is True]

    # 表示対象（次アクションあり=販売中or発売前）を次アクション日順に
    rows = []
    for ev in events:
        na = next_action(ev, today)
        if na is None:
            continue  # 販売終了は載せない
        _, sort_date = status_text(ev, today)
        rows.append((sort_date, ev.get("id", 0), ev))
    rows.sort(key=lambda x: (x[0], x[1]))

    total = len(rows)
    pages = [rows[i:i + PER_PAGE] for i in range(0, total, PER_PAGE)] or [[]]
    npages = len(pages)

    for pidx, page_rows in enumerate(pages):
        lo = pidx * PER_PAGE + 1
        hi = min((pidx + 1) * PER_PAGE, total)
        pager = pager_html(pidx, npages, total)
        prev_link = f'<a href="/{page_name(pidx - 1)}">← 前の50件</a>' if pidx > 0 else ""
        next_link = f'<a href="/{page_name(pidx + 1)}">次の50件 →</a>' if pidx < npages - 1 else ""

        out = []
        out.append("<!DOCTYPE html>")
        out.append('<html lang="ja"><head>')
        out.append('<meta charset="UTF-8">')
        out.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
        out.append('<meta name="robots" content="index,follow">')
        out.append(f"<title>OSHINAVI チケット発売カレンダー（{lo}〜{hi}件目／全{total}件・AIデータ一覧）</title>")
        out.append(f'<meta name="description" content="OSHINAVI掲載チケットの発売日・販売状況一覧（{lo}〜{hi}件目／全{total}件・50件ずつ分割・AI/検索エンジン向け静的データ）。">')
        out.append("<style>")
        out.append("body{font-family:sans-serif;max-width:1100px;margin:0 auto;padding:16px;line-height:1.6;color:#111}")
        out.append("h1{font-size:20px}table{border-collapse:collapse;width:100%;font-size:13px}")
        out.append("th,td{border:1px solid #ccc;padding:6px 8px;text-align:left;vertical-align:top}")
        out.append("th{background:#f3f3f3}a{color:#06c}.note{color:#555;font-size:13px}.pager{margin:12px 0;font-size:13px}")
        out.append("</style></head><body>")
        out.append("<h1>OSHINAVI チケット発売カレンダー</h1>")
        out.append(
            f'<p class="note">AI・検索エンジン向けの静的データ一覧（50件ずつ分割）。'
            f'人間向けのトップは <a href="/">OSHINAVI トップ</a>。<br>'
            f"最終更新: {today.isoformat()} ／ 全 <strong>{total}</strong>件中 "
            f"<strong>{lo}〜{hi}件目</strong>を表示（発売日が近い順）。</p>"
        )
        out.append(f'<div class="pager">ページ（50件ずつ）: {pager}<br>{prev_link} {next_link}</div>')
        out.append("<table>")
        out.append(
            "<tr><th>状態</th><th>イベント</th><th>アーティスト</th>"
            "<th>会場（都道府県）</th><th>開催日</th><th>ジャンル</th>"
            "<th>料金</th><th>購入先</th></tr>"
        )
        for _, _, ev in page_rows:
            st, _ = status_text(ev, today)
            url, vendor = buy_url(ev)
            buy = f'<a href="{esc(url)}" target="_blank" rel="noopener">{esc(vendor)}</a>' if url else "（リンク未設定）"
            held = ev.get("dateLabel") or ev.get("date") or ""
            price = ev.get("price") or "—"
            venue = ev.get("venue", "")
            pref = ev.get("prefecture", "")
            venue_pref = f"{esc(venue)}（{esc(pref)}）" if pref else esc(venue)
            out.append(
                "<tr>"
                f"<td>{esc(st)}</td>"
                f"<td>{esc(ev.get('name',''))}</td>"
                f"<td>{esc(ev.get('artist',''))}</td>"
                f"<td>{venue_pref}</td>"
                f"<td>{esc(held)}</td>"
                f"<td>{esc(genre_label(ev))}</td>"
                f"<td>{esc(price)}</td>"
                f"<td>{buy}</td>"
                "</tr>"
            )
        out.append("</table>")
        out.append(f'<div class="pager">ページ（50件ずつ）: {pager}<br>{prev_link} {next_link}</div>')
        out.append(f'<p class="note">generated by tools/build_ai_page.py at {datetime.now().isoformat(timespec="seconds")}</p>')
        out.append("</body></html>")

        with open(page_name(pidx), "w", encoding="utf-8") as f:
            f.write("\n".join(out))

    # sitemap.xml も同時生成（ページ数の増減に自動追従）
    sm = ['<?xml version="1.0" encoding="UTF-8"?>']
    sm.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for u in ["", "index.html", "events.html"]:
        sm.append(f'  <url><loc>https://oshinavi.jp/{u}</loc><lastmod>{today.isoformat()}</lastmod><changefreq>daily</changefreq></url>')
    for i in range(npages):
        sm.append(f'  <url><loc>https://oshinavi.jp/{page_name(i)}</loc><lastmod>{today.isoformat()}</lastmod><changefreq>daily</changefreq></url>')
    sm.append("</urlset>")
    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write("\n".join(sm))

    print(f"wrote {npages} pages ({total} events, {PER_PAGE}/page, today={today}) + sitemap.xml")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--today", default=None, help="YYYY-MM-DD（デフォルト: 今日）")
    args = ap.parse_args()
    today = date.fromisoformat(args.today) if args.today else date.today()
    build(today)


if __name__ == "__main__":
    main()
