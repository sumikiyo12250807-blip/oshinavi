# UserPromptSubmit hook: 毎ターン、あたし(Claude)に「保存ルールは本体を読んでから適用」を注入する。
# 「一行しか読まないずぼら」を機械的に矯正する常設リマインド（memory: feedback_read_full_memory_before_apply）。
$ErrorActionPreference = 'SilentlyContinue'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$msg = '【常設リマインド】① 作業を始める前に PLAYBOOK.md の該当行を見て、挙がった memory を「全文」Read してから動く（一行要約だけで動かない）。② 保存ルール（除外/非表示/表示順/トーン/ジャンル/削除/新着プールの番号固定など）は該当 memory 本体で「条件（〜の時だけ）」まで確認し、単独ケースを巻き込まない。(まず PLAYBOOK.md / feedback_read_full_memory_before_apply)'
$out = @{ hookSpecificOutput = @{ hookEventName = 'UserPromptSubmit'; additionalContext = $msg } } | ConvertTo-Json -Compress
[Console]::Out.WriteLine($out)
exit 0
