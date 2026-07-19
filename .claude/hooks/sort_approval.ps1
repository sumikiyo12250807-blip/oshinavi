# UserPromptSubmit hook: ユーザー本人の発言だけを鍵にして、並び順ロジックの変更を解錠する。
# sort_guard.ps1（並び順が勝手に書き換わったらブロックする番人）とセットで動く。
# あたし(Claude)はこの承認印を書く手順を持たない＝自分でOKを出したことにできない。
# (memory: feedback_display_order / feedback_display_rules)
$ErrorActionPreference = 'SilentlyContinue'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$raw = [Console]::In.ReadToEnd()
if (-not $raw) { exit 0 }
try { $data = $raw | ConvertFrom-Json } catch { exit 0 }
$p = $data.prompt
if (-not $p) { exit 0 }

$stateDir = 'C:/Users/user/oshinavi/.claude/state'
if (-not (Test-Path $stateDir)) { New-Item -ItemType Directory -Path $stateDir -Force | Out-Null }
$approve = Join-Path $stateDir 'sort_approved.txt'

# 「並び順を変える」への明示的なGOだけを鍵とみなす。
# 「順番がおかしい」「並び順がおかしい」は “直せ” であって “ロジックを好きに変えろ” ではない（2026-07-19の教訓）。
$patterns = @(
    '(並び順|表示順|ソート|並べ方).{0,8}(変えて|変更して|直していい|改造して|変えていい)',
    '(並び順|表示順|ソート).{0,6}(ルール).{0,8}(変えて|変更)',
    '(発売開始|本日発売).{0,12}(先頭|上).{0,8}(に(して|固定)|でいい)'
)
$hit = $false
foreach ($re in $patterns) {
    if ($p -match $re) { $hit = $true; break }
}
if ($hit) {
    Set-Content -Path $approve -Value (Get-Date).ToString('yyyy-MM-dd') -Encoding utf8
}
exit 0
