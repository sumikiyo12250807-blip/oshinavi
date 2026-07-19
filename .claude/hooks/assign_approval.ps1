# UserPromptSubmit hook: ユーザー本人の発言だけを鍵にして、新着の振り分けを解錠する。
# newpool_guard.ps1（新着が勝手に減ったらブロックする番人）とセットで動く。
#
# 狙い: 解錠の権限をユーザーの発言だけに握らせる。あたし(Claude)はこのファイルを
# 書く手順を持たない＝「自分でOKを出したことにする」偽装ができない。
# (memory: feedback_new_pool_ok_before_assign / feedback_selfrun_gates_three)
$ErrorActionPreference = 'SilentlyContinue'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$raw = [Console]::In.ReadToEnd()
if (-not $raw) { exit 0 }
try { $data = $raw | ConvertFrom-Json } catch { exit 0 }
$p = $data.prompt
if (-not $p) { exit 0 }

$stateDir = 'C:/Users/user/oshinavi/.claude/state'
if (-not (Test-Path $stateDir)) { New-Item -ItemType Directory -Path $stateDir -Force | Out-Null }
$approve = Join-Path $stateDir 'assign_approved.txt'

# 「振り分け」への明示的なGOだけを鍵とみなす。
# 単なる「OK」「いいよ」は対象外（曖昧な肯定を承認と読まない・過去の誤削除の教訓と同じ）。
$patterns = @(
    '振り?分け(て|OK|おｋ|オッケー|よろ|お願い|おねがい)',
    'ジャンル(分け|振り分け)(て|OK|おｋ|お願い|おねがい)',
    '(新着|チェック).{0,10}(OK|おｋ|オッケー).{0,10}(振り?分け|ジャンル)',
    '(振り?分け|ジャンル分け).{0,6}(進めて|やって|実行)'
)
$hit = $false
foreach ($re in $patterns) {
    if ($p -match $re) { $hit = $true; break }
}
if ($hit) {
    Set-Content -Path $approve -Value (Get-Date).ToString('yyyy-MM-dd') -Encoding utf8
}
exit 0
