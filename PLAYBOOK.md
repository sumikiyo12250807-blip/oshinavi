# 🧭 OSHINAVI 行動プレイブック（何かする前に必ずこの表で該当行を見る→挙げたmemoryを全文Read→動く）

**使い方**：作業を始める前に「これは何の行動か」を決め、下表の該当行を見る。「読む」欄のmemoryファイルを**全文Read**（一行要約で動かない）。「罠」は即席チェック。迷ったら止まって聞く。

---

## 🚨ゲート（2026-08-16 全面変更＝**ユーザーのGO待ちは無くなり「エージェント検証」に置き換わった**）
push・削除・振り分け、**3つとも自走してよい**。ただし**必ず次のA/B/Cを守る**（出典：feedback_selfrun_gates_only_two / feedback_push / feedback_user_confirms_expired / feedback_new_pool_ok_before_assign を全文Read）。

| | 必須 |
|---|---|
| **A 検証** | **別エージェントに独立再導出させて疑義ゼロ**（あたしの結論を見せない）＋機械ゲート全通し（check_badges／reconcile_pia --ids／check_order.js／CRLF指紋） |
| **B 保留**<br>🚨**止まるのは禁止** | **疑義・迷い・相談が1つでもあれば「その件だけ保留」**にして①質問を出す②**すぐ別の作業へ移る**③**返事が来るまで聞き続ける**。<br>🚨**便や作業を止めない・自分で決めない**（2026-08-26「止まるのはダメよ／プッシュも、迷ったのは省いておいてプッシュしとくの」）。<br>特に**振り分けのジャンル判断**と**削除の除外条件**（売り切れ／発売時刻前／w.pia直販0券種／他社に生き枠／抽選結果待ち／ぴあだけの照合） |
| **C 残す** | **後から見られるリンク**＝削除は公演名＋確認用直URL、振り分けは公演名＋ジャンル＋URL。**報告に出す＋`logs/` にも残す**（携帯から遡れるように） |
| **⛔例外** | 🚨🚨**ぴあ以外（e+／楽天／ローチケ）で載せるイベントは、毎回ユーザーが「目視で」確認する**（2026-08-27 ユーザー明示・8/16の「確認を待つ」から強化）。<br>**載せる中身そのもの**（公演名／公演日／**開演時刻**／会場／県／枠名／受付の開始と締切／URL）を**表で見せてOKをもらってから投入**する。<br>🚨「入れて」は**方針のOK**であって、**中身確認を省いてよいという意味ではない**（同日にあたしが誤読した）。<br>Why＝`reconcile_eplus.py` は存在するが、ぴあのように「事故→原因究明→道具に恒久対策」を積んでおらず**まだ鉄壁ではない**。ぴあと同じ道を通して育てるまでは人の目で埋める。自走に移す時期は**ユーザーが決める**。<br>[[feedback_nonpia_user_eyes_until_gate]]／ぴあ由来は従来どおり自走OK |

🚨**毎朝 `node tools/check_zero_badge.js` を回す**（2026-08-20新設）＝「カードは出るのに買える枠が0」を拾う唯一の網。
終了コード2が出たら放置しない（2026-08-20に54件が埋もれていた）。

**push**＝1日3回まで（Netlifyクレジット）・**push後は何を上げたか1行報告**。
🚨**迷った件はpushから省いて、残りは押す**＝返事待ちで便ごと止めない（2026-08-26）。
🚨**便の中でpushはいちばん最後**＝**中身を直し切ってから公開する**（[[feedback_push]] の2026-08-26項）。
　**朝**＝振り分け・新着収集まで／**昼**＝本日発売の締切を差し替えてから／**夜**＝X投稿の公演の取りこぼしを潰してから。
　ルーチンの前に押すと「買えない枠を消した結果」が昼まで出ない＝**買えないものを半日載せたままになる**。クレジットの話ではない。
🚨**便を締める前に3点を機械で確認する**（2026-08-18に未pushのまま「今日は終わり」と報告した）＝
①`git log --oneline origin/main..HEAD` が空か ②EVENTSを触ったら `build_ai_page.py` を回したか
③push直前に `reconcile_pia.py --new` を通したか。**自分の過去の発言を写して報告しない**（[[feedback_unpushed_commit_check]]）。
⚠️**「自走OK」は「検証を飛ばしてよい」ではない**。緩む局面で緩い方に転んだ事故が3回ある（7/19・7/31ほか）。**迷ったら消さない・押し切らない**。

---

## 🕐 1日の運転（2026-08-16 ユーザーと合意）

**ユーザーの「おはよう」で開始 → 朝／昼／夕方／夜の4便**。完全自動ではなく「**止まってよい自走**」＝
ゲートで止まって携帯から返事をもらい、その場から再開する。手順書は **`.claude/skills/day/SKILL.md`**（`/day`）。

| 便 | やること | 止まる所 |
|---|---|---|
| 🌅朝 | 🚨**①朝のルーチン（期限切れtriage→隠れ枠ヒール→「〆切日に発売時刻」型の掃除→削除→check_zero_badge）②前夜の新着をチェック ③振り分け ④新着を収集 ⑤最後にpush**（🚨**2026-08-26夜ユーザー修正＝pushは朝の便のいちばん最後**。「前日と変わりないのにプッシュしてどうすんのよ」） | 相談があれば止まる（8/16以降GO待ち無し） |
| ☀️昼 | 隠れ枠ヒールをもう一度。🚨**普通は12時以降**・その日に**14:00発売の枠があるなら14時より後**にずらす（発売時刻の後でないとぴあが締切を出さない） | 同上 |
| 🌆夕方 | （新着収集は**朝に前倒し**した＝2026-08-16変更） | — |
| 🌙夜 | 🚨**着手は17:00**（20:01予約に間に合わせるため）。X投稿＝**Xフォロワー多い順トップ4＋まとめ1本**（🚨2026-08-17＝**選定でユーザーに聞かない・着手はもっと早く**）。本文はFable。予約は**20:01から15分おき**（`:01/:16/:31/:46`）＝🚨2026-08-30に19:01から変更（実測でクリック率は夜20-23時0.45%／夕17-19時0.27%）。<br>🚨**予約したら、投稿に出した公演のチケット取りこぼしをぴあで総ざらいして潰す→直してからpush**（2026-08-26） | **文面はユーザーが見てから予約**（ここは従来どおり） |

🚨**新着50件は「投入した翌日」に再チェックを通してからpush**（ユーザー明示）。詳細 `project_daily_operation`

---

## 行動別チェックリスト

| 行動 | ゲート | 動く前に全文Readするmemory | 🚨罠（これで事故った） |
|---|---|---|---|
| **朝ルーチン** | 自走 | feedback_morning_routine / feedback_plan_md / **feedback_zero_badge_gate** | ①plan.md②check_expired③ヒール④昼もう一度ヒール。振り分け/削除/pushは合図待ち |
| **期限切れ削除** | 要OK | feedback_user_confirms_expired / feedback_pre_delete_webfetch_verify / feedback_delete_nonpia_blindspot / feedback_reconcile_drop_unparsed_not_noise / **feedback_soldout_keep_visible** | 「抽選結果発表前」はふみ型で削除禁止／当日公演は翌朝／URLは機械抽出のみ(捏造禁止)／w.pia直販0枠は誤検出／🚨**売り切れは削除せず`mark_soldout.py`で「予定枚数終了」表示に**（削除ゲートに載せない） |
| **新着harvest(ぴあ)** | 自走 | feedback_presale_first_harvest / **feedback_newpool_presale_ratio_gate** / feedback_capture_all_not_select / feedback_harvest_countdown_first / reference_pia_tickets_tool | 発売前優先・1バッチ50上限・eventCd総ざらい／🚨**投入前に `python tools/harvest_audit.py` でカバー率と発売前比率を出す**（「発売前が枯れた」は数字で証明してから言う。2026-08-17に音楽カバー率4.7%＝あ行だけで50件埋めた事故） |
| **新着harvest(e+/楽天/ローチケ)** | 🚨**要ユーザー目視**（2026-08-27） | **feedback_nonpia_user_eyes_until_gate** / reference_eplus_harvest / reference_eplus_machine_parse / project_eplus_harvester_bug_and_qc | 🚨**収集は自走でよいが、載せる前に中身を表で見せてOKをもらう**（公演名／公演日／**開演時刻**／会場／県／枠名／受付の開始と締切／URL）。`reconcile_eplus.py --ids` を通す（8項目・FAILなら投入しない）。各公演-P個別URL必須／発売中≠発売前／JSON-LDが源／撮影会除外／**同日同会場で時刻違いはバッジに時刻**／「先行」は条件つきか裏取り |
| **新着投入(genre:new化)** | 自走 | feedback_zero_error_pipeline / feedback_url_first_on_new_add / reference_reconcile_pia_tool / feedback_badge_date_full_form | 投入前check_badges＋reconcile --new／URL全件fetch／二段構えゼロエラー |
| **🔒投入後の新着プール** | — | **feedback_new_list_order_lock** / **feedback_candidate_list_stable_numbering** / feedback_new_order_array | 🚨🚨**丸ごと作り直さない＝id/番号振り直し禁止。個別直しは現物編集(id据え置き)**／削除は欠番／並びはid昇順固定 |
| **新着の振り分け** | 要OK | feedback_new_pool_ok_before_assign / project_vendor_genre_autoassign / feedback_genre_both_when_unclear | ユーザー「振り分けて」明示後のみ／ぴあカテゴリは再分類しない／迷いは主+extraGenres |
| **隠れ枠ヒール** | 自走 | feedback_harvest_today_sale_enddate / feedback_wpia_direct_sale_trap | 毎朝＋昼／startDate==dateは隠れ枠／w.pia直販は削除NG要目視 |
| **エントリ修正/統合** | 自走 | feedback_tour_consolidate / feedback_tour_per_ticket_url / feedback_bundle_full_rederive / feedback_multiwindow_webfetch_verify | ツアーは1エントリ／各公演に個別URL／全URL開いて再導出 |
| **表示・並び順いじる** | 要確認 | feedback_display_order / feedback_display_rules / feedback_ask_what_user_sees | 本日発売は一日中先頭／写経検証NG(実物eval)／「直ってない」は画面の実物を1つ聞く |
| **X投稿** | 選定は自走／**文面は要確認** | 🚨🚨**まず feedback_x_post_method_0825 を全文Read（これが決定版・字数も締めもここで決まる）** / project_sns_promotion / **feedback_x_pick_bigname_miss** / feedback_model_routing_fable / feedback_x_link_oshinavi_only / feedback_x_no_link_spam / feedback_x_deadline_vs_presale_by_genre | 🚨**2026-08-17変更＝選定はユーザーに聞かない。Xフォロワー多い順で上位4本＋まとめ1本・着手は早く（夜まで待たない）・文面まで作っておく**／説明書かない・気持ちの代弁／URLは素のoshinavi.jp／ツアー名は公式裏取り／文字数機械カウント／フォロワー数はポスト数・Instagramと取り違えない・取れなければ「取れなかった」と書く |
| **push** | 要OK | feedback_push / feedback_check_before_push / project_netlify_credits | 1日2回・事前確認／commit→pushの間にブラウザチェック／push前にai.html/SSR再生成 |

---

## 全行動共通（毎回）
- 保存ルール（除外/非表示/表示順/トーン/ジャンル/削除）は**一行要約で動かず該当memory全文Read→条件(〜の時だけ)まで確認**（feedback_read_full_memory_before_apply）
- 🚨**memoryや手順書に書き足す時は「やること」を必ず先頭に置く**（下の方に書くと実行されない＝2026-08-26ユーザー指摘。新しい決定はいちばん上・古いのは「失効」印をつけて下に残す）
- 出力は日本語・おねえ言葉（feedback_tone_onee / feedback_language）／推測で話さない・裏取り（feedback_no_speculation）／ツール出力捏造禁止（feedback_no_fabricated_output）
- 報告は短く・検索語は縦1列（feedback_short_reports）／エントリ参照はid＋公演名（feedback_entry_name_with_id）
