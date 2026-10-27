#!/usr/bin/env python3
"""「予習する（最新CD）」の飛び先を、Amazon の検索結果から**いちばん新しいCDの商品ページ**に変える（2026-10-27 すちこ「③のAmazonを商品ページにするのもお願い」）。

Why: 9月の管理画面は「月に100回以上押されて注文1件」。検索結果に着くと、どれを買えばいいか分からずに帰る。
     その人の最新作の商品ページに着けば、そのままカートに入れられる。

やり方:
  - links.amazon が検索URL（/s?k=）のエントリを、検索語ごとにまとめる（同じ人は1回だけ調べる）
  - 人気の順（tools/artist_popularity.json のフォロワー数）に上から --top 組
  - 音楽カテゴリを「新しい順」（&s=date-desc-rank）で検索 → 商品名に名前が入っているCDの先頭を採る
    （同じ作品の盤違いが並んだら「通常盤」を選ぶ）。名前が入っていなければ変えない＝検索のまま
  - 🚨Amazon は続けて叩くと空のページを返す（10/27 実測＝10秒あけても2組目で止まった）＝--wait 秒あけ、
    空のページは5分おいて1回だけ読み直す。3回続けて空なら止める
  - 調べるだけ（tmp/amazon_latest.json）→ --apply で index.html に書く（ほかの道具が index.html を書いていない時に）

使い方:
  python tools/amazon_latest.py --top 300 --wait 45
  python tools/amazon_latest.py --apply
"""
import argparse
import html as _html
import io
import json
import os
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
OUT = "tmp/amazon_latest.json"
TAG = "oshinavi0a-22"
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
     "Accept-Language": "ja,en;q=0.8"}
SKIP_TITLE = re.compile(r"オムニバス|V\.?A\.?|ヴァリアス|Various|トリビュート|tribute|カラオケ|オルゴール"
                        r"|\[Analog\]|アナログ|レコード|\bLP\b|重量盤", re.I)   # 10/27 人間椅子でレコード盤を選んだ＝CDのボタンなので外す


def norm(s):
    return unicodedata.normalize("NFKC", s or "").lower().replace(" ", "").replace("　", "")


def load():
    s = io.open("index.html", encoding="utf-8", newline="").read()
    m = re.search(r"const\s+EVENTS\s*=\s*(\[)", s)
    E, end = json.JSONDecoder().raw_decode(s, m.start(1))
    return s, m.start(1), end, E


def query_of(u):
    m = re.search(r"[?&]k=([^&]+)", u or "")
    if not m:
        return None, False
    k = urllib.parse.unquote(m.group(1)).strip()
    with_cd = bool(re.search(r"\sCD$", k))
    return re.sub(r"\s*CD$", "", k).strip(), with_cd


def fetch(kw, with_cd):
    u = ("https://www.amazon.co.jp/s?k=" + urllib.parse.quote(kw + (" CD" if with_cd else ""))
         + "&i=specialty-aps&srs=26200021051&s=date-desc-rank")
    try:
        return urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=25).read().decode("utf-8", "replace")
    except Exception as ex:
        return "ERR " + str(ex)[:80]


def results(h):
    out = []
    for m in re.finditer(r'<div[^>]+data-asin="([A-Z0-9]{10})"[^>]*data-component-type="s-search-result"(.*?)'
                         r'(?=<div[^>]+data-asin="[A-Z0-9]{10}"[^>]*data-component-type="s-search-result"|$)', h, re.S):
        blk = m.group(2)
        t = re.search(r"<h2[^>]*>.*?<span[^>]*>([^<]{2,250})</span>", blk, re.S)
        if not t:
            continue
        out.append((m.group(1), _html.unescape(t.group(1)).strip(), bool(re.search(r">(?:CD|Audio CD)<", blk))))
    return out


def cowork(kw, title):
    """商品名の「 - 」のあと（名義）にほかの人が並ぶ＝共作・合同盤（10/27 ASKA→「音銀河 - 玉置浩二・ASKA」・dustbox→3組の合同盤）。
    その人の最新作ではないので選ばない。"""
    m = re.search(r"\s-\s([^-]+?)(?:\s*[\(（\[].*)?$", title)
    if not m:
        return False
    parts = [p for p in re.split(r"\s*(?:・|/|／|&|＆|×|,|、| feat\.? | with )\s*", m.group(1)) if p.strip()]
    # 名前そのものに「&」「/」が入る人（例：反田恭平&ジャパン・ナショナル・オーケストラ）は名義と同じなら共作ではない
    return len(parts) >= 2 and norm(kw) != norm(m.group(1))


def choose(kw, rs):
    n = norm(kw)
    hit = [r for r in rs[:10] if r[2] and n and n in norm(r[1]) and not SKIP_TITLE.search(r[1]) and not cowork(kw, r[1])]
    if not hit:
        return None
    first = hit[0]
    # 「【Amazon.co.jp限定】◯◯ (完全生産限定盤)」の頭の【】は外して作品名で盤違いをまとめる（10/27 YOASOBI で限定盤を選んだ）
    def base_of(t):
        return norm(re.split(r"[\(（\[【]", re.sub(r"^\s*【[^】]*】\s*", "", t))[0])[:8]
    base = base_of(first[1])
    same = [r for r in hit if base_of(r[1]) == base]
    tsu = [r for r in same if "通常盤" in r[1]]
    return (tsu or [first])[0]


def survey(top, wait):
    _, _, _, E = load()
    try:
        pop = {int(k): v for k, v in json.load(open("tools/artist_popularity.json", encoding="utf-8")).items()}
    except FileNotFoundError:
        pop = {}
    q = {}
    for e in E:
        u = (e.get("links") or {}).get("amazon")
        if not u or "/s?" not in u or (e.get("links") or {}).get("amazonLabel"):
            continue
        kw, with_cd = query_of(u)
        if not kw or len(norm(kw)) < 2:
            continue
        d = q.setdefault((kw, with_cd), {"ids": [], "pop": 0})
        d["ids"].append(e["id"])
        d["pop"] = max(d["pop"], pop.get(e["id"], 0))
    order = sorted(q.items(), key=lambda kv: (-kv[1]["pop"], -len(kv[1]["ids"])))[:top]
    try:
        done = json.load(open(OUT, encoding="utf-8"))
    except FileNotFoundError:
        done = {}
    empty_run = 0
    for i, ((kw, with_cd), d) in enumerate(order, 1):
        key = kw + ("|CD" if with_cd else "")
        if key in done and done[key].get("state") in ("ok", "nomatch"):
            continue
        h = fetch(kw, with_cd)
        rs = results(h)
        if not rs:
            time.sleep(300)
            h = fetch(kw, with_cd)
            rs = results(h)
        if not rs:
            empty_run += 1
            done[key] = {"state": "empty", "ids": d["ids"]}
            print(f"[{i}/{len(order)}] {kw} 空のページ（{empty_run}回続けて）", flush=True)
            if empty_run >= 3:
                print("止める＝Amazon が続けて空のページを返した", flush=True)
                break
        else:
            empty_run = 0
            c = choose(kw, rs)
            if c:
                done[key] = {"state": "ok", "asin": c[0], "title": c[1], "ids": d["ids"], "pop": d["pop"]}
                print(f"[{i}/{len(order)}] {kw} → {c[0]} {c[1][:60]}", flush=True)
            else:
                done[key] = {"state": "nomatch", "ids": d["ids"], "top": [r[1][:50] for r in rs[:3]]}
                print(f"[{i}/{len(order)}] {kw} 名前の入ったCDなし＝検索のまま", flush=True)
        json.dump(done, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
        time.sleep(wait)


def apply():
    done = json.load(open(OUT, encoding="utf-8"))
    s, st, end, E = load()
    to = {}
    for k, v in done.items():
        # 調べた時に共作の決まりが無かった分は、書く時にはじく（検索のまま）
        if v.get("state") == "ok" and not cowork(k.split("|")[0], v.get("title", "")) and not SKIP_TITLE.search(v.get("title", "")):
            for i in v["ids"]:
                to[i] = f"https://www.amazon.co.jp/dp/{v['asin']}?tag={TAG}"
    n = 0
    for e in E:
        u = (e.get("links") or {}).get("amazon")
        if e["id"] in to and u and "/s?" in u:
            e["links"]["amazon"] = to[e["id"]]
            n += 1
    nl = "\r\n" if "\r\n" in s[:2000] else "\n"
    body = "[" + nl + ("," + nl).join(json.dumps(x, ensure_ascii=False, separators=(",", ":")) for x in E) + nl + "]"
    io.open("index.html", "w", encoding="utf-8", newline="").write(s[:st] + body + s[end:])
    print(f"商品ページに変えた {n}件（{sum(1 for v in done.values() if v.get('state') == 'ok')}組）")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=300)
    ap.add_argument("--wait", type=float, default=45)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    apply() if a.apply else survey(a.top, a.wait)
