# livePocket 鉄壁ゲート 仕様（2026-09-28 夜 ユーザー指示）

> ユーザー「livePocketこのサイトから持ってくるイベントのゲートを作って、エージェントにサイドチェックしてもらって、鉄壁のゲートを作るの」
> 同じ夜「livePocket これおわったのだらけ　まだ売ってないのはないの？」

## 今の番人（tools/gate_livepocket_slots.py）の穴
- 作り直しに **同じ読み取り（livepocket_harvest.parse_event）と同じビルダー** を使う＝読み取りが間違えると番人も同じ間違いで「一致」する（ZAIKOスタリオンと同じ型）。
- ビルダーを通さない突合（raw_check）は **締切と配信だけ**。
- 見ていない＝公演日（date/dateLabel）・会場・県・受付の数（枠が丸ごと落ちる）・発売前/販売中/売切/販売終了の取り違え・startDate（発売日）・公演が終わっている・出す側の混入。

## 新しいゲート tools/gate_livepocket_indep.py（エージェントA が作る）
🚨**独立**＝`tools/livepocket_harvest.py` と `tools/build_livepocket_entries.py` を import しない・コードを写さない・読まない。
   生HTML（https://livepocket.jp/e/<id>）を自分の読み方で読む（可能なら JSON-LD / meta / 構造化データを優先し、DOMのクラス名に頼る部分は最小に）。
入力＝`--built <json>`（投入前）／`--ids`（登録済み）／無指定＝index.html の livePocket 由来すべて。
1ページごとに独立に取り出す：
  A. 開催日（全日程）・開演時刻 B. 会場名・都道府県 C. 受付の一覧（名前・札・開始日時・終了日時・券種の札）
登録と突き合わせる（1つでも違えば 🚨・exit 1）：
  ① entry.date ＝ 最終開催日／dateLabel の初日・最終日が一致（会期の型も）
  ② venue・prefecture が一致（表記ゆれは正規化してから・違えば🚨）
  ③ 販売前/販売中/予定枚数終了/販売終了 の受付の数 ＝ 登録の枠（そのページURLの枠）の状態別の数
     ＝枠が丸ごと落ちている／増えている を捕まえる。出す側の受付・載せない理由のある受付は理由付きで数から外す
  ④ 各受付：販売前→ startDate＝開始日・date＝締切（締切が公演日より後なら公演日。配信は例外）／販売中→ startDate なし・date＝締切 or 公演日／予定枚数終了→ soldout／販売終了→ soldout＋saleEnded
  ⑤ 最終開催日 < 今日 のエントリが残っていない
  ⑥ 出す側（出店・出展・出演エントリー・案内登録）が混ざっていない
  ⑦ 読めないページ・知らない札は「一致」にしない＝判定不能として exit 1（照合できた枠/全枠 で報告）
出力＝tmp/gate_livepocket_indep_report.txt（食い違いは 項目・登録の値・実ページの値・URL）
間隔＝1秒以上（livePocket へ同時に2本走らせない）

## サイドチェック（エージェントB・Aのコードを読まない）
1. index.html と tmp/x0928e/built_livepocket.json から **無作為に30件**（発売前・販売中・売切・販売終了・複数日・複数受付・配信 を必ず含む）を選び、
   実ページを自分で開いて①〜⑥の正解を手で書き出す（tmp/x0928e/lp_truth_30.json）。
2. 正解と登録を比べて、登録の誤りを列挙（＝今のビルダーの穴）。
3. Aのゲートをその30件に流し、**Bが見つけた誤りをAが全部鳴らすか**・**正しい件を鳴らさないか**を確かめる。
4. 変異テスト＝built JSON のコピーに誤りを10種わざと入れて（締切を1日ずらす・売切を消す・受付を1つ消す・県を変える・startDate を消す・公演日を過去にする…）Aが全部鳴らすか。
5. 1つでも見逃したら A に差し戻し → 直す → もう一度。**全部鳴って・正しい件で鳴らない**まで。

## 通ったら
- 毎朝の手順（.claude/skills/day/SKILL.md の livePocket 行・reference_livepocket_harvest）に「投入前に gate_livepocket_indep --built → exit 0 以外は入れない」を足す
- 今夜の 470件（tmp/x0928e/built_livepocket.json）と登録済み 366件に流す
