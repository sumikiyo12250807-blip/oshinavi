# -*- coding: utf-8 -*-
"""
検索からの流入の「伸びしろ」を数える。
・掲載中のアーティスト数／公演数／会場数／都道府県
・いま検索で着地できるページ数（sitemap.xml）
結果は tmp/seo_gap_0908.md へ。
"""
import json, re, io, collections

src = open("index.html", encoding="utf-8").read()
m = re.search(r"const EVENTS\s*=\s*(\[.*?\]);\s*\n", src, re.S)
events = json.loads(m.group(1))

live = [e for e in events if e.get("genre") != "new"]
newpool = [e for e in events if e.get("genre") == "new"]

artists = collections.Counter()
venues = collections.Counter()
prefs = collections.Counter()
genres = collections.Counter()
for e in live:
    a = (e.get("artist") or "").strip()
    if a:
        for part in re.split(r"[／/]", a):
            part = part.strip()
            if part:
                artists[part] += 1
    v = (e.get("venue") or "").strip()
    if v: venues[v] += 1
    genres[e.get("genre") or "?"] += 1
    for t in e.get("tickets", []) or []:
        mm = re.search(r"（([^\d（）]{2,4}?)\s", t.get("type", "") or "")
        if mm: prefs[mm.group(1)] += 1

sm = open("sitemap.xml", encoding="utf-8").read()
n_urls = sm.count("<loc>")

o = io.open("tmp/seo_gap_0908.md", "w", encoding="utf-8")
W = o.write
W("# 検索からの流入の伸びしろ（2026-09-08）\n\n")
W("- 掲載中のエントリ（新着プールを除く）＝**%d件**／新着プール＝%d件\n" % (len(live), len(newpool)))
W("- 出てくるアーティスト名（／で分割・ユニーク）＝**%d通り**\n" % len(artists))
W("- 会場（ユニーク）＝**%d通り**\n" % len(venues))
W("- いま検索エンジンに出せているページ＝**%d本**（sitemap.xml の登録数）\n" % n_urls)
W("- ＝1ページあたり **%.0f件**の公演を詰め込んでいる\n\n" % (len(live) / max(n_urls, 1)))

W("## 掲載数が多いアーティスト 上位30（＝個別ページを作る価値が高い順）\n\n")
W("| アーティスト | 掲載公演数 |\n|---|---|\n")
for a, n in artists.most_common(30):
    W("| %s | %d |\n" % (a.replace("|", "｜"), n))

W("\n## ジャンル別の在庫\n\n| ジャンル | 件数 |\n|---|---|\n")
for g, n in genres.most_common():
    W("| %s | %d |\n" % (g, n))

W("\n## 会場 上位20\n\n| 会場 | 件数 |\n|---|---|\n")
for v, n in venues.most_common(20):
    W("| %s | %d |\n" % (v.replace("|", "｜")[:40], n))
o.close()
print("wrote tmp/seo_gap_0908.md  live=%d artists=%d venues=%d sitemap_urls=%d"
      % (len(live), len(artists), len(venues), n_urls))
