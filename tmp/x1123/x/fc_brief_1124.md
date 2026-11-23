# 11/24(火)発売の X 投稿4本の独立ファクトチェック（あなたは確かめる係）

前提：**文はまちがっている前提で**1文ずつ確かめる。書き手のメモ（sources_1124.md・material）は読まない。自分で売り場と公式を開いて、ゼロから確かめる。

## 対象
C:/Users/user/oshinavi/tmp/x1123/x/post/ の mat01〜mat03・shu01（4本）

## 確かめ方
1. 一覧の行（時刻・名前・県・（先行））は、OSHINAVI の登録（C:/Users/user/oshinavi/index.html の EVENTS）と突き合わせる。
   - 照合は Python を .py に書いて1回で流す（`import sys; sys.path.insert(0,'C:/Users/user/oshinavi/tools'); import compact_events as C; E=C.load(open('C:/Users/user/oshinavi/index.html',encoding='utf-8',newline='').read())`）。
   - 対象は 11/24・11/25・11/26 に始まる受付（tickets の startDate と type の「HH:MM発売」）。
   - 見る点：行の時刻にその公演の受付があるか・県が合うか・（先行）の有無・抽選を一般のように書いていないか。
   - 書いた .py と結果は C:/Users/user/oshinavi/tmp/x1123/x/ に fcx_ で始まる名前で置く。
2. 本文の事実（公演の中身・日付・曜日・会場・受付名・締切・料金・ドリンク代）は売り場と公式のページを WebFetch で開いて照合する。
   - 主役＝id56015 スワローズ 楽燕祭 2027（スペシャルシート抽選 11/24 12:00）。URL はカード（tickets[].url・links）と、東京ヤクルトスワローズの公式サイトから取る。URL は推測で作らない。
   - ぴあ（t.pia.jp）は1件ごとに数秒あけてよい（いまぴあを叩くほかの道具は動いていない）。e+ は同時に2つ以上開かない。
3. 曜日は Python で計算する。2026-11-24 は火曜。
4. X_SCRIPT.md の決まり（C:/Users/user/oshinavi/X_SCRIPT.md）に明らかに反する所も拾う（1晩5本の形・J-POP 8件まで・ほかは5件まで・予告はジャンル名だけ）。

## 出すもの
C:/Users/user/oshinavi/tmp/x1123/x/fc_1124.md：
- 🔴 まちがい（載せると嘘になる）
- 🟠 直したほうがよい（決まり違い・言い過ぎ）
- 🟡 気になる程度

それぞれに、どの投稿のどの文か・正しい値・根拠の URL を書く。最後に、照合できた行と全部の行の数を書く。

## 決まり
- 急ぎ：18:40 までに出す。
- Bash は1つのコマンドだけにする（&& ; | や cd は使わない）。
- メールアドレスは書かない。
- 投稿のファイルは直さない（報告だけ）。
- 最後の報告は日本語で短く：🔴🟠🟡 の数と、各指摘を1行ずつ。
