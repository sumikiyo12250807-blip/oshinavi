# -*- coding: utf-8 -*-
"""e+新着の artist が「公演名の先頭1語」で切れているのを、実ページの出演者に直す。

🚨 EVENTS 配列を json.dumps で作り直さない。"id": N の行を目印にして
   その直後の "artist": の行だけを行ベースで置換する（改行コードを壊さないため）。
   [[feedback_index_html_crlf_preserve]] の 2026-08-31 項の雛形どおり。
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

PATH = "index.html"

# id -> 新しい artist。根拠はすべて e+ 実ページの出演者欄
# （tmp/eplus_artist_src_0906.txt に機械で取った生データを残してある）
FIX = {
    # --- artist が「公演名の先頭1語」で切れていたもの ---
    6951: "Project U.D.M",
    6953: "GUNGIRE／KALA／Strawday ほか",
    6954: "Chanty／Sick2",
    6955: "ホタル／ジュリィー",
    6956: "フラワーカンパニーズ／アルカラ／ビレッジマンズストア／LACCO TOWER ほか",
    6957: "opium／MERALOA／SHUTO／MEME／tzkwym",
    6959: "前田拳太郎",
    6961: "ドミコ",
    6962: "FUNKY MONKEY BΛBY’S",
    6963: "you／RENO",
    6964: "メトロトム／SEX-ANDROID／NoGoD ほか",
    6966: "小野大輔／山下大輝／佐藤拓也／櫻井孝宏 ほか",
    6967: "なきごと／バチカン市国に愛されたい／ミーマイナー",
    6968: "新原泰佑／北香那／田中俊介／橋本さとし ほか",
    6969: "アロージャズオーケストラ／見砂和照と東京キューバンボーイズ／渡辺真知子",
    6971: "庄野真代／細坪基佳／桑山哲也／横田美穂／名渡山遼 ほか",
    6975: "Hammer Head Shark",
    6976: "Enfants／Hammer Head Shark",
    6977: "LOSTAGE／MEANING／bacho／waterweed ほか",
    6978: "ヒカシュー",
    6980: "アルカラ／夜の本気ダンス／LEGO BIG MORL ほか",
    6981: "climbgrow／Panorama Panama Town",
    6982: "辰巳ゆうと／青山新／MATSURI",
    6985: "石川さゆり",
    # --- 対バン相手が artist に入っておらず、その名前で検索しても出てこないもの ---
    6934: "THE BACK HORN／クリープハイプ",
    6936: "Sick2／Co’COON／Chanty ほか",
    6965: "摩天楼オペラ／NoGoD",
    6974: "古舘伊知郎／南野陽子／岩崎良美／デーモン閣下／八神純子 ほか",
}

with io.open(PATH, encoding="utf-8", newline="") as f:
    lines = f.read().split("\n")

ID_RE = re.compile(r'^\s*"id":\s*(\d+),\s*\r?$')
ARTIST_RE = re.compile(r'^(\s*"artist":\s*)(.*?)(,\s*\r?)$')

cur = None
done = {}
for i, ln in enumerate(lines):
    m = ID_RE.match(ln)
    if m:
        cur = int(m.group(1))
        continue
    if cur in FIX and cur not in done:
        ma = ARTIST_RE.match(ln)
        if ma:
            old = json.loads(ma.group(2))
            new = FIX[cur]
            lines[i] = ma.group(1) + json.dumps(new, ensure_ascii=False) + ma.group(3)
            done[cur] = (old, new)

with io.open(PATH, "w", encoding="utf-8", newline="") as f:
    f.write("\n".join(lines))

for eid in sorted(done):
    old, new = done[eid]
    print("id=%-5d %s  →  %s" % (eid, old, new))
missing = sorted(set(FIX) - set(done))
print("")
print("直した件数 = %d / 指定 %d" % (len(done), len(FIX)))
if missing:
    print("🚨 見つからなかった id:", missing)
