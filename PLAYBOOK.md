# 🧭 OSHINAVI 行動プレイブック（何かする前に必ずこの表で該当行を見る→挙げたmemoryを全文Read→動く）

**使い方**：作業を始める前に「これは何の行動か」を決め、下表の該当行を見る。「読む」欄のmemoryファイルを**全文Read**（一行要約で動かない）。「罠」は即席チェック。迷ったら止まって聞く。

---

## ゲート（手を止めてユーザーのOKを待つのは3つだけ）
**①新着の振り分け ②削除 ③push**。それ以外（変換/新着収集/投入/修正/統合/ヒール/重複掃除）は自走で実行→報告。
（出典：feedback_selfrun_gates_only_two / feedback_user_confirms_expired）

---

## 行動別チェックリスト

| 行動 | ゲート | 動く前に全文Readするmemory | 🚨罠（これで事故った） |
|---|---|---|---|
| **朝ルーチン** | 自走 | feedback_morning_routine / feedback_plan_md | ①plan.md②check_expired③ヒール④昼もう一度ヒール。振り分け/削除/pushは合図待ち |
| **期限切れ削除** | 要OK | feedback_user_confirms_expired / feedback_pre_delete_webfetch_verify / feedback_delete_nonpia_blindspot / feedback_reconcile_drop_unparsed_not_noise | 「抽選結果発表前」はふみ型で削除禁止／当日公演は翌朝／URLは機械抽出のみ(捏造禁止)／w.pia直販0枠は誤検出 |
| **新着harvest(ぴあ)** | 自走 | feedback_presale_first_harvest / feedback_capture_all_not_select / feedback_harvest_countdown_first / reference_pia_tickets_tool | 発売前優先・1バッチ50上限・eventCd総ざらい |
| **新着harvest(e+)** | 自走 | reference_eplus_harvest / reference_eplus_machine_parse | 各公演-P個別URL必須／発売中≠発売前／JSON-LDが源／撮影会除外 |
| **新着投入(genre:new化)** | 自走 | feedback_zero_error_pipeline / feedback_url_first_on_new_add / reference_reconcile_pia_tool / feedback_badge_date_full_form | 投入前check_badges＋reconcile --new／URL全件fetch／二段構えゼロエラー |
| **🔒投入後の新着プール** | — | **feedback_new_list_order_lock** / **feedback_candidate_list_stable_numbering** / feedback_new_order_array | 🚨🚨**丸ごと作り直さない＝id/番号振り直し禁止。個別直しは現物編集(id据え置き)**／削除は欠番／並びはid昇順固定 |
| **新着の振り分け** | 要OK | feedback_new_pool_ok_before_assign / project_vendor_genre_autoassign / feedback_genre_both_when_unclear | ユーザー「振り分けて」明示後のみ／ぴあカテゴリは再分類しない／迷いは主+extraGenres |
| **隠れ枠ヒール** | 自走 | feedback_harvest_today_sale_enddate / feedback_wpia_direct_sale_trap | 毎朝＋昼／startDate==dateは隠れ枠／w.pia直販は削除NG要目視 |
| **エントリ修正/統合** | 自走 | feedback_tour_consolidate / feedback_tour_per_ticket_url / feedback_bundle_full_rederive / feedback_multiwindow_webfetch_verify | ツアーは1エントリ／各公演に個別URL／全URL開いて再導出 |
| **表示・並び順いじる** | 要確認 | feedback_display_order / feedback_display_rules / feedback_ask_what_user_sees | 本日発売は一日中先頭／写経検証NG(実物eval)／「直ってない」は画面の実物を1つ聞く |
| **X投稿** | 要確認 | project_sns_promotion / feedback_x_link_oshinavi_only / feedback_x_no_link_spam / feedback_x_deadline_vs_presale_by_genre | 説明書かない・気持ちの代弁／URLはoshinavi.jp/?x=N／ツアー名は公式裏取り／文字数機械カウント |
| **push** | 要OK | feedback_push / feedback_check_before_push / project_netlify_credits | 1日2回・事前確認／commit→pushの間にブラウザチェック／push前にai.html/SSR再生成 |

---

## 全行動共通（毎回）
- 保存ルール（除外/非表示/表示順/トーン/ジャンル/削除）は**一行要約で動かず該当memory全文Read→条件(〜の時だけ)まで確認**（feedback_read_full_memory_before_apply）
- 出力は日本語・おねえ言葉（feedback_tone_onee / feedback_language）／推測で話さない・裏取り（feedback_no_speculation）／ツール出力捏造禁止（feedback_no_fabricated_output）
- 報告は短く・検索語は縦1列（feedback_short_reports）／エントリ参照はid＋公演名（feedback_entry_name_with_id）
