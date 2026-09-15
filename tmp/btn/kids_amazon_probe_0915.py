# -*- coding: utf-8 -*-
"""子ども向けの作品ごとに「作品名 ぬりえ／おもちゃ／絵本」がAmazonで何件出るかを実測する（2026-09-15 夜）
ユーザー「ニルスのふしぎな旅だったらそのニルスの塗り絵を張ったり、プリキュアだったらプリキュアの玩具だったり、それぞれのボタンを作って」
・数え方は tools/amazon_audit.py と同じ＝商品名に作品名が入っているものだけ数える（Amazonは0件でも関連商品を並べるので data-asin の数では数えない）
・間隔8秒／3件未満は20秒おいて単独で測り直す（連続で叩くと偽の0件を返す）
・カテゴリは絞らない（CDの時の音楽カテゴリ指定は付けない）
使い方: python kids_amazon_probe_0915.py  → tmp/btn_tpl/kids_amazon.json と画面に一覧
"""
import html as _html
import json
import re
import sys
import time
import urllib.parse
import urllib.request

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

WAIT, RETRY_WAIT, HIT_MIN = 8.0, 20.0, 3
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
    'Accept-Language': 'ja,en;q=0.8',
}
ITEMS = {'ぬりえ': r'ぬりえ|塗り絵|ぬり絵', 'おもちゃ': r'おもちゃ|玩具|トイ|フィギュア|ぬいぐるみ|なりきり|変身', '絵本': r'絵本|えほん'}

# (作品名＝検索語, 商品名に入っているか見る語の正規表現, 当てはまるエントリの番号)
WORKS = [
    ("ニルスのふしぎな旅", r"ニルス", [5550]),
    ("プリキュア", r"プリキュア", [450, 6435, 9140, 9143, 9144, 9145, 9146]),
    ("アンパンマン", r"アンパンマン", [312, 9259]),
    ("しまじろう", r"しまじろう", [309, 7094, 7140]),
    ("仮面ライダー", r"仮面ライダー", [6333, 7091, 7137, 7561]),
    ("ウルトラマン", r"ウルトラマン", [2544, 7090, 8314]),
    ("スーパー戦隊", r"戦隊|ジャー", [6532]),
    ("シナモロール", r"シナモロール|シナモン", [43]),
    ("サンリオ", r"サンリオ", [5100, 8659]),
    ("ポムポムプリン", r"ポムポムプリン", [3945]),
    ("ハローキティ", r"キティ", [2362]),
    ("ディズニー", r"ディズニー", [52]),
    ("ファンターネ", r"ファンターネ", [2552, 3507, 5111]),
    ("おかあさんといっしょ", r"おかあさんといっしょ", [9158, 9159]),
    ("レオてつ", r"レオてつ|おとうさんといっしょ", [4223, 6537]),
    ("いないいないばあっ ワンワン", r"ワンワン|いないいないばあ", [5713]),
    ("ガチャピン ムック", r"ガチャピン|ムック", [5594]),
    ("パンどろぼう", r"パンどろぼう", [4283, 9359]),
    ("はらぺこあおむし", r"はらぺこあおむし", [3595]),
    ("ノンタン", r"ノンタン", [1083]),
    ("おまえうまそうだな", r"おまえうまそうだな|ティラノサウルス", [3165]),
    ("えんとつ町のプペル", r"プペル", [2871]),
    ("もうぬげない", r"もうぬげない", [949]),
    ("不思議の国のアリス", r"アリス", [1058, 2915]),
    ("ピノッキオ", r"ピノッキオ", [1063]),
    ("シンドバッド", r"シンドバッド", [4899]),
    ("ゲゲゲの鬼太郎", r"鬼太郎", [2414]),
    ("クレヨンしんちゃん", r"しんちゃん", [9202]),
    ("ゴジラ", r"ゴジラ", [9211, 9212, 9213]),
    ("NARUTO", r"NARUTO|ナルト", [9352, 9353, 9355]),
    ("進撃の巨人", r"進撃の巨人", [9237, 9238, 9239, 9240, 9275, 9276, 9277, 9278, 9279, 9280, 9281, 9282, 9283, 9284, 9377, 9378, 9379, 9380, 9381, 9448, 9450, 9451, 9452]),
    ("ベイビーシャーク", r"ベイビーシャーク|Baby Shark|BABY SHARK", [9396, 9397]),
    ("米村でんじろう", r"でんじろう", [452]),
]


def url_of(q):
    return 'https://www.amazon.co.jp/s?k=' + urllib.parse.quote(q) + '&tag=oshinavi0a-22'


def titles(h):
    out, seen = [], set()
    for t in re.findall(r'<h2[^>]*>.*?<span[^>]*>([^<]{4,200})</span>', h, re.S):
        t = _html.unescape(re.sub(r'\s+', ' ', t)).strip()
        if t and t not in seen:
            seen.add(t); out.append(t)
    return out


def probe(q, work_re, item_re):
    req = urllib.request.Request(url_of(q), headers=HEADERS)
    try:
        h = urllib.request.urlopen(req, timeout=25).read().decode('utf-8', 'replace')
    except Exception as ex:
        return None, str(ex)[:60]
    ts = titles(h)
    return sum(1 for t in ts if re.search(work_re, t) and re.search(item_re, t)), ''


def probe2(q, work_re, item_re):
    n, err = probe(q, work_re, item_re)
    if n is not None and n < HIT_MIN:
        time.sleep(RETRY_WAIT)
        n2, err2 = probe(q, work_re, item_re)
        if n2 is not None:
            n = max(n, n2)
    time.sleep(WAIT)
    return n, err


res = []
for work, wre, ids in WORKS:
    row = {'work': work, 'ids': ids}
    for item, ire in ITEMS.items():
        q = work + ' ' + item
        n, err = probe2(q, wre, ire)
        row[item] = n
        row[item + '_url'] = url_of(q)
        if err:
            row[item + '_err'] = err
    res.append(row)
    print('%s（%d件）｜ぬりえ %s｜おもちゃ %s｜絵本 %s' % (work, len(ids), row['ぬりえ'], row['おもちゃ'], row['絵本']), flush=True)
    with open('tmp/btn_tpl/kids_amazon.json', 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
print('done', len(res))
