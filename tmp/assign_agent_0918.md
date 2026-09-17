# 新着95件 ジャンル振り分けの独立チェック（2026-09-18）

親エージェントの判定案は見ずに、`tools/build_pia_entries.py` の `genre_from_subcat()` を
実際に呼んでゼロから導出した。ネットアクセスは一切していない。

## 0. まとめ

- 95件すべてが**機械で一意に決まった**（`genre_from_subcat()` が `None` を返した件＝0件／
  名前ベースfallback `genre_of()` に落ちた件＝0件）。
- 判定経路の内訳
  - `PIA_GENRE_MAP` にサブカテゴリがそのまま載っていた（MAP_EXACT）… **65件**
  - 大分類フォールバック `PIA_CAT_FALLBACK`（スポーツ→sports 17件／クラシック→classic 11件）… **28件**
  - 「演歌・邦楽」の分岐（`_dento_stage`→dento／`_hogaku`→hougaku／どちらも無ければenka）… **2件**
  - 「祭り・花火大会」の分岐に入った件 … 0件
  - 部分一致ループに落ちた件 … 0件
- ジャンル分布
  sports 24 / jpop 23 / classic 13（うち2件は classic+engeki）/ owarai 6 /
  engeki 4 / talkshow 4 / aisatsu 4 / musicetc 4 / kids 4 / musical 2 / art 2 / enka 2 /
  movie 1 / dento 1 / fanevent 1
- `_piaSub` が空の行は**ゼロ**。
- `_piaSub` が「海外ROCK・POPS」の行は**ゼロ**＝**kpop読み替えの対象は今回なし**
  （「民族音楽」もゼロ）。ただし J-POP・ROCK に入っている中に海外グループ疑いが1件あり（後述 ⚠️E）。
- それでも 🚨 **機械に写すだけでは安心できない件が 13件**ある（第2章）。

---

## 1. id → ジャンル 対応表（95件・タブ区切り）

列は `id / ぴあ大分類 / ぴあサブ（_piaSub後半）/ 主ジャンル / 追加ジャンル / 判定経路`

```
id7558	映画	映画その他	movie		MAP_EXACT
id8172	音楽	演歌・邦楽	enka		邦楽分岐
id8351	音楽	J-POP・ROCK	jpop		MAP_EXACT
id8385	音楽	演歌・邦楽	enka		邦楽分岐
id8693	演劇	ミュージカル・ショー	musical		MAP_EXACT
id8698	演劇	演劇	engeki		MAP_EXACT
id8765	スポーツ	スポーツその他	sports		MAP_EXACT
id8770	スポーツ	ソフトボール	sports		大分類フォールバック
id8790	スポーツ	スポーツその他	sports		MAP_EXACT
id9859	クラシック	オーケストラ	classic		大分類フォールバック
id10429	音楽	音楽その他	musicetc		MAP_EXACT
id10430	音楽	J-POP・ROCK	jpop		MAP_EXACT
id10431	音楽	J-POP・ROCK	jpop		MAP_EXACT
id10439	音楽	J-POP・ROCK	jpop		MAP_EXACT
id11058	音楽	音楽その他	musicetc		MAP_EXACT
id11060	音楽	J-POP・ROCK	jpop		MAP_EXACT
id11061	音楽	J-POP・ROCK	jpop		MAP_EXACT
id11062	音楽	J-POP・ROCK	jpop		MAP_EXACT
id11066	音楽	J-POP・ROCK	jpop		MAP_EXACT
id11068	音楽	J-POP・ROCK	jpop		MAP_EXACT
id11069	音楽	J-POP・ROCK	jpop		MAP_EXACT
id11071	音楽	J-POP・ROCK	jpop		MAP_EXACT
id11073	音楽	J-POP・ROCK	jpop		MAP_EXACT
id11074	音楽	J-POP・ROCK	jpop		MAP_EXACT
id11077	演劇	ミュージカル・ショー	musical		MAP_EXACT
id11080	音楽	J-POP・ROCK	jpop		MAP_EXACT
id11082	音楽	J-POP・ROCK	jpop		MAP_EXACT
id11083	音楽	J-POP・ROCK	jpop		MAP_EXACT
id11085	音楽	J-POP・ROCK	jpop		MAP_EXACT
id11087	音楽	J-POP・ROCK	jpop		MAP_EXACT
id11088	音楽	J-POP・ROCK	jpop		MAP_EXACT
id11089	音楽	J-POP・ROCK	jpop		MAP_EXACT
id11090	演劇	寄席・お笑い	owarai		MAP_EXACT
id11092	演劇	寄席・お笑い	owarai		MAP_EXACT
id11093	演劇	バレエ・ダンス	classic	engeki	MAP_EXACT
id11095	演劇	朗読・リーディング	engeki		MAP_EXACT
id11096	演劇	演劇	engeki		MAP_EXACT
id11097	演劇	寄席・お笑い	owarai		MAP_EXACT
id11098	演劇	演劇	engeki		MAP_EXACT
id11099	演劇	歌舞伎・古典芸能	dento		MAP_EXACT
id11100	演劇	寄席・お笑い	owarai		MAP_EXACT
id11101	演劇	バレエ・ダンス	classic	engeki	MAP_EXACT
id11102	演劇	寄席・お笑い	owarai		MAP_EXACT
id11103	演劇	寄席・お笑い	owarai		MAP_EXACT
id11104	スポーツ	サッカー	sports		大分類フォールバック
id11105	スポーツ	サッカー	sports		大分類フォールバック
id11106	スポーツ	サッカー	sports		大分類フォールバック
id11108	スポーツ	スポーツその他	sports		MAP_EXACT
id11110	スポーツ	スポーツその他	sports		MAP_EXACT
id11111	スポーツ	プロレス	sports		大分類フォールバック
id11112	スポーツ	プロレス	sports		大分類フォールバック
id11114	スポーツ	スポーツその他	sports		MAP_EXACT
id11115	スポーツ	ラグビー	sports		大分類フォールバック
id11116	スポーツ	サッカー	sports		大分類フォールバック
id11117	スポーツ	サッカー	sports		大分類フォールバック
id11118	スポーツ	サッカー	sports		大分類フォールバック
id11119	スポーツ	サッカー	sports		大分類フォールバック
id11120	スポーツ	サッカー	sports		大分類フォールバック
id11122	スポーツ	野球	sports		大分類フォールバック
id11123	スポーツ	野球	sports		大分類フォールバック
id11125	スポーツ	ラグビー	sports		大分類フォールバック
id11127	スポーツ	スポーツその他	sports		MAP_EXACT
id11128	映画	舞台挨拶	aisatsu		MAP_EXACT
id11129	映画	舞台挨拶	aisatsu		MAP_EXACT
id11130	映画	舞台挨拶	aisatsu		MAP_EXACT
id11131	映画	舞台挨拶	aisatsu		MAP_EXACT
id11132	アート	アート	art		MAP_EXACT
id11133	イベント	講演会・トークショー	talkshow		MAP_EXACT
id11134	イベント	講演会・トークショー	talkshow		MAP_EXACT
id11137	イベント	イベントその他	musicetc		MAP_EXACT
id11138	イベント	イベントその他	musicetc		MAP_EXACT
id11139	イベント	博覧会・展示会・見本市	art		MAP_EXACT
id11140	イベント	講演会・トークショー	talkshow		MAP_EXACT
id11142	イベント	ショー・ファンイベント	fanevent		MAP_EXACT
id11143	クラシック	器楽・室内楽	classic		大分類フォールバック
id11144	クラシック	吹奏楽	classic		大分類フォールバック
id11145	クラシック	器楽・室内楽	classic		大分類フォールバック
id11146	クラシック	オーケストラ	classic		大分類フォールバック
id11148	クラシック	器楽・室内楽	classic		大分類フォールバック
id11149	クラシック	器楽・室内楽	classic		大分類フォールバック
id11150	クラシック	器楽・室内楽	classic		大分類フォールバック
id11151	クラシック	器楽・室内楽	classic		大分類フォールバック
id11152	音楽	J-POP・ROCK	jpop		MAP_EXACT
id11153	音楽	J-POP・ROCK	jpop		MAP_EXACT
id11154	イベント	講演会・トークショー	talkshow		MAP_EXACT
id11155	スポーツ	スポーツその他	sports		MAP_EXACT
id11156	スポーツ	サッカー	sports		大分類フォールバック
id11157	スポーツ	サッカー	sports		大分類フォールバック
id11158	イベント	スクール・レジャー	kids		MAP_EXACT
id11159	イベント	スクール・レジャー	kids		MAP_EXACT
id11160	イベント	スクール・レジャー	kids		MAP_EXACT
id11161	イベント	スクール・レジャー	kids		MAP_EXACT
id11162	クラシック	器楽・室内楽	classic		大分類フォールバック
id11163	クラシック	器楽・室内楽	classic		大分類フォールバック
id11164	音楽	J-POP・ROCK	jpop		MAP_EXACT
```

---

## 2. 🚨 迷う件・相談したい件（13件）

「機械の答え」は上表のとおり動かさない前提で、**実態と食い違っていそうな件**を挙げる。
2026-08-31の「アークラ大サーカス」（ぴあ＝イベントその他／実はクラフトフェア／登録は engeki）
と同じ型の事故を防ぐための洗い出し。

### ⚠️A id11137・id11138「真アギト展（名古屋会場）」／名古屋PARCO 西館8F PARCO HALL
- ぴあ＝**イベント/イベントその他** → 機械の答えは **musicetc（表示「その他」）**
- 引っかかり：名前も会場も**完全に展示会**。ぴあ自身が同じ「展」を id11139『白隠さんの禅』京都展では
  「博覧会・展示会・見本市」＝**art** に入れている。同種のものが art と その他 に割れる。
- ⚠️相談：ぴあ通り musicetc に置くか、実態どおり art に寄せるか。
  （ルール1に厳密なら musicetc。ただし「展示会が その他タブ」は利用者に見つけてもらえない）
- 補足：2件は同じ展示の「期間内フリー券（11/4以降）」と「日時指定券（10/31〜11/3）」＝
  枠違いなのでエントリは畳まない。

### ⚠️B id11158・id11159・id11160・id11161「銀河特急ミルキー☆サブウェイ × TOWER RECORDS CAFE」（大阪/渋谷/名古屋栄/福岡）
- ぴあ＝**イベント/スクール・レジャー** → 機械の答えは **kids**
- 引っかかり：実態は**タワレコカフェのコラボカフェ**。`PIA_GENRE_MAP` の
  「スクール・レジャー→kids」は「わんにゃん夜ふかし縁日」で確認したマッピングで、
  コラボカフェが子供向けタブに4件並ぶのは実態とズレる。
- ⚠️相談：kids のままでよいか。fanevent（ショー・ファンイベント）の方が近い気がする。
  マッピング自体を見直す話になるので、あたし（サブエージェント）では決めない。

### ⚠️C id11101「『BDC DANCE LAB 2026』」／BROADWAY DANCE CENTER Studio 2・2026-12-06
- ぴあ＝**演劇/バレエ・ダンス** → 機械の答えは **classic ＋ engeki**
- 引っかかり：会場は BROADWAY DANCE CENTER のスタジオ＝**ストリート／ジャズダンス系のスタジオ発表会**。
  `PIA_GENRE_MAP` のコメントは「バレエ=classic+engeki両方方式」と**バレエ前提**で書かれているのに、
  ぴあの同じサブには非バレエのダンスも入る。**クラシック音楽タブに載る**のは違和感。
- ⚠️相談：バレエ以外のダンスも classic に入れ続けるか。
  （同じサブの id11093 キーウ・クラシック・バレエは classic+engeki で問題なし）

### ⚠️D id11110「コズエン Maid Cafe ～戦う天使たち、今日はメイドです～」／ベルサール新宿南口・2026-11-07
- ぴあ＝**スポーツ/スポーツその他** → 機械の答えは **sports**
- 引っかかり：名前からして**メイドカフェ形式のファンイベント**で、試合ではない。
  ぴあが所属団体の都合でスポーツ枠に置いているだけに見える。**アークラ大サーカス型**の食い違い候補。
- ⚠️相談：sports のままか fanevent か。

### ⚠️E id11083「MORE STAR」／ヒューリックホール東京・2026-09-24
- ぴあ＝**音楽/J-POP・ROCK** → 機械の答えは **jpop**
- 引っかかり：グループ名の作り（英語2語）が海外（韓国）アイドルの型に見える。
  ただし **kpop読み替えの条件は「_piaSubが海外ROCK・POPS」**であって、この件は J-POP・ROCK なので
  例外は発動しない＝機械的には jpop で正しい。
- ⚠️相談：日本のグループか確認が要る（韓国グループなら kpop 読み替えの前提そのものが
  「ぴあが海外扱いしていない」ので、ルールの穴になる）。**あたしはネットを見ていないので断定しない。**

### ⚠️F id8172「瑛人×SANIMYOK PUAN Live2026」／祇園JTN・2026-09-28
- ぴあ＝**音楽/演歌・邦楽** → 邦楽分岐で `_dento_stage` も `_hogaku` も当たらず、
  サブに「演歌」を含むので機械の答えは **enka**
- 引っかかり：「瑛人」が「香水」のシンガーソングライターだとすると**J-POP**で、
  演歌タブに入るのは実態とかなりズレる。会場もライブハウス。
- ⚠️相談：ぴあの区分ミスを疑う件。enka のまま出すと演歌を探している人のノイズになる。

### ⚠️G id8385「江上遥オータムソロコンサート」／渋谷美竹サロン・2026-10-28
- ぴあ＝**音楽/演歌・邦楽** → 機械の答えは **enka**
- 引っかかり：公演名に和楽器の語が1つも出ないので `HOGAKU_RE` を素通りして enka に落ちた。
  **もし箏・尺八などの和楽器奏者なら hougaku が正**で、これは memory に何度も出ている
  「琵琶絵巻」「和洋楽器ユニット」「東儀秀樹」と**同じ型の取りこぼし**（名前に語が出ない）。
- ⚠️相談：奏者の楽器を1回確かめたい。

### ⚠️H id11080「南佳孝 バレンタインディナー&ライブ2027」／神戸ポートピアホテル 偕楽の間・2027-02-14
- ぴあ＝**音楽/J-POP・ROCK** → 機械の答えは **jpop**
- 引っかかり：会場が**ホテルの宴会場**で名前も「ディナー&ライブ」＝実態はディナーショー。
  ぴあには「ディナーショー」サブ（→dinnershow）があるのに、この公演だけ J-POP・ROCK に置いている。
- ⚠️相談：ぴあ通り jpop か、dinnershow に寄せるか。

### ⚠️I id8765「第20回アジア競技大会／応援Plus<応援グッズ>」・id8790「第5回アジアパラ競技大会／応援Plus<応援グッズ>」／名古屋市内 グッズ受取窓口
- ぴあ＝**スポーツ/スポーツその他** → 機械の答えは **sports**
- 引っかかり：**会場が「グッズ受取窓口」＝観る公演ではなく応援グッズの引換**。
  ジャンル以前に「これは掲載対象のチケットか」の話になる。カウントダウンの意味も薄い。
- ⚠️相談：ジャンルは sports でよいが、**そもそも載せるかどうか**を決めてほしい。

### ⚠️J id11114「STARDOM NEW YEAR DREAM 2027 ～サイン会～」／横浜武道館・2027-01-02
- ぴあ＝**スポーツ/スポーツその他** → 機械の答えは **sports**
- 引っかかり：試合ではなく**サイン会**。ただし STARDOM は女子プロレスなので sports タブでも
  探す人の期待とはズレない。⚠️は弱め。fanevent の方が正確ではある。

### ⚠️K id11127「ONE ASIA WORLD オープニングセレモニー」／ONE ASIA CHAMPIONS ROAD（久屋大通公園）・2026-09-19
- ぴあ＝**スポーツ/スポーツその他** → **sports**
- 引っかかり：**式典**であって競技ではない。⚠️は弱め（大会付帯なので sports で通ると思う）。

### ⚠️L id7558「Tommy february6・Tommy heavenly6 豪華アナログBOX発売記念!」／ローソン・ユナイテッドシネマ STYLE-S ほか全国ツアー・2026-10-31
- ぴあ＝**映画/映画その他** → 機械の答えは **movie**
- 引っかかり：中身は**音楽（川瀬智子の企画）**で、映画館を使うイベント。
  映画を探している人には「映画その他」でも、音楽ファンには movie タブでは見つけられない。
- ⚠️相談：ぴあ通り movie（大分類のタブがあるのでそこへ）で押し切るのが前例どおりだと思うが、一応。

### ⚠️M id11122・id11123「東京ヤクルトスワローズ 対 中日ドラゴンズ 2026/10月開催」／神宮球場・2026-10-03
- ジャンルは両方 **sports** で疑いなし。ジャンル外の指摘＝
  id11123 は同じ試合の **≪車椅子席≫** で、ホーム/アウェイの別ではなく**席種違い**。
  「同じ試合を畳まない」ルール（ホーム/アウェイ）とは別の話なので、**2エントリで持つのか
  1エントリの枠違いにするのか**だけ確認したい。

---

## 3. 名前で間違えやすい罠（機械の答えが正しいので**触らないこと**の確認）

ルール2（名前の語で中身を決めない）に照らして、**あえて機械どおりにした**件。

| id | 公演名 | 名前が誘う先 | ぴあ＝正しい答え |
|---|---|---|---|
| id11164 | ROCK or LIVE! -ロックお笑い部- 東京編 | 「お笑い部」→owarai | 音楽/J-POP・ROCK → **jpop** |
| id11060 | GASOLINE／**柳家**睦とラットボーンズ／Oi-SKALL MATES | 「柳家」→落語→owarai | 音楽/J-POP・ROCK → **jpop** |
| id11133 | いとうせいこう×奥泉光「文芸**漫談**シーズン8」 | 「漫談」→owarai | イベント/講演会・トークショー → **talkshow** |
| id11134 | 鬼小十郎**まつり**後夜祭2026 森川智之トークライブ | 「まつり」→fes/hanabi | イベント/講演会・トークショー → **talkshow**（「祭り・花火大会」サブではないので花火分岐に入らない） |
| id11154 | 横浜DeNAベイスターズ **vs** 阪神タイガース 爆笑トークバトル2027 | 「vs」→sports | イベント/講演会・トークショー → **talkshow** |
| id11096 | **大衆演劇**EXPO 第三回浅草大宴会 | 「EXPO」→art/博覧会 | 演劇/演劇 → **engeki** |
| id11077 | 極上のミュージカル**コンサート** in 各務原 | 「コンサート」→classic/jpop | 演劇/ミュージカル・ショー → **musical** |
| id11061 | 【当日引換券】**KYOMAF** MUSIC LIVE 2026 | アニメイベント→anime | 音楽/J-POP・ROCK → **jpop** |
| id11108 | ALL JAPAN CHEER **DANCE** CHAMPIONSHIP 2026 | 「ダンス」→classic+engeki | スポーツ/スポーツその他 → **sports** |
| id11155 | 大和地所スペシャル 超プロ野球ULTRA | 「野球」→野球サブ | スポーツ/スポーツその他 → **sports**（同じ sports なので実害なし） |
| id11099 | 土佐の「こじゃんと」**能楽**プロジェクト | — | 演劇/歌舞伎・古典芸能 → **dento**（`_dento_stage` の線引きとも一致） |

---

## 4. 仕組みの気づき（ジャンルの正の側の話）

- 🚨 **クラシック大分類のサブカテゴリは `PIA_GENRE_MAP` に1件も載っていない。**
  今回の11件（オーケストラ／器楽・室内楽／吹奏楽）は全部 `PIA_CAT_FALLBACK['クラシック']` で
  classic に落ちている。結果は同じなので実害はないが、**「なぜ classic か」が機械の記録として残らない**。
  `PIA_GENRE_CD` には8種（オーケストラ／器楽・室内楽／オペラ・声楽／吹奏楽／合唱／
  クラシック邦楽／フェスティバル・ガラコンサート／クラシックその他）が定義済みなので、
  対応表に書き足しておくと後から読みやすい。
  ただし **「クラシック邦楽」だけは MAP に足してはいけない**（先に邦楽分岐で hougaku に行く形が正で、
  MAP に classic と書くと分岐より後ろなので害はないが、読む人が混乱する）。
- 🚨 同じく **スポーツ大分類のサブも「スポーツその他」以外が MAP に無く**、17件が大分類フォールバック
  （サッカー10／野球2／ラグビー2／プロレス2／ソフトボール1）。
  こちらも行き先は sports で一致するので実害なし。
- 「フェスティバル」は音楽(0100111)・演劇(0200107)・クラシック(0700107)の3か所にあり、
  MAP のキーは `'フェスティバル'` の1本。クラシックの「フェスティバル・ガラコンサート」は
  部分一致ループで `'フェスティバル'` に当たって **fes** になる。今回は該当なしだが、
  ガラコンサートが fes に落ちるのは事故になりうる（要注意メモ）。

---

## 5. 使った手順

1. `tmp/assign_question_0918.txt` をタブ区切りで読み、`id / _piaSub / 公演名 / 会場 / 公演日` に分解（95行）。
2. `_piaSub` を最初の `/` で割って `cat`（大分類）と `sub`（サブカテゴリ）にした。
3. `importlib.util.spec_from_file_location` で `tools/build_pia_entries.py` をそのまま読み込み、
   **`genre_from_subcat(cat, sub, name)` を95回実際に呼んだ**。
4. あわせて判定経路を自分で再現して記録した
   （`'邦楽' in sub` / `'花火' in sub` / `sub in PIA_GENRE_MAP` / 部分一致ループ / `PIA_CAT_FALLBACK`）。
5. `None` が返った件には `genre_of(name)`（名前ベースfallback）も出すようにしたが、**0件だった**。
6. ネットアクセスは一切していない。実態の裏取りが要る件は第2章に ⚠️ で出した。

スクリプト：`%TEMP%\claude\...\scratchpad\check_genre_0918.py`（一時ファイル・プロジェクト外）
