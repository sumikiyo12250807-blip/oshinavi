# -*- coding: utf-8 -*-
"""子ども向けの「〇〇グッズ」ボタンの飛び先（作品名だけのAmazon検索）が使えるかを実測する（2026-09-15 夜）
ユーザー「グッズで作って」（しまじろうと同じ「〇〇グッズ」でそろえる）
・飛び先＝ https://www.amazon.co.jp/s?k=<作品名>&tag=oshinavi0a-22 （しまじろう＝ユーザーのリンクも作品名だけの検索だった）
・数え方＝商品名に作品名が入っている商品の数（data-asin では数えない）。3件以上で使える
・間隔8秒／3件未満は20秒おいて単独で測り直す
使い方: python kids_goods_probe_0915.py → tmp/btn_tpl/kids_goods.json
"""
import html as _html
import json
import re
import sys
import time
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
WAIT, RETRY_WAIT, HIT_MIN = 8.0, 20.0, 3
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
           'Accept-Language': 'ja,en;q=0.8'}

# (ボタンの字, 検索語, 商品名に入っているか見る正規表現, エントリ名に当てる正規表現)
# 並び順に意味がある＝先に当たったものを使う（シナモロール・ポムポムプリン・キティをサンリオより前／ファンターネをおかあさんといっしょより前）
WORKS = [
    ("プリキュアグッズ", "プリキュア", r"プリキュア", r"プリキュア"),
    ("アンパンマングッズ", "アンパンマン", r"アンパンマン", r"アンパンマン"),
    ("仮面ライダーグッズ", "仮面ライダー", r"仮面ライダー", r"仮面ライダー"),
    ("ウルトラマングッズ", "ウルトラマン", r"ウルトラマン", r"ウルトラ"),
    ("シナモロールグッズ", "シナモロール", r"シナモロール|シナモン", r"シナモロール"),
    ("ポムポムプリングッズ", "ポムポムプリン", r"ポムポムプリン", r"ポムポムプリン"),
    ("ハローキティグッズ", "ハローキティ", r"キティ", r"キティ|Kitty"),
    ("サンリオグッズ", "サンリオ", r"サンリオ", r"サンリオ"),
    ("ディズニーグッズ", "ディズニー", r"ディズニー", r"ディズニー"),
    ("ファンターネグッズ", "ファンターネ", r"ファンターネ", r"ファンターネ"),
    ("おかあさんといっしょグッズ", "おかあさんといっしょ", r"おかあさんといっしょ", r"おかあさんといっしょ"),
    ("ワンワングッズ", "いないいないばあっ ワンワン", r"ワンワン|いないいないばあ", r"ワンワン"),
    ("ガチャピン・ムックグッズ", "ガチャピン ムック", r"ガチャピン|ムック", r"ガチャピン"),
    ("パンどろぼうグッズ", "パンどろぼう", r"パンどろぼう", r"パンどろぼう"),
    ("はらぺこあおむしグッズ", "はらぺこあおむし", r"はらぺこあおむし", r"はらぺこあおむし"),
    ("ノンタングッズ", "ノンタン", r"ノンタン", r"ノンタン"),
    ("えんとつ町のプペルグッズ", "えんとつ町のプペル", r"プペル", r"プペル"),
    ("不思議の国のアリスグッズ", "不思議の国のアリス", r"アリス", r"不思議の国のアリス"),
    ("シンドバッドグッズ", "シンドバッド", r"シンドバッド", r"シンドバッド"),
    ("ゲゲゲの鬼太郎グッズ", "ゲゲゲの鬼太郎", r"鬼太郎", r"鬼太郎"),
    ("クレヨンしんちゃんグッズ", "クレヨンしんちゃん", r"しんちゃん", r"クレヨンしんちゃん"),
    ("ゴジラグッズ", "ゴジラ", r"ゴジラ", r"ゴジラ"),
    ("NARUTOグッズ", "NARUTO", r"NARUTO|ナルト", r"NARUTO|ナルト"),
    ("進撃の巨人グッズ", "進撃の巨人", r"進撃の巨人", r"進撃の巨人"),
    ("ベイビーシャークグッズ", "ベイビーシャーク", r"ベイビーシャーク|Baby Shark|BABY SHARK|ベビーシャーク", r"BABY SHARK|ベイビーシャーク"),
    ("ニルスのふしぎな旅グッズ", "ニルスのふしぎな旅", r"ニルス", r"ニルス"),
]


def url_of(q):
    return 'https://www.amazon.co.jp/s?k=' + urllib.parse.quote(q) + '&tag=oshinavi0a-22'


def probe(q, tre):
    try:
        h = urllib.request.urlopen(urllib.request.Request(url_of(q), headers=HEADERS), timeout=25).read().decode('utf-8', 'replace')
    except Exception as ex:
        return None, [], str(ex)[:60]
    ts, seen = [], set()
    for t in re.findall(r'<h2[^>]*>.*?<span[^>]*>([^<]{4,200})</span>', h, re.S):
        t = _html.unescape(re.sub(r'\s+', ' ', t)).strip()
        if t and t not in seen:
            seen.add(t); ts.append(t)
    hit = [t for t in ts if re.search(tre, t)]
    return len(hit), hit[:3], ''


res = []
for label, q, tre, ere in WORKS:
    n, ex, err = probe(q, tre)
    if n is not None and n < HIT_MIN:
        time.sleep(RETRY_WAIT)
        n2, ex2, err2 = probe(q, tre)
        if n2 is not None and n2 > n:
            n, ex = n2, ex2
    time.sleep(WAIT)
    res.append({'label': label, 'query': q, 'url': url_of(q), 'title_re': tre, 'event_re': ere,
                'hits': n, 'ok': bool(n is not None and n >= HIT_MIN), 'examples': ex, 'err': err})
    print('%s｜%s件｜%s' % (label, n, ' / '.join(e[:30] for e in ex)), flush=True)
    with open('tmp/btn_tpl/kids_goods.json', 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
print('done', len(res), 'ok', sum(r['ok'] for r in res))
