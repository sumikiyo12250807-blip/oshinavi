# 11/16 夕 記事3本に情報を足した版の独立ファクトチェック（係2人・本文だけ渡し・素材は見せずゼロから）

## 結果
- 🔴 0件（3本とも）
- 🟠 で直したもの
  - freedomofchoice：「大阪公演のチケットぴあの一般発売は12/19(土) 10:00から」＝係が公式・ぴあで確かめられず → 文を削った（博多座の一般発売 R9年 1/16(土) 10:00 だけ残した＝博多座のページで一致）
- 🟠 で直さなかったもの（あたしが今日取ったぴあの生ページで一致を確かめ直した＝v1 から変えていない文）
  - takahashiyu：「高橋優」プレリザーブ 11/17(火) 11:00〜11/30(月) 23:59 → takahashiyu_pia.txt に「「高橋優」プレリザーブ」「2026/11/17(火) 11:00 ～ 2026/11/30(月) 23:59」
  - sumidabasho：車椅子席も 11/17(火) 10:00 に別の枠 → sumidabasho_pia.txt に「一般発売（車椅子席）」「2026/11/17(火) 10:00より発売」
  - freedomofchoice：イープラスの先着・座席選択の先行 11/17 12:00 → 今日も e+ は開かない（昼の便が回っている）。前回どおり OSHINAVI の登録（id53678）が出どころ・対象の回は書かず㊟
- 🟡 で直したもの（直した文は生HTMLの素材と照合し直した）
  - takahashiyu：「コメントは「あなたは世界を変えています」という言葉でしめくくられている」→「コメントには「あなたは世界を変えています」という一節もある」（原文の最後の文は別）
  - sumidabasho：「お弁当とお土産のセットの案内」→「お弁当セットの案内」（見出しは「お弁当セット」・お土産は画像のファイル名だけ）
  - freedomofchoice：犬山イヌコ「「ナイロン100℃」の頃から」→「「ナイロン100℃」をはじめ」（昔の話に読まれないように）
- 直さなかった🟡：前回の「free style stroke」は途中9会場が中止＝本文は「開かれていた」で誤りではない・中止の話は楽しい話でないので書かない
- 未公表：FREEDOM OF CHOICE のあらすじ・役どころ・KERA や出演者のコメントは公式・報道どちらにも出ていない（博多座の「あらすじ」欄は空）＝書いていない
- 機械照合（check.py）：書かない言葉0・経歴語0・「。」のあと改行・引用は生HTMLと全部一致

## 足した出典
### takahashiyu
https://www.billboard-japan.com/d_news/detail/107914/2
https://www.takahashiyu.com/news/page/2/
https://www.takahashiyu.com/news/0821release_tori_info/
https://www.takahashiyu.com/news/nhk_minnano-uta/
### freedomofchoice
https://www.astage-ent.com/stage-musical/s303510.html
（博多座・キューブ・東宝は前回と同じページの別の段）
### sumidabasho
https://www.sumo.or.jp/Jungyo/timetable/
https://www.sumo.or.jp/Jungyo/
