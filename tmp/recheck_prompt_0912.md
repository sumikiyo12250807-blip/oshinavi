あなたはチケット情報の独立検証係です。**登録済みの値は一切見ずに**、ぴあの実ページだけからゼロで情報を導いてください。

入力ファイル: C:\Users\user\oshinavi\tmp\recheck_{PART}_0912.txt
（1行1件。`id<TAB>ぴあURL（空白区切りで複数あることがある）`）

各 id について、書かれたぴあURLを全部開き（URLが eventBundleCd= の形なら、そのまとめページに並ぶ個別公演ページ event.do?eventCd=... も全部開く）、次を書き出す:
- title: ぴあに出ている公演名
- pia_genre: ぴあのページに出ているジャンル表示（パンくず等。例「音楽 > J-POP・ROCK」）
- shows: 公演ごとに {date: "YYYY-MM-DD", pref: 都道府県, venue: 会場名}
- slots: 販売枠（券種・受付）ごとに {type: 枠の名前, show_dates: [対象公演日 "YYYY-MM-DD"...], start: 受付開始 "YYYY-MM-DD HH:MM" か null, end: 受付終了 "YYYY-MM-DD HH:MM" か null, state: "受付中" / "発売前" / "受付終了" / "予定枚数終了" / "不明"}
- note: 読めなかった・混雑ページだった・ページが消えていた等があれば1行。無ければ null

今日は 2026-09-12。
注意:
- 🚨index.html は開かない・読まない（登録値に引っぱられないため）。書き換えも絶対にしない。
- ぴあが混雑ページ（sorry・「アクセスが集中」）を返したら30秒ほど置いて取り直す。短時間に叩きすぎない（1ページごとに1〜2秒あける）。
- WebFetch の要約は「受付終了」を誤読することがある。受付期間の日付の文字で状態を決める（開始が過去かつ終了が未来＝受付中）。
- 可能なら python で生HTMLを取って読む方が確実（requests＋User-Agent指定）。スクリプトは scratchpad に .py を Write して `python ファイル.py` で実行する。python -c や heredoc は使わない。
- Bash/PowerShell を使う時、許可画面の description は必ず日本語で書く。

出力: 結果を JSON 配列で `C:\Users\user\AppData\Local\Temp\claude\C--Users-user-oshinavi\0fc1d2b7-fccb-457b-879f-7aec070e018d\scratchpad\recheck_{PART}_result.json` に書く（1要素＝1 id、キーは id(数値), title, pia_genre, shows, slots, note）。
最後のメッセージは日本語で「読めた件数／読めなかった件数とそのid」だけを短く。
