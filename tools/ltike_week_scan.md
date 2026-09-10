# ローチケの「その週に発売開始する公演」を総ざらいする手順（2026-09-10 確立）

## なぜ要るか

ユーザー（2026-09-10）＝
> 「昨日**藤井風が oshinavi.jp に無かった**件ね。大物で、みんなが行きたそうなコンサートは
>  うちにないものがないか、それを探してほしい」

藤井風は **e+の独占**だった。ぴあ・楽天だけ見ていても引っかからない。
ローチケは**3つめの売り場**で、ここにしか無い大物がいる。

## 🚨 ローチケは WebFetch/curl が全滅。**実ブラウザで開いて画面から読む**

（[[reference_ltike_machine_unreachable]]）。だからこれは「ツール」ではなく**手順書**。

## 入口＝検索URLが日付で叩ける（2026-09-10 発見）

```
https://l-tike.com/search/?keyword=&tig=110&sdate_from=20260907&sdate_to=20260913&rcmflg=1&stype=04
                                    ^ジャンル      ^発売日の範囲(YYYYMMDD)          ^今週発売
```
`tig=110` … コンサート・ライブ
`sdate_from` / `sdate_to` … **発売日**の範囲。ここを変えれば任意の週を出せる
`stype=04` … 今週発売

実測（2026-09-07〜09-13）＝**270件**。20件ずつのページ送り。

## 1ページの読み取り（ブラウザのJSで）

```js
const t = document.body.innerText;
const parts = t.split(/\nコンサート\n/).slice(1);
const rows = parts.map(p => ({
  name: (p.split('\n')[0] || '').trim(),
  d:   (p.match(/公演日：\n(.+)/) || [])[1] || '',
  v:   (p.match(/会場：\n(.+)/) || [])[1] || '',
  st:  ((p.match(/受付期間\n([\s\S]*?)\n(20\d{2}\/)/) || [])[1] || '').replace(/\n/g,' / ').trim(),
  per: (p.match(/(20\d{2}\/\d{1,2}\/\d{1,2}\([^)]*\) \d{1,2}:\d{2} ～ 20\d{2}\/\d{1,2}\/\d{1,2}\([^)]*\) \d{1,2}:\d{2})/) || [])[1] || ''
}));
```
取れるもの＝**アーティスト名／公演日／会場／販売方法（先着・抽選）／券種／状態／受付期間**。
🚨**「予定枚数終了」もそのまま書いてある**＝売り切れの区別まで取れる。

## 突き合わせ

読んだ結果を JSON に落として `python tools/check_big_artists.py <json>` に渡す。
🚨**名前の部分一致だけで「載っていない」と言わない**＝
   京まふ＝KYOMAF、XMF＝Xnterstellar、=LOVE＝STARフェス のように**表記が違うだけ**で載っていることがある。
   ぴあで総ざらい（`tools/pia_kw_search.py`）してから **eventCd で突き合わせる**のが確実。

## トップページの「注目」欄について（2026-09-10 実測）

`https://l-tike.com/concert/` には
「注目チケット／先行受付／**今週末一般発売開始**／発売中・公演間近／配信／**注目のアーティスト**」がある。
🚨**「注目のアーティスト」はチケット一覧ではなくアーティスト名鑑**＝
   名前があっても券は無いことがある（King Gnu はローチケの検索でも0件だった）。
   **券のある一覧（上の検索URL）を正とする。**

## 🆕 エントリを作るところまで（2026-09-10 実測・3件で確立）

検索結果だけでは足りない。**「詳細はこちら」の先まで開く**と、エントリに要るものが全部そろう。

### ① ボタンの `data-*` を吸う（クリック不要）
```js
[...document.querySelectorAll('a.entryBtn[data-lcode]')].map(a => {
  const d = a.dataset;
  return [d.prfname, d.prfdate, d.basevenuename, d.lcode, d.pfkeys,
          d.schduleno, d.sendcarriercode, d.basevenuecd, d.rcptypename].join('|');
}).join('
')
```
🚨**JSの戻り値に `?a=b` 形の文字列を混ぜると拡張がブロックする**（Cookie/query string data）。
**値だけ返して、URLの組み立てはPython側でやる**。

### ② URLを組む
`https://l-tike.com/order/?gLcode=<lcode>&gPfKey=<pfkeys>&gEntryMthd=<rcptypename>&gScheduleNo=<schduleno>&gCarrierCd=<sendcarriercode>&gPfName=<prfnameをURLエンコード>&gBaseVenueCd=<basevenuecd>`

🚨🚨**`gEntryMthd` を `02` で固定しない＝`data-rcptypename` の値**。
　2026-09-10に `02` 固定で組んで **404** を踏んだ（別府葉子・野田かつひこは `01`）。
🚨**枠が複数ある公演は `schduleno` が枠ごとに違う**＝**枠ごとに別URL**を `ticket.url` に入れる。
　（REVERSE EDGE 2＝プレリク `sn=1`／一般発売 `sn=2`）
⚠️**組んだら必ず開いて200を確かめる**。ローチケは発売直前まで個別ページが立たないことがある。

### ③ 詳細ページから読むもの
**正式タイトル／出演者／開場・開演／席種と価格／年齢制限／受付方法（Loppi店頭の有無）／受付期間**。
- 「スマートフォン受付のみ・Loppi店頭受付なし」の公演がある＝載せてよいがPCでは買えない
- 価格は**ローチケ1枚だけ**なので `price` には入れない（[[feedback_price]]＝2サイト一致が条件）

### 実績（2026-09-10）
| id | 公演 | 枠 |
|---|---|---|
| 7819 | REVERSE EDGE 2（SUPERNOVA KAWASAKI 11/2） | プレリク〜9/13＋一般 9/19発売 |
| 7820 | 別府葉子シャンソンコンサート in OSAKA（12/19 大阪） | 一般 9/20 10:00発売 |
| 7821 | Life History2026 ふるさとの唄 野田かつひこ（12/15 福岡） | 一般 9/14 10:00発売 |
