# UserPromptSubmit hook: 毎ターン、あたし(Claude)に「保存ルールは本体を読んでから適用」を注入する。
# 「一行しか読まないずぼら」を機械的に矯正する常設リマインド（memory: feedback_read_full_memory_before_apply）。
$ErrorActionPreference = 'SilentlyContinue'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$msg = '【常設リマインド】① 作業を始める前に PLAYBOOK.md の該当行を見て、挙がった memory を「全文」Read してから動く（一行要約だけで動かない）。② 保存ルール（除外/非表示/表示順/トーン/ジャンル/削除/新着プールの番号固定など）は該当 memory 本体で「条件（〜の時だけ）」まで確認し、単独ケースを巻き込まない。③ 🚨pushは1日3回まで（朝・昼・夜の便の最後に1回ずつ・途中の直しは commit だけ／2026-09-27に26回押した）。push・削除・ぴあの振り分けは承認不要＝検証が通ったら許可を待たずにやって「やった」と報告。「押すわね」「〜したら〜の順に進めるわね」でターンを閉じない(2026-09-17)。裏のジョブが終わったら言われなくても便の最後で押す。④ 🚨小窓（許可の確認）を出さない＝Bashは単発だけ。cd始まり・&&・;・|・$( )・<<・ループは使わず .py を Write して1発実行（feedback_no_expansion_commands・番人 no_expansion_guard.py）。⑤ 🚨質問は昼に出さない＝「夜に聞くリスト」（plan.md）に積んで、夜の「お疲れ様」でまとめて聞く。例外は不可逆のもの（削除が割れた・X投稿の文面）だけ（feedback_ask_questions_at_otsukaresama）。(まず PLAYBOOK.md / feedback_read_full_memory_before_apply)'
$out = @{ hookSpecificOutput = @{ hookEventName = 'UserPromptSubmit'; additionalContext = $msg } } | ConvertTo-Json -Compress
[Console]::Out.WriteLine($out)
exit 0
