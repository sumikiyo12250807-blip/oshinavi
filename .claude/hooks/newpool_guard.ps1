# PostToolUse hook: 新着プール(genre:"new")が勝手に減っていないかを見張る番人。
# memory: feedback_new_pool_ok_before_assign（振り分けはユーザーの明示OK後）を機械的に強制する。
#
# 2026-07-19 の事故＝あたしが新着47件をユーザーのチェック前に振り分け、
# genre が classic 等に変わって「新着タブが空っぽ」になった。ユーザーは見るものを失った。
# 保存ルール同士が矛盾していた（ゲートは2つ／振り分けはOK後）ため、意志だけでは防げない。
# よってファイルの実体を数えて止める。
#
# 判定:
#   new件数が 0 になった or 半分以上ドカッと減った → 振り分けの疑い → exit 2 でブロック
#   数件だけ減った（統合・新着からの除去）→ 通すが件数は記録する
# 解除:
#   ユーザー本人が「振り分けて」等と言うと assign_approval.ps1 が承認印を書く。
#   あたし(Claude)からは承認印を作れない＝偽装できない。
$ErrorActionPreference = 'SilentlyContinue'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$root      = 'C:/Users/user/oshinavi'
$index     = Join-Path $root 'index.html'
$stateDir  = Join-Path $root '.claude/state'
$countFile = Join-Path $stateDir 'newpool_count.txt'
$approve   = Join-Path $stateDir 'assign_approved.txt'

if (-not (Test-Path $index)) { exit 0 }
if (-not (Test-Path $stateDir)) { New-Item -ItemType Directory -Path $stateDir -Force | Out-Null }

# 現在の genre:"new" 件数を数える
$text = Get-Content $index -Raw -Encoding UTF8
$now  = ([regex]::Matches($text, '"genre":\s*"new"')).Count

# 前回値（初回は記録して通す）
if (-not (Test-Path $countFile)) {
    Set-Content -Path $countFile -Value $now -Encoding utf8
    exit 0
}
$prev = 0
[int]::TryParse((Get-Content $countFile -Raw).Trim(), [ref]$prev) | Out-Null

# 増えた・変わらない → 記録して通す
if ($now -ge $prev) {
    Set-Content -Path $countFile -Value $now -Encoding utf8
    exit 0
}

# 減った。ユーザーの承認印が今日付いているか
$today = (Get-Date).ToString('yyyy-MM-dd')
$ok = $false
if (Test-Path $approve) {
    if ((Get-Content $approve -Raw).Trim() -eq $today) { $ok = $true }
}
if ($ok) {
    Set-Content -Path $countFile -Value $now -Encoding utf8
    exit 0
}

# 振り分け相当の大幅減（全消し or 半分以上）はブロック
$bigDrop = ($now -eq 0) -or (($prev - $now) -ge [math]::Ceiling($prev / 2.0))
if ($bigDrop -and $prev -gt 0) {
    $msg = "BLOCKED: 新着プール(genre:`"new`")が $prev 件 -> $now 件に減りました。ユーザーの振り分けOKは出ていません。`n`n" `
         + "これは 2026-07-19 に起きた事故と同じ形です（ユーザーのチェック前に振り分け→新着タブが空になり、見るものが無くなった）。`n`n" `
         + "やること:`n" `
         + " 1. 直前のバックアップ(index.html.bak_*)から genre を `"new`" に戻す`n" `
         + " 2. 決めたジャンルは _genre に下書きとして持たせる`n" `
         + " 3. ユーザーに「新着(件数)チェックお願い」と報告して待つ`n`n" `
         + "振り分けてよいのは、ユーザー本人が「振り分けて」「振り分けOK」等と言った時だけです。`n" `
         + "(memory: feedback_new_pool_ok_before_assign / feedback_selfrun_gates_three)"
    [Console]::Error.WriteLine($msg)
    exit 2
}

# 小幅減（統合・除去）は通すが記録は更新
Set-Content -Path $countFile -Value $now -Encoding utf8
exit 0
