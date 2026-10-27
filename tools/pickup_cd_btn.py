#!/usr/bin/env python3
"""今週のピックアップの記事（1組1ページ）に「予習する（最新CD）」のボタンを足す（2026-10-27 すちこ「④の記事にCDボタンもお願い」）。

- 記事の「発売になる公演 タップで探す」（pk-shows・?q=名前）の名前で EVENTS を引き、その組の links.amazon を使う
  （tools/amazon_latest.py で商品ページになっていればそれ・無ければ検索のURL）。
- エントリに links.amazon が無く、音楽のジャンルの組だけ「名前 CD」の検索を作る（reference_amazon_affiliate の付与対象）。
  演劇・お笑い・展覧会などの CD が合わない組には付けない。
- ボタンは index.html と同じ画像（img/btn_cd_0915.png）。クリックは GA4 へ（tools/click_track.py・page_kind=pickup）。
- 何度回しても同じ（印 pk-amz があれば差し替える）。号を作ったら最後に1回回す。

使い方: python tools/pickup_cd_btn.py            # pickup/ の全号
        python tools/pickup_cd_btn.py --dry      # 書かずに付く組と付かない組を出す
"""
import argparse
import glob
import io
import json
import os
import re
import sys
import unicodedata
import urllib.parse

import click_track

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
TAG = "oshinavi0a-22"
CD_GENRES = {"jpop", "rock", "idol", "kpop", "hiphop", "classic", "anime", "seiyuu", "vtuber", "youtuber", "enka", "jazz",
             "yougaku"}
BOX = re.compile(r'\n?[ \t]*<div class="pk-amz"[^>]*>.*?</div>', re.S)


def norm(s):
    return unicodedata.normalize("NFKC", s or "").lower().replace(" ", "").replace("　", "")


def load_events():
    s = io.open("index.html", encoding="utf-8").read()
    m = re.search(r"const\s+EVENTS\s*=\s*(\[)", s)
    return json.JSONDecoder().raw_decode(s, m.start(1))[0]


def cd_for(name, E):
    n = norm(name)
    mine = [e for e in E if e.get("genre") != "new" and n and (n == norm(e.get("artist")) or
                                                               n in [norm(p) for p in re.split(r"[／/]", e.get("artist") or "")])]
    if not mine and len(n) >= 3:   # 「辻井伸行（ピアノ）」「Carved In Stone／…」のような書き方も拾う
        mine = [e for e in E if e.get("genre") != "new" and n in norm(e.get("artist"))]
    urls = [(e.get("links") or {}).get("amazon") for e in mine
            if (e.get("links") or {}).get("amazon") and not (e.get("links") or {}).get("amazonLabel")]
    urls = [u for u in urls if u.startswith("http") and ("amazon.co.jp" in u or "amzn.to" in u)]
    # 検索のリンクは公演名で探しているもの（「大和証券グループ presents 辻井伸行…」）が混ざる＝記事では使わず名前で作る。
    # 使うのは商品ページ（/dp/）と人が選んだ短縮リンク（amzn.to）だけ
    urls = [u for u in urls if "/s?" not in u]
    for u in urls:
        if "/dp/" in u:
            return u
    if urls:
        return urls[0]
    if any(e.get("genre") in CD_GENRES or (e.get("links") or {}).get("amazon") for e in mine):
        k = name if all(e.get("genre") == "classic" for e in mine) else f"{name} CD"
        return f"https://www.amazon.co.jp/s?k={urllib.parse.quote(k)}&i=specialty-aps&srs=26200021051&tag={TAG}"
    return None


def box(url):
    return ('\n  <div class="pk-amz" style="margin:12px 0 4px">'
            f'<a href="{url}" target="_blank" rel="noopener" style="display:inline-block">'
            '<img src="../../img/btn_cd_0915.png" alt="予習する（最新CD）" style="height:40px;display:block" loading="lazy" decoding="async">'
            '</a></div>')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    E = load_events()
    got, none = [], []
    for f in sorted(glob.glob("pickup/*/*.html")):
        if os.path.basename(f) == "index.html":
            continue
        s = io.open(f, encoding="utf-8", newline="").read()
        m = re.search(r'<a class="pk-shows" href="[^"]*\?q=([^"&]+)"[^>]*>.*?</a>', s, re.S)
        if not m:
            none.append((f, "（pk-shows なし＝深掘りなど）"))
            continue
        name = urllib.parse.unquote(m.group(1))
        url = cd_for(name, E)
        s2 = BOX.sub("", s)
        if url:
            m2 = re.search(r'<a class="pk-shows" href="[^"]*\?q=[^"]+"[^>]*>.*?</a>', s2, re.S)
            s2 = s2[:m2.end()] + box(url) + s2[m2.end():]
            got.append((f, name, url))
        else:
            none.append((f, name))
        if click_track.MARK not in s2:
            s2 = s2.replace("</body>", click_track.snippet("pickup") + "\n</body>", 1)
        if not a.dry and s2 != s:
            io.open(f, "w", encoding="utf-8", newline="").write(s2)
    for f, n, u in got:
        print("付けた", f, n, u[:90])
    for x in none:
        print("付けない", *x)
    print(f"付けた {len(got)} / 付けない {len(none)}")


if __name__ == "__main__":
    main()
