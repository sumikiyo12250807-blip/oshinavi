# 2026-09-05 e+から新着に投入（受付前ぶん）＋既存の直し

ソース＝イープラス（`/sf/word/` の未登録プール）。**確認用の表は作らず、新着タブの実物で見てもらう**方式。

機械ゲート＝`gate_eplus_slots.py` PASS（実ページの枠合計26／ビルド26・公演の取りこぼし0）／`reconcile_eplus.py --ids` **FAIL 0**／`check_badges` OK／`check_order.js` 並び順違反0／CRLF指紋 全行CRLF。

独立検証（別エージェントがゼロから再導出）＝**照合できた枠 27/27・取れなかったページ0**。公演日・会場・県すべて一致、締切も実ページの受付終了日と一致、重複・誤結合なし。指摘を受けた artist の直し2件は反映済み。


## 新着に入れた11件

| id | 出演 | 公演名 | 会場 | 公演日 | 枠 | 確認用 |
|---|---|---|---|---|---|---|
| 6935 | ARGYROS／The Monali.／スノウスマイル／TABOO／不明界隈　ほか | Planet CHILD Music presents 『四季彩プラネタリウム』 | BlackHole | 2026-10-15 | 1 | [ページ](https://eplus.jp/sf/detail/4589250001-P0030001P021001) |
| 6936 | Sick2 | Sick2 presents 『Sick2 BOX 2026-EAST-／-WEST-』 | 全国ツアー（赤羽ReNY alpha／OSAKA MUSE） | 2026-11-24 | 4 | [ページ](https://eplus.jp/sf/detail/4554220001-P0030001P021001) |
| 6937 | DAMILA／M.E.S.S／CHAOSS | DAMILA 主催BLOODY MARY SHOW-666- Episode5 鮮血に飾るHALLOWEEN | Live House 獅子王 | 2026-10-30 | 1 | [ページ](https://eplus.jp/sf/detail/4592800001-P0030001P021001) |
| 6938 | シンギュラリティ | シンギュラリティ TOUR2026 『PROVIDENCE』 | 全国ツアー（大阪RUIDO／HOLIDAY NEXT NAGOYA／札幌Crazy Monkey／大塚 Live House Hearts+） | 2026-10-07 | 5 | [ページ](https://eplus.jp/sf/detail/4589140001-P0030001P021001) |
| 6939 | L-MEME／tzkwym | MEME× tzkwym 「血湧き肉躍る-ハロウィン-」 | 東高円寺二万電圧 | 2026-10-28 | 1 | [ページ](https://eplus.jp/sf/detail/4590340001-P0030001P021001) |
| 6940 | wacci | wacci<東海大学 建学祭> | 東海大学湘南キャンパス総合体育館 | 2026-11-01 | 1 | [ページ](https://eplus.jp/sf/detail/4579740001-P0030001P021001) |
| 6941 | シンガーズハイ | シンガーズハイ<駿河台大学 駿輝祭> | 駿河台大学 体育館 | 2026-10-25 | 2 | [ページ](https://eplus.jp/sf/detail/4586820001-P0030001P021001) |
| 6942 | 野村康太 | 野村康太トークショー<駒沢女子大学 りんどう祭> | 駒沢学園 記念講堂 | 2026-10-11 | 2 | [ページ](https://eplus.jp/sf/detail/4589590001-P0030001P021001) |
| 6943 | 蛾と蝶 | 記念単独公演 楓生誕祭2026 | 高田馬場CLUB PHASE | 2026-10-15 | 2 | [ページ](https://eplus.jp/sf/detail/4588480001-P0030001P021001) |
| 6944 | サーカス／加藤実 | サーカス ～心をつなぐハーモニー～ 思い出の名曲コンサート | 新宿文化センター 大ホール | 2026-12-02 | 2 | [ページ](https://eplus.jp/sf/detail/4588660001-P0030001P021001) |
| 6945 | おとぎ話 / SCOOBIE DO | THE SUN ALSO RISES vol.423 -F.A.D 30th Anniversary- おとぎ話 / SCOOBIE DO | F.A.D YOKOHAMA | 2026-12-09 | 1 | [ページ](https://eplus.jp/sf/detail/4580350001-P0030001P021001) |

## 既存エントリの直し5件

| id | 公演名 | 直したこと |
|---|---|---|
| 6103 | 川崎学園祭 お笑いライブ!! | 締切 2026-09-06→2026-10-17（発売日のままだった）／e+のURL／artistを出演者3組に |
| 6295 | アロージャズオーケストラ | e+の先着一般発売枠（9/19 10:00〜11/27）が丸ごと抜けていたので追加／URL／正式名に |
| 6080 | 灼熱のマンボVS輝けるスイング! | 締切 2026-09-19→2027-01-09（発売日のままだった）／e+のURL／artistを出演者名に |
| 583 | MELANCHOLIC CIRCUS | 別アーティスト「サーカス」（加藤実）の東京12/2枠2つが混入していたので除去→愛知9/26の単独公演に戻した |
| 6939 | MEME× tzkwym 「血湧き肉躍る-ハロウィン-」 | artistを「L-MEME／tzkwym」に（既存 id6022/id6207 と同じ名前で探せるように） |

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


---

# 第2便＝e+の「受付中」ぶん（同じ日の午前）

候補180件 → 公演IDでDBに実在した122件を除外 → 58件をビルド → 49エントリ。
そのうち **公演が全部すでに載っていた6件は投入せず**、
**同じアーティストのツアーが既にある4件は新規を作らず既存に足りない枠だけ足し**、残りを新規で投入。

## 機械ゲートの結果（🚨2枚とも通さないと素通りする）

| ゲート | 結果 |
|---|---|
| `gate_eplus_slots` | **PASS**（エントリ49件・照合したURL184本） |
| `reconcile_eplus --ids`（48件・271枠） | 🚨 **FAIL 151件**（c-死枠114／a-締切>公演日16／b-締切ズレ8／b-発売日ズレ5／b-締切時刻ズレ4／h-時刻欠3／b-発売前化1） |
| 後始末＝FAILの枠133本を落とす | `reconcile_eplus` 再照合 **FAIL 0**（134枠） |
| `check_badges` / `check_order` / `check_dup_slots` | OK ／ 違反0 ／ **A0・B0・C0** |
| CRLF指紋 | 全行CRLF・LF単独0 |

🚨**`gate_eplus_slots` が PASS しても安心できない。**
e+のツアーは**個別の -P ページに販売窓を出さないことがある**のに、
`eplus_harvest.py build` は **base ページの窓を各公演にコピー**する。
ゲート側はそれを「実ページの枠 < ビルドの枠」の **NOTE で流していた**（33本）。
そのまま載せると**バッジを押しても買えないページに着く**ので、reconcile が弾いた分は落とした。

## 新着に入れた38件（id6948〜6985）

| id | 出演 | 公演名 | 会場 | 公演日 | 枠 | 確認用 |
|---|---|---|---|---|---|---|
| 6948 | cubrick | cubrick presents「二転三転」vol.110 | HOLIDAY SHINJUKU | 2026-09-17 | 1 | [ページ](https://eplus.jp/sf/detail/4580370001-P0030001P021001) |
| 6949 | ヤミテラ | ヤミテラ TOUR 2026 SUMMER 『九龍強襲』 | 全国ツアー（SECOND CRUTCH／graf） | 2026-09-11 | 3 | [ページ](https://eplus.jp/sf/detail/4551610001-P0030001P021001) |
| 6950 | ナナクロニクル | ナナクロニクル | 全国ツアー（名古屋JAMMIN’／OSAKA MUSE／赤羽ReNY alpha／Zepp Haneda(TOKYO)） | 2027-03-26 | 4 | [ページ](https://eplus.jp/sf/detail/3884970001-P0030050P021001) |
| 6951 | Project | Project U.D.M活動終了主催公演 「DAWN OF DYSTOPIA」 | EDGE ikebukuro | 2026-11-27 | 1 | [ページ](https://eplus.jp/sf/detail/4552290001-P0030001P021001) |
| 6952 | DAMILA | DAMILA ONE MAN LIVE BLOODY MARY SHOW-666- Episode 4 | Live House 獅子王 | 2026-09-06 | 1 | [ページ](https://eplus.jp/sf/detail/4554060001-P0030001P021001) |
| 6953 | YOU | YOU SOCK FESTIVAL | SPACE ODD | 2026-10-02 | 1 | [ページ](https://eplus.jp/sf/detail/4590160001-P0030001P021001) |
| 6954 | Home | Home Party Chanty Presents | 長野 LIVE HOUSE J | 2026-09-21 | 1 | [ページ](https://eplus.jp/sf/detail/4570530001-P0030001P021001) |
| 6955 | ホタル結成25周年&再結成10周年 | ホタル結成25周年&再結成10周年 2時間ドラマシリーズ 歌謡サスペンス激情 傑作選「鉛の雨に桜散る」 | EDGE ikebukuro | 2026-10-06 | 2 | [ページ](https://eplus.jp/sf/detail/4572100001-P0030001P021001) |
| 6956 | back | back on live FES 2026 能登半島災害復興支援 | 富山MAIRO/他 | 2026-09-22 | 1 | [ページ](https://eplus.jp/sf/detail/4562600001-P0030001P021001) |
| 6957 | 「血湧き肉躍る-番外編-」 | 「血湧き肉躍る-番外編-」 | graf | 2026-09-17 | 1 | [ページ](https://eplus.jp/sf/detail/4556740001-P0030001P021001) |
| 6958 | flumpool | flumpool 医療創生大学学園祭 | 医療創生大学 コンサートホール | 2026-10-25 | 1 | [ページ](https://eplus.jp/sf/detail/4519920001-P0030001P021001) |
| 6959 | 甲南女子大学 | 甲南女子大学 よつば祭 前田拳太郎 トークショー | 甲南女子大学 芦原講堂 | 2026-10-24 | 1 | [ページ](https://eplus.jp/sf/detail/4571310001-P0030001P021001) |
| 6960 | オーイシマサヨシ | オーイシマサヨシ<大分大学 蒼稜祭> | 大分大学 旦野原キャンパス 第一体育館 | 2026-11-01 | 2 | [ページ](https://eplus.jp/sf/detail/4572690001-P0030001P021001) |
| 6961 | 第3回 | 第3回 穂国祭ライブ ドミコ | 愛知大学(豊橋校舎)学生会館1F大ホール | 2026-10-30 | 1 | [ページ](https://eplus.jp/sf/detail/4580650001-P0030001P021001) |
| 6962 | FUNKY | FUNKY MONKEY BΛBY’S <香川大学 第47回香川大学医学部祭> | 香川大学 医学部体育館 | 2026-10-11 | 1 | [ページ](https://eplus.jp/sf/detail/4590240001-P0030001P021001) |
| 6963 | Japan | Japan Guitarist Team Live ～ ORIGIN ～ | 赤羽ReNY alpha | 2026-09-19 | 1 | [ページ](https://eplus.jp/sf/detail/4501290001-P0030001P021001) |
| 6964 | CRUSH | CRUSH OF MODE-ENDLESS SUMMER’26- | BIGCAT | 2026-09-06 | 1 | [ページ](https://eplus.jp/sf/detail/4527050001-P0030001P021001) |
| 6965 | 摩天楼オペラ | 摩天楼オペラ & NoGoD ⇒浦和ナルシス応援企画4『漆黒のシンフォニーat埼玉会館』 | 埼玉会館 小ホール | 2026-09-22 | 1 | [ページ](https://eplus.jp/sf/detail/4542980001-P0030001P021001) |
| 6966 | Voice | Voice Box 2026 朗読「FAUST」～光と闇の黙示録～時よ止まれ、汝は美しい! | J:COMホール八王子 | 2026-09-13 | 1 | [ページ](https://eplus.jp/sf/detail/3300420001-P0030016P021001) |
| 6967 | MUSIC | MUSIC YOKAJA Vol.1 | 全国ツアー（広島・Read／BEAT STATION） | 2026-10-25 | 2 | [ページ](https://eplus.jp/sf/detail/4594990001-P0030001P021001) |
| 6968 | Bunkamura | Bunkamura Production 2026 ミュージカル 「獅子 THE LION-BEAT」 | THEATER MILANO-Za | 2026-10-20 | 19 | [ページ](https://eplus.jp/sf/detail/3857440004-P0030033P021016) |
| 6969 | ジャズ&ラテン | ジャズ&ラテン フェスティバル アロージャズオーケストラ&見砂和照と東京キューバンボーイズ スペシャルゲスト渡辺真知子 | 梅田芸術劇場メインホール | 2027-01-14 | 1 | [ページ](https://eplus.jp/sf/detail/1525130001-P0030026P021001) |
| 6970 | 庄野真代 | 庄野真代 50th Anniversary Special Live ～DOMESTIC MAYO LINE 2026 | Billboard Live OSAKA | 2026-10-03 | 2 | [ページ](https://eplus.jp/sf/detail/0159790002-P0030022P021001) |
| 6971 | えんがわ音楽祭 | えんがわ音楽祭 ～水の音コンサート～メインコンサート | 洞川温泉ビジターセンター特設ステージ | 2026-09-14 | 1 | [ページ](https://eplus.jp/sf/detail/4582600001-P0030001P021001) |
| 6972 | ハナレグミ | ハナレグミ | 全国ツアー（昭和女子大学人見記念講堂／高崎芸術劇場 スタジオシアター／つくばカピオ／ビッグハート出雲 白のホール） | 2026-12-06 | 3 | [ページ](https://eplus.jp/sf/detail/0061060001-P0030201P021001) |
| 6973 | SWAN | SWAN -Ballet cross Reading- | 新国立劇場 中劇場 | 2026-09-09 | 3 | [ページ](https://eplus.jp/sf/detail/4545910001-P0030001P021007) |
| 6974 | 古舘伊知郎×南野陽子 | 古舘伊知郎×南野陽子 presents 昭和101年スーパーソングブックショウ! ～昭和のベストヒット・グラフィティー～ | 全国ツアー（パシフィコ横浜 国立大ホール／フェスティバルホール） | 2026-10-19 | 2 | [ページ](https://eplus.jp/sf/detail/4541560001-P0030001P021001) |
| 6975 | Hammer | Hammer Head Shark | 渋谷CLUB QUATTRO | 2026-09-11 | 1 | [ページ](https://eplus.jp/sf/detail/4457840001-P0030003P021001) |
| 6976 | VINTAGE | VINTAGE ROCK pre. スターゲイザー | KOENJI HIGH | 2026-09-25 | 1 | [ページ](https://eplus.jp/sf/detail/4582590001-P0030001P021001) |
| 6977 | ONE | ONE & ONLY FESTIVAL 2026 | GLION MUSEUM | 2026-09-13 | 2 | [ページ](https://eplus.jp/sf/detail/4377420001-P0030002P021003) |
| 6978 | [マンスリーヒカシュー2026] | [マンスリーヒカシュー2026] 9月編 退化する人間の朝食にセメントのような粉 | 吉祥寺Star Pine’s Cafe | 2026-10-07 | 2 | [ページ](https://eplus.jp/sf/detail/4531610001-P0030001P021001) |
| 6979 | a | a flood of circle | 全国ツアー（小倉FUSE／club SPOT／SRホール／Music Zoo KOBE 太陽と虎／福山Cable／Live House 浜松 窓枠／club SONIC iwaki／八戸ROXX／秋田クラブスウィンドル／高松DIME／奈良NEVERLAND／京都磔磔／札幌BESSIE HALL／旭川カジノドライブ／函館ARARA／金沢vanvanV4／新潟GOLDEN PIGS RED STAGE／長野 LIVE HOUSE J／仙台darwin／F.A.D YOKOHAMA／W studio RED／CLUB CHAOS／岡山ペパーランド／米子laughs／広島セカンド・クラッチ／FUKUOKA BEAT STATION／心斎橋BIGCAT／THE BOTTOM LINE／豊洲PIT／Output） | 2027-01-31 | 23 | [ページ](https://eplus.jp/sf/detail/0255560001-P0030814P021001) |
| 6980 | KANSAI | KANSAI LOVERS 2026 | 大阪城音楽堂 | 2026-09-26 | 1 | [ページ](https://eplus.jp/sf/detail/1596540001-P0030021P021001) |
| 6981 | red | red cloth 2man show climbgrow/Panorama Panama Town | 新宿 red cloth | 2026-09-25 | 1 | [ページ](https://eplus.jp/sf/detail/4553990001-P0030001P021001) |
| 6982 | Beyond | Beyond Music Festival 2026 | 全国ツアー（LINE CUBE SHIBUYA／服部緑地野外音楽堂） | 2026-10-25 | 2 | [ページ](https://eplus.jp/sf/detail/4158250001-P0030003P021001) |
| 6983 | TALK&LIVE | TALK&LIVE ザ・ゴールデンステージ produced by Japanet <第13回>五木ひろし | HAPPINESS ARENA | 2026-10-31 | 2 | [ページ](https://eplus.jp/sf/detail/4370560001-P0030007P021001) |
| 6984 | 石川さゆり | 石川さゆり | 全国ツアー（神戸国際会館 こくさいホール／三原市芸術文化センター ポポロ／川口リリア・フカガワみらいホール(メインホール)／森ノ宮ピロティホール） | 2027-01-10 | 3 | [ページ](https://eplus.jp/sf/detail/0012400001-P0030305P021001) |
| 6985 | 石川さゆりコンサート | 石川さゆりコンサート ～極上のアンサンブル～ | タクトホームこもれびGRAFAREホール メインH | 2026-11-15 | 2 | [ページ](https://eplus.jp/sf/detail/4567550001-P0030001P021001) |

## 既存ツアーに足した枠（新規エントリを作らなかった分）

| id | 公演名 | 足した枠 |
|---|---|---|
| 5879 | go!go!vanillas ／ go!go!vanillas | 枠合計 4本 |
| 5251 | セックスマシーン!! ／ セックスマシーン!! | 枠合計 15本 |
| 5784 | ORCALAND ／ ORCALAND | 枠合計 6本 |
| 5766 | EPO ／ EPO | 枠合計 5本 |
| 3892 | 夜の本気ダンス ／ 夜の本気ダンス | 枠合計 29本 |
| 1477 | セカンドバッカー ／ セカンドバッカー | 枠合計 5本 |
| 2325 | 栄喜 ／ 栄喜 | 枠合計 7本 |
| 4240 | リュックと添い寝ごはん ／ リュックと添い寝ごはん | 枠合計 2本 |
| 5762 | 水平線 ／ 水平線 | 枠合計 2本 |
| 579 | 二見颯一 ／ 二見颯一 | 枠合計 4本 |

## 投入しなかったもの（理由つき）

| 何 | 理由 |
|---|---|
| セカンドバッカー／栄喜／リュックと添い寝ごはん／ORCALAND／水平線 | **公演が全部すでに載っていた**（(県, M/D公演) の重なり100%） |
| New Acoustic Camp 2026 | `gate_eplus_slots` FAIL＝実ページに**まったく同じ文言の券種が2〜3行**あり、ビルドが1本に潰していた。券種違いが画面から消えるので**保留** |
| FAILした133枠 | -Pページに販売窓が無い（押しても買えない） |

## 🚨 この便で見つけた取りこぼし

**id5766 EPO の東京9/29**＝既存（ぴあ）は一般発売 **〜9/13 23:59** の1枠だけ。
e+ の実ページには **〜9/20 18:00** と **〜9/25 18:00** の2枠が生きていた。
＝**9/13を過ぎたら画面上は買えないのに、実際は9/25まで買えた**。この2枠を足した。

「公演が載っているか」だけ見ると見逃す型。**販売窓の終わりまで比べる**こと。

## 🚨 url の焼き込みで踏んだ罠

**id5784 ORCALAND** の ぴあ由来ラベル（〜9/10 **23:59**）に e+ の -P URL を焼いたら、
実ページの締切（**18:00**）と食い違って `[b-締切時刻ズレ]` で弾かれた。**4本とも外した**。
＝**url の焼き込みは「同じ売り場から取ったラベル」にだけ**。他社URLを付けると押した先の締切が変わる。

