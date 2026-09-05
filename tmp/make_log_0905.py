# -*- coding: utf-8 -*-
"""投入・修正したものを logs/ に残す（後から携帯で遡れるように）。"""
import json, io, re, datetime

TODAY = datetime.date.today().isoformat()
hh = io.open('index.html', encoding='utf-8', newline='').read()
db = {e['id']: e for e in json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);', hh, re.S).group(1))}

NEW_IDS = list(range(6935, 6946))
FIX = [
    (6103, '川崎学園祭 お笑いライブ!!', '締切 2026-09-06→2026-10-17（発売日のままだった）／e+のURL／artistを出演者3組に'),
    (6295, 'アロージャズオーケストラ', 'e+の先着一般発売枠（9/19 10:00〜11/27）が丸ごと抜けていたので追加／URL／正式名に'),
    (6080, '灼熱のマンボVS輝けるスイング!', '締切 2026-09-19→2027-01-09（発売日のままだった）／e+のURL／artistを出演者名に'),
    (583, 'MELANCHOLIC CIRCUS', '別アーティスト「サーカス」（加藤実）の東京12/2枠2つが混入していたので除去→愛知9/26の単独公演に戻した'),
    (6939, 'MEME× tzkwym 「血湧き肉躍る-ハロウィン-」', 'artistを「L-MEME／tzkwym」に（既存 id6022/id6207 と同じ名前で探せるように）'),
]

L = []
L.append('# %s e+から新着に投入（受付前ぶん）＋既存の直し\n' % TODAY)
L.append('ソース＝イープラス（`/sf/word/` の未登録プール）。**確認用の表は作らず、新着タブの実物で見てもらう**方式。\n')
L.append('機械ゲート＝`gate_eplus_slots.py` PASS（実ページの枠合計26／ビルド26・公演の取りこぼし0）／'
         '`reconcile_eplus.py --ids` **FAIL 0**／`check_badges` OK／`check_order.js` 並び順違反0／CRLF指紋 全行CRLF。\n')
L.append('独立検証（別エージェントがゼロから再導出）＝**照合できた枠 27/27・取れなかったページ0**。'
         '公演日・会場・県すべて一致、締切も実ページの受付終了日と一致、重複・誤結合なし。'
         '指摘を受けた artist の直し2件は反映済み。\n')
L.append('\n## 新着に入れた11件\n')
L.append('| id | 出演 | 公演名 | 会場 | 公演日 | 枠 | 確認用 |')
L.append('|---|---|---|---|---|---|---|')
for i in NEW_IDS:
    e = db[i]
    url = (e.get('links') or {}).get('eplus') or ''
    L.append('| %d | %s | %s | %s | %s | %d | [ページ](%s) |'
             % (i, e['artist'], e['name'], e['venue'], e['date'], len(e['tickets']), url))

L.append('\n## 既存エントリの直し5件\n')
L.append('| id | 公演名 | 直したこと |')
L.append('|---|---|---|')
for i, nm, what in FIX:
    L.append('| %d | %s | %s |' % (i, nm, what))

L.append("""
## 🚨 この日わかったこと

1. **`tools/eplus_harvest.py` の build が、アーティスト名の部分一致でDBにある候補を捨てていた。**
   これから発売の候補36件のうち、eidで本当にDBにあったのは18件。残り18件は新規なのに
   **16件が名前の巻き添えで消え、投入できたのは2件だけ**だった
   （サーカス⊂メランコリックサーカス／wacci／シンギュラリティ／Sick2／"THE"で切れた おとぎ話 など）。
   → **eid判定に変更**（旧挙動は `--name-dedup`）。ぴあ側は2026-08-17に同じ直しをしてあった。

2. **同じ e+ の base-eid でも、-Pページごとに興行が違うことがある。**
   `0314250001` は P0030049＝「渡辺真知子、サーカス、三浦祐太朗 ～時代を彩る名曲コンサート～」（12/4 神戸）、
   P0030050＝「クリスマスジャズ&ポピュラーコンサート ゲスト:サーカス」（12/5 奈良）で**別の公演**。
   束ねる前に各-PページのJSON-LDの公演名を突き合わせること。

3. **ぴあ側でも「部分一致で畳む」事故が生きていた**＝eventCd 2630866（サーカス／加藤実）の枠が
   id583「MELANCHOLIC CIRCUS」に入っていた。**飛び先ページの表題を開いて確かめる**。

4. **e+ も叩きすぎると HTTP 503 を返す**＝`reconcile_eplus` の [FETCH] は「枠が死んだ」ではなく
   「照合できなかった」。時間をあけて取り直すまで判定を確定しない（ぴあの429と同じ型）。
""")

io.open('logs/newpool_%s_eplus.md' % TODAY, 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')
print('LOG_WRITTEN logs/newpool_%s_eplus.md' % TODAY)
