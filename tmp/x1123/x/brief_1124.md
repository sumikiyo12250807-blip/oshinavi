# 11/24(火)発売の X 投稿を書く（あなたは書き手）

## 読むもの（これだけ）
1. C:/Users/user/oshinavi/X_SCRIPT.md を**全部**読む（2回に分けて Read）。これが唯一の決まり。とくに先頭の「2026-11-22〜 1晩は最大5本」と「2026-11-23〜 予約は15分おき」
2. 素材：C:/Users/user/oshinavi/tmp/x1123/x/material_1124.md の「# 11/24(火)発売」の部分（ジャンル別に機械でまとめた行・そのまま使う）。下の「2〜3日後の発売」は使わない
3. 主役のカード：C:/Users/user/oshinavi/tmp/x1123/x/shu_1124.txt（主役の名前の段だけ）
4. 見本（昨日すちこが OK した分）：C:/Users/user/oshinavi/tmp/x1122/x/post/*.txt（形・長さ・締めの散らし方を寄せる。文はそのまま使わない）

## 本数と並び（今夜は4本＝トレンド枠なし。Snow Man は売り場で買えるか確かめられなかったので出さない）
- mat01：スポーツ・おでかけ・舞台（sports 3行・musical 2行・engeki 2行・kids・art・talkshow・dento・musicetc の珠光茶会）
- mat02：お笑い（owarai 8行。NMB48 劇場の公演は FANY の札がお笑い＝ここに入れる。研究生らしい16人の行2本は「NMB48 劇場公演」として1行にまとめてよい）
- mat03：音楽（jpop 3行＝8件まで全部／classic 3・rock 2・idol 8行・enka の DRUM TAO・yougaku 1＝ジャンルごとに最大5件・残りは前からの丸め方で）
- shu01：主役1本＝スワローズ 楽燕祭 2027（id56015・渋谷区文化総合センター大和田 さくらホール R9年 1/23・スペシャルシート抽選 11/24 12:00）＝明日発売でフォロワーがいちばん多い（東京ヤクルトスワローズ公式 805,500・tmp/x1123/x/followers_1124.json）。公式（ヤクルトスワローズの公式サイトのファンクラブ・イベントのページ）で中身の裏を取る。楽燕祭はまとめ mat01 にも残す
- 「このあとの投稿では…」の予告は上の順に合わせる（ジャンル名だけ・時刻は書かない）。最後の shu01 は「明日の夜も…」の締め

## 主役の中身（1〜3行）
- 公式（主催・劇場・本人の公式サイト・FANY のイベントページ・e+）を WebFetch で開いて、裏が取れた事実だけ書く。1事実1URL で C:/Users/user/oshinavi/tmp/x1123/x/sources_1124.md に残す（どの投稿のどの文の根拠か）。ぴあ（t.pia.jp）は開かない
- 仕組みの解説はしない。経歴は書かない。ドリンク代が売り場に書いてあれば書く（11/23 すちこ「ドリンク代は書いて」）
- 公式のタグ：主役は名前そのもののタグを優先

## 記事の1行（どれか1本に）
- いまトップに出ている新しい記事の1本（X_SCRIPT の 11/12 の項の形）。URLは足さない。C:/Users/user/oshinavi/pickup/index.html の先頭の記事を見て、今夜の投稿に関係のあるものがあればそれ、無ければ先頭の1本

## 書き方の注意
- 時刻・日付・会場・受付名は素材とカードの表記どおり。曜日は自分で計算して確かめる（2026-11-24 は火曜）
- 主役の ?q= は %エンコード（python C:/Users/user/oshinavi/tools/x_qlink.py 名前）
- 書けたら機械の検品：`python C:/Users/user/oshinavi/tools/x_check.py <ファイル>`・`python C:/Users/user/oshinavi/tools/x_qlink.py --check "C:/Users/user/oshinavi/tmp/x1123/x/post/*.txt"`。鳴ったら直す
- Bash は1つのコマンドだけ（&& ; | や cd は使わない）。メールアドレスは書かない

## 出すもの
- C:/Users/user/oshinavi/tmp/x1123/x/post/mat01.txt〜mat03.txt・shu01.txt（貼り付ける文そのまま）
- C:/Users/user/oshinavi/tmp/x1123/x/sources_1124.md
- 最後の報告は日本語で短く：ファイル名と各本の1行目の見出し・何のジャンルか・検品の結果だけ
