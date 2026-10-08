#!/usr/bin/env python3
"""アーティストごとの軽い静的ページ artist/<番号>.html と一覧 artists.html を作る（2026-10-09 ユーザー決定「2番でいきましょう」）。

Why: OSHINAVI の中身は index.html の EVENTS（JS）にあり、検索エンジンから
「◯◯ チケット 発売日」で来る入口が無い。1組1ページの軽いHTMLを置いて検索の入口にする。
ページは JS なし・その組の「これから買える／発売前の枠」だけを発売日順に並べ、
売り場への直リンクと OSHINAVI の検索（/?q=名前）へのリンクを置く。

判定は build_ai_page.py の関数（index.html の表示ルールと揃えたもの）をそのまま使う。
URL の番号は tools/artist_pages.json に名前ごとに固定する（作り直しても同じ名前は同じURL）。

使い方:
  python tools/build_artist_pages.py               # 作る（sitemap.xml にも足す）
  python tools/build_artist_pages.py --today 2026-10-09
build_ai_page.py の最後から呼ばれる（sitemap.xml を作り直した後に足すため）。
"""
import argparse
import html
import json
import os
import re
import unicodedata
from collections import defaultdict
from datetime import date, datetime

import build_ai_page as A

REG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "artist_pages.json")
OUT_DIR = "artist"
MAX_PAGES = 500          # 人気の組から（これから買える・発売前の枠が多い順）
MIN_ROWS = 1
POP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "artist_popularity.json")  # collect_followers.py
# 名前として使わない（出演者の総称・告知文・催しや会場の名前が artist 欄に入っているもの）
SKIP_NAME = re.compile(r"出演者多数|芸人多数|多数|ほか$|他$|^未定$|^TBA$|^ゲスト|^各|^\s*$|ご確認|公式HP|お知らせ"
                       r"|TOUR|ツアー|公演|ライブ|LIVE|イベント|発売記念|展$|展覧|ミュージアム|CAFE|カフェ|寄席|繁昌亭|館$"
                       r"|劇場|巡業|フェス|FES|祭|コンサート|CONCERT|ミュージカル|『|「|〜|~|in |IN |\d{4}")


def norm(s):
    return unicodedata.normalize("NFKC", s or "").replace(" ", "").replace("　", "").lower()


def esc(s):
    return html.escape(str(s)) if s is not None else ""


def artist_names(ev):
    """エントリの artist を名前に分ける（「A／B」は両方の組のページに載せる）。"""
    a = unicodedata.normalize("NFKC", ev.get("artist") or "").strip()
    if not a:
        return []
    # NFKC で「／」は「/」になる。「AC/DC」のような名前（両側が英字1〜3文字）は割らない
    if re.fullmatch(r"[A-Za-z]{1,3}/[A-Za-z]{1,3}", a):
        parts = [a]
    else:
        parts = [p.strip() for p in a.split("/") if p.strip()]
    if len(parts) > 6:      # 大人数の催しは名前ページにしない
        return []
    # 「aiko Live Tour」のように名前のあとにツアー名が続く形は、前の名前だけを使う
    parts = [re.split(r"\s+(?:LIVE|Live|live|TOUR|Tour|tour|ツアー|CONCERT|Concert|コンサート|ONE ?MAN|ワンマン)\b", p)[0].strip()
             for p in parts]
    return [p for p in parts if len(p) >= 2 and not SKIP_NAME.search(p) and not re.search(r"(?i)live|tour", p) and len(p) <= 40]


def ticket_rows(ev, today):
    """これから発売・販売中の枠（売り切れ・終わった枠は出さない）。"""
    out = []
    for t in ev.get("tickets") or []:
        if t.get("soldout"):
            continue
        sd, d = t.get("startDate"), t.get("date")
        try:
            if sd and A.parse(sd) >= today:
                key, state = sd, "発売前"
            elif d and A.parse(d) >= today:
                key, state = d, "販売中"
            else:
                continue
        except ValueError:
            continue
        out.append((key, state, t))
    return out


def fmt_md(iso):
    try:
        d = date.fromisoformat(iso)
    except (TypeError, ValueError):
        return ""
    return f"{d.month}/{d.day}({'月火水木金土日'[d.weekday()]})"


def state_text(state, t, today):
    # 静的ページは1日3回しか作り直さない＝「本日」「明日」は日付が変わると嘘になる。日付だけで書く
    sd, d = t.get("startDate"), t.get("date")
    if state == "発売前":
        when = f"{fmt_md(sd)}発売"
        if d and d != sd and not t.get("saleEndUnknown"):
            return f"{when}（〜{fmt_md(d)}）"
        return when
    if t.get("saleUntilSoldOut"):
        return "販売中（予定枚数に達し次第終了）"
    if t.get("saleEndUnknown"):
        return f"{fmt_md(sd)}〜発売中" if sd else "販売中"
    return f"販売中（〜{fmt_md(d)}）"


def vendor_of(url):
    u = url or ""
    for k, name in [("rakuten", "楽天チケット"), ("pia.jp", "チケットぴあ"), ("eplus", "e+"), ("l-tike", "ローチケ"),
                    ("tiget", "TIGET"), ("fany", "FANY"), ("zaiko", "ZAIKO"), ("livepocket", "livePocket")]:
        if k in u:
            return name
    return "売り場"


CSS = ("body{font-family:sans-serif;max-width:860px;margin:0 auto;padding:16px;line-height:1.6;color:#1a1a1a;background:#fff}"
       "h1{font-size:22px;margin:8px 0}h2{font-size:17px;margin:20px 0 6px;border-left:4px solid #e4007f;padding-left:8px}"
       ".note{color:#555;font-size:13px}.cta{display:inline-block;margin:10px 0;padding:10px 16px;background:#e4007f;color:#fff;"
       "border-radius:8px;text-decoration:none;font-weight:bold}.ev{border:1px solid #ddd;border-radius:8px;padding:10px 12px;margin:10px 0}"
       ".ev .n{font-weight:bold}.ev .v{color:#444;font-size:14px}ul{padding-left:18px;margin:6px 0}li{margin:4px 0;font-size:14px}"
       ".st{font-weight:bold;color:#c00}.pre{color:#0a58ca}a{color:#06c;word-break:break-all}"
       "@media (prefers-color-scheme: dark){body{background:#111;color:#eee}.ev{border-color:#444}.ev .v,.note{color:#bbb}a{color:#6af}}")


def page_html(name, items, today, stamp, total_rows):
    title = f"{name} チケット発売日・先行・一般発売まとめ | OSHINAVI"
    first = items[0][0] if items else None
    desc = (f"{name}のチケット情報（{today.month}/{today.day}更新）。これから発売・販売中の受付{total_rows}件を発売日順に。"
            f"先行・一般発売の日付と売り場へのリンクをまとめています。")
    q = html.escape(f"https://oshinavi.jp/?q={name}", quote=True)
    o = ["<!DOCTYPE html>", '<html lang="ja"><head>', '<meta charset="UTF-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
         '<meta name="robots" content="index,follow">',
         f"<title>{esc(title)}</title>", f'<meta name="description" content="{esc(desc)}">',
         f"<style>{CSS}</style></head><body>",
         '<p class="note"><a href="/">OSHINAVI</a> ＞ <a href="/artists.html">アーティスト一覧</a></p>',
         f"<h1>{esc(name)} のチケット発売日</h1>",
         f'<p class="note">最終更新：{esc(stamp)}／これから発売・販売中の受付 {total_rows}件（発売日・締切が近い順）。'
         f'日付は各売り場の掲載にもとづきます。買う前に売り場のページで必ず確かめてください。</p>',
         f'<a class="cta" href="{q}">OSHINAVIで「{esc(name)}」を見る</a>']
    for _, ev, rows in items:
        o.append('<div class="ev">')
        o.append(f'<div class="n">{esc(ev.get("name") or "")}</div>')
        venue = ev.get("venue") or ""
        pref = ev.get("prefecture") or ""
        held = ev.get("dateLabel") or ev.get("date") or ""
        o.append(f'<div class="v">{esc(venue)}{("（" + esc(pref) + "）") if pref else ""}／公演 {esc(held)}</div><ul>')
        for key, state, t in rows:
            cls = "pre" if state == "発売前" else "st"
            url = t.get("url") or A.buy_url(ev)[0]
            link = f' <a href="{esc(url)}" target="_blank" rel="noopener">{esc(vendor_of(url))}</a>' if url else ""
            o.append(f'<li><span class="{cls}">{esc(state_text(state, t, today))}</span> {esc(t.get("type") or "")}{link}</li>')
        o.append("</ul></div>")
    o.append(f'<a class="cta" href="{q}">OSHINAVIで「{esc(name)}」を見る</a>')
    o.append('<p class="note"><a href="/artists.html">ほかのアーティストを見る</a>｜<a href="/">OSHINAVI トップ</a></p>')
    o.append("</body></html>")
    return "\n".join(o)


def build(today):
    _n = datetime.now()
    stamp = f"{today.year}年{today.month}月{today.day}日 {_n:%H:%M}"
    events = [e for e in A.extract_events_array("index.html") if e.get("verified") is True and e.get("genre") != "new"]

    by = defaultdict(lambda: {"name": None, "items": []})
    for ev in events:
        rows = ticket_rows(ev, today)
        if not rows:
            continue
        rows.sort(key=lambda r: r[0])
        for nm in artist_names(ev):
            k = norm(nm)
            if not k:
                continue
            g = by[k]
            g["name"] = g["name"] or nm
            g["items"].append((rows[0][0], ev, rows))

    # 人気の組から＝X投稿の準備で調べたフォロワー数（エントリ単位）の最大値 → 受付の数
    try:
        pop = {int(k): v for k, v in json.load(open(POP, encoding="utf-8")).items()}
    except FileNotFoundError:
        pop = {}
    for g in by.values():
        g["pop"] = max((pop.get(ev.get("id"), 0) for _, ev, _ in g["items"]), default=0)
    ranked = sorted(by.items(), key=lambda kv: (-kv[1]["pop"], -sum(len(r) for _, _, r in kv[1]["items"]),
                                                -len(kv[1]["items"]), kv[0]))
    ranked = [kv for kv in ranked if sum(len(r) for _, _, r in kv[1]["items"]) >= MIN_ROWS][:MAX_PAGES]

    try:
        reg = json.load(open(REG, encoding="utf-8"))
    except FileNotFoundError:
        reg = {}
    nxt = max(reg.values(), default=0) + 1
    os.makedirs(OUT_DIR, exist_ok=True)
    made = []
    for k, g in ranked:
        if k not in reg:
            reg[k] = nxt
            nxt += 1
        items = sorted(g["items"], key=lambda x: (x[0], x[1].get("id", 0)))
        total_rows = sum(len(r) for _, _, r in items)
        with open(os.path.join(OUT_DIR, f"{reg[k]}.html"), "w", encoding="utf-8") as f:
            f.write(page_html(g["name"], items, today, stamp, total_rows))
        made.append((g["name"], reg[k], total_rows))
    json.dump(reg, open(REG, "w", encoding="utf-8"), ensure_ascii=False, indent=0, sort_keys=True)

    # 今回作らなかった（これから買える枠が無くなった）組の古いページは消す＝売り切れ・終わった情報を検索に残さない
    live = {str(n) for _, n, _ in made}
    for fn in os.listdir(OUT_DIR):
        m = re.fullmatch(r"(\d+)\.html", fn)
        if m and m.group(1) not in live:
            os.remove(os.path.join(OUT_DIR, fn))

    # 一覧ページ（五十音・アルファベット順）
    made_sorted = sorted(made, key=lambda x: norm(x[0]))
    o = ["<!DOCTYPE html>", '<html lang="ja"><head>', '<meta charset="UTF-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1.0">', '<meta name="robots" content="index,follow">',
         "<title>アーティスト別 チケット発売日一覧 | OSHINAVI</title>",
         f'<meta name="description" content="OSHINAVIに載っているアーティスト{len(made)}組の、これから発売・販売中のチケット発売日ページの一覧。">',
         f"<style>{CSS}</style></head><body>",
         '<p class="note"><a href="/">OSHINAVI</a></p>', "<h1>アーティスト別 チケット発売日</h1>",
         f'<p class="note">最終更新：{esc(stamp)}／{len(made)}組（これから発売・販売中の受付がある組）。</p><ul>']
    for nm, n, cnt in made_sorted:
        o.append(f'<li><a href="/{OUT_DIR}/{n}.html">{esc(nm)}</a>（{cnt}件）</li>')
    o.append("</ul></body></html>")
    with open("artists.html", "w", encoding="utf-8") as f:
        f.write("\n".join(o))

    # sitemap.xml に足す（build_ai_page が毎回作り直すので、その後に呼ばれる前提）
    sm = open("sitemap.xml", encoding="utf-8").read()
    sm = re.sub(r"\s*<url><loc>https://oshinavi\.jp/(?:artists\.html|artist/\d+\.html)</loc>.*?</url>", "", sm)
    add = [f'  <url><loc>https://oshinavi.jp/artists.html</loc><lastmod>{today.isoformat()}</lastmod><changefreq>daily</changefreq></url>']
    for _, n, _ in made:
        add.append(f'  <url><loc>https://oshinavi.jp/{OUT_DIR}/{n}.html</loc><lastmod>{today.isoformat()}</lastmod><changefreq>daily</changefreq></url>')
    sm = sm.replace("</urlset>", "\n".join(add) + "\n</urlset>")
    open("sitemap.xml", "w", encoding="utf-8").write(sm)
    print(f"artist pages {len(made)} + artists.html + sitemap (today={today})")
    return made


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--today", default=None)
    a = ap.parse_args()
    build(date.fromisoformat(a.today) if a.today else date.today())


if __name__ == "__main__":
    main()
