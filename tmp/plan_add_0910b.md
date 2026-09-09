
# 🔴 9/10 昼〜夜に続けること（楽天まわり・ユーザー指摘2件から）

```
ユーザー（9/10 朝）＝
  ①「木下グループが売り切れ出てる　売り切れで表示してね」
  ②「楽天から持ってきたチケットが売ってるのしかない件　これから発売のチケット探して、そっちを優先にして」

✅①は片づいた＝tools/rakuten_perf_status.py を新設して34件を当て、10枠に「予定枚数終了」を付けた
   🚨楽天の売り状態は**生HTMLに1文字も無い**。購入ボタンのAJAX
      POST https://cms-api.ticket.rakuten.co.jp/coreui/ajax/performance/widget
      {ids, ecd, eid}  ← ecd/eid は生HTMLから正規表現で取れる
   にしか出ない。カードの class は売り切れても active のまま。
   ⏭️別レイアウトで**調べられていない9件**（＝売り切れていない、ではない）:
      1 さだまさし／3674 クーザ／7505 THE ORCHESTRA TOKYO／7506 Chalca／7507 ちゃーむぽっしゅ／
      7582 世田谷たまがわ花火／7583 春猿火／7584 KOKO／7585 理芽
      形＝data-perf を持たない。7582は価格表に「予定枚数終了」が生で入っている。
      7505は data-event-json（外部JSON）。1と7583は salesDisplayStatus が入っている単独公演型。

✅②の入口が見つかった＝**post-sitemap の番号は投稿順**（1番=2019年 / 27番=2026年）。
   26+27 の 1,262件で「今動いている公演」がほぼ入る。lastmod で絞ってはいけない。
   道具＝tools/rakuten_presale_harvest.py --maps 27,26
   結果＝tmp/rakuten_presale_0910.json ／ 仕分け＝tmp/rakuten_presale_split_0910.py

   やること（順に）:
     1. tmp/rakuten_presale_split_0910.py で ①既存に足す ②同名だがURL違い ③新規 に分ける
     2. ①＝登録済みなのに発売前の枠だけ抜けている型（理芽・KOKO・春猿火で実証）
        → build_rakuten_entries で作り直して refresh_deadlines（消さない形）で足す
     3. ③＝build_rakuten_entries → 重複チェック → 新着プールへ
        🚨ぴあ以外なので**振り分けはユーザーの確認後**（新着タブに置く）
     4. reconcile_rakuten --ids で照合してから push

🚨恒久＝毎日の新着収集に「楽天の発売前」を入れる。ぴあ→楽天→e+ の順は変えない。
```
