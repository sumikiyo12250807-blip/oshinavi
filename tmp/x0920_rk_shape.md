# 楽天：買える行があるのに飛ばされた9ページの「形」（2026-09-20 朝・読み取りのみ）

⚠️ 依頼にあった「パース漏れ」は**違った**。9ページとも `rakuten_harvest.parse_perfs()` は今日かけると
**全公演を正しく読めている**（下の表の「parse_perfs」列）。落ちているのは組み立て側の別の場所。

## 真因＝枠づくりが `r['windows']`（ページ上部の販売枠）しか見ていない

`tools/build_rakuten_entries.py` の枠づくりは `for w in r['windows']:` の中だけで `tickets` を作る（200行目あたり）。
この9ページは **windows が空か、終わった枠しか無い**。だから tickets が0本になり、`return None, '買える枠なし'`（263行目）で落ちる。

ところが**公演カード1枚ずつが、いま生きている販売期間を持っている**（`data-date` の min_start_on / max_end_on）。
`parse_perfs()` はそれを `sale_start` / `sale_end` として既に返している＝**材料はもう手元にある**。

> 例（関東大学バスケ2巡目・1公演目）: sale_start 2026-09-18 12:00 ／ sale_end 2026-10-24 23:59 ／ status 受付中

楽天のAJAX（`tools/rakuten_perf_status.py` が使う widget API）でも、同じ公演が「購入する」で返る＝買えるのは事実。

## 一覧

| ページ | 公演カード | parse_perfs | 会場が取れた | windows | 生きた窓 | カードの締切が今日以降 | AJAXで購入可 |
|---|---|---|---|---|---|---|---|
| 関東大学バスケ2巡目 | 34枚(PC 17) | 17 | 17 | 0 | 0 | 有 | 17行 |
| 乃木坂46 42ndSGアンダーライブ | 2枚(PC 1) | 1 | 1 | 0 | 0 | 有 | 1行 |
| n.SSign 全国 | 24枚(PC 12) | 12 | 12 | 2 | 0 | 有 | 4行 |
| コドモパーティーIII | 8枚(PC 4) | 4 | 4 | 1 | 0 | 有 | 4行 |
| @JAM the Field vol.30 | 4枚(PC 2) | 2 | 2 | 0 | 0 | 有 | 2行 |
| 高中正義 全国 | 20枚(PC 18) | 10 | 10 | 4 | 0 | 有 | 3行 |
| LOVEBITES 全国 | 6枚(PC 10) | 3 | 3 | 1 | 0 | 有 | 1行 |
| スタンレーレディス | 8枚(PC 4) | 4 | 4 | 0 | 0 | 有 | 4行 |
| 河鍋暁斎の世界 兵庫 | 2枚(PC 1) | 1 | 1 | 2 | 1 | 有 | 1行 |

## 形は何種類か＝**3種類（原因も3つ）**

- **windows空**（4件）: 関東大学バスケ2巡目／乃木坂46 42ndSGアンダーライブ／@JAM the Field vol.30／スタンレーレディス
- **windows全部終了**（4件）: n.SSign 全国／コドモパーティーIII／高中正義 全国／LOVEBITES 全国
- **windowsに生きた枠あり**（1件）: 河鍋暁斎の世界 兵庫

公演カードの作りは3種類とも同じ（下の生HTML）。違うのは「ページ上部の販売枠」の側だけ。

- **①windows空／②windows全部終了（計8件）** ＝ 直し方は1つで足りる。
  windows から作った tickets が0本になったら、**公演カードの sale_start / sale_end で枠を作る**。
  材料は `parse_perfs()` の戻り値にもう入っている。
- **③河鍋暁斎の世界［兵庫］だけ別の原因＝全角コロン**。
  販売期間が `2026/07/11(土) 00：00 〜 2026/09/23(水) 17：00` と**全角の「：」**で書かれていて、
  `win_start_iso()` / `win_end_iso()` が `(None, None)` を返す → `if not sd: continue` で枠が1本も作られない。
  実測＝`win_start_iso('… 00：00 …')` は None、半角に直すと `('2026-07-11','00:00')`。
  🚨これは**1文字の正規化で直る**（timming を NFKC 正規化するか `：`→`:` に置換）。
  候補25ページ中この1ページ・2枠だけだが、**同じ書き方のページは今後も来る**。

## 依頼の1〜3への答え

**1. 公演1行を包む要素** ＝ 既知の形のまま。`<div class='performance active' data-date='{"min_start_on":…,"max_end_on":…}'>` の中に
`<div class='column-1〜6'>`（1=券種名 / 6=公演日 / 2=公演時間 / 3=エリア / 4=会場）。PC側だけ `data-perf='NN'` を持ち、
モバイル側の同じカードは持たない（カード数がPCの2倍に見えるのはこのため）。`perf_NN` は購入ボタンのプレースホルダの class。

**2. `data-event-json`** ＝ **9ページとも無い**（外部JSON型ではない）。だから新型の読み口は関係ない。

**3. 公演日・会場・都道府県・販売期間** ＝ 全部カードから機械で取れる。
日付=column-6 の「2026年9月23日」／会場=column-4 ／エリア=column-3 ／開演=column-2 の「開演 HH:MM」／
販売期間=`data-date` の `min_start_on`・`max_end_on`（ISO）。`parse_perfs()` の戻り値がそのまま使える。
🚨`max_end_on` が空のカードは締切が書かれていない枠＝`saleEndUnknown` にすること。
ただし**今回の9ページでは、公演行54のうち締切が空のものは0**だった（全部に締切が入っている）。
＝この9件を救うのに `saleEndUnknown` は要らない。他のページ向けの備えとして残す話。

## 1番（関東大学バスケットボールリーグ戦2巡目）の詳細＝いちばん実害が大きい

- URL: https://ticket.rakuten.co.jp/sports/basketball/rt3abb0/
- 公演カード 34枚（PC 17枚）・`parse_perfs` は 17公演を返す・会場も 17件そろっている
- **windows は空**（ページ上部に販売枠の欄が無い）→ いまの組み立てでは tickets が0本 → 「買える枠なし」
- AJAX（ecd=RT3ABB0 / eid=1107754）では 17行が「購入する」
- カードから取れる販売期間の例（先頭3公演）:
  - 2026-09-23 00:00 全国／各会場 ｜ 締切 2026-10-24 23:59 ｜ buyable
  - 2026-09-23 11:00 東京都／日本大学 アスレティックセンター八幡山 ｜ 締切 2026-09-22 23:59 ｜ buyable
  - 2026-09-23 14:30 東京都／明治大学 和泉キャンパス ｜ 締切 2026-09-22 23:59 ｜ buyable
- 登録は「1巡目」(id8384)だけ＝**2巡目は丸ごと未登録**

### 公演1行分の生HTML（このグループの代表・先頭だけ）

```html
<div class='performance-msg' style='justify-content: center;color: #000;padding: 10px; text-align: center;'> このイベントの販売は終了しました </div> <div class='performance active' data-date='{"min_start_on":"2026-09-18T12:00:00","max_start_on":"2026-09-18T12:00:00","min_end_on":"2026-10-24T23:59:59","max_end_on":"2026-10-24T23:59:59"}'><div class='column-1'>リーグ戦シーズンシート(自由席) 9/23(水)〜10/25(日)</div><div class='column-6'>2026年 09月 23日 (水) 〜 10月 25日 (日)</div><div class='column-2'>開演 00:00</div><div class='column-3'>全国</div><div class='column-4'>各会場</div><div class='column-5 performance_btn perf_1' data-perf='1'>.
```

素材＝tmp/x0920_rk_shape.json（9ページ分の計測）／tmp/x0920_rk18_status.json（AJAXの公演行）