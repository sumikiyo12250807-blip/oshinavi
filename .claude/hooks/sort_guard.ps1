# PostToolUse hook: 並び順ロジックが勝手に書き換わっていないか見張る番人。
# memory: feedback_display_order（並び順ルール）／feedback_display_rules（表示ルール変更は事前確認）
#
# 2026-07-19 の事故＝あたしが並び順ロジックを **その場の解釈で2回も改造**した。
#   ① 今日発売の枠を「本日発売」として一日中先頭に固定 → 日付の時間軸が壊れた
#   ② その塊の中を締切順に並べ替え → 7/19→9/22 と進んでから 7/19 に戻る並びになった
#   ユーザー「並び順がおかしい」「間違えてる 並び順のルール 言ってみて」→ 全部撤回して復元。
#
# 並び順ルールは 2026-07-10 にユーザーが決めた仕様:
#   日付を1本の時間軸にして早い順。同じ日付なら「発売開始」が上、「締切」が下。売切/終了は末尾。
#     7/11 発売開始 → 7/11 締切 → 7/12 発売開始 → 7/12 締切 …
# あたしの判断で触ってよいものではない。触るならユーザーの明示指示が要る。
#
# 監視対象＝index.html の EVENTS.sort ブロックと saleStartPending（並びを決める中核）。
# 解除＝ユーザー本人が「並び順を変えて」等と言うと sort_approval が承認印を書く（あたしからは作れない）。
$ErrorActionPreference = 'SilentlyContinue'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$root     = 'C:/Users/user/oshinavi'
$index    = Join-Path $root 'index.html'
$stateDir = Join-Path $root '.claude/state'
$hashFile = Join-Path $stateDir 'sort_hash.txt'
$approve  = Join-Path $stateDir 'sort_approved.txt'

if (-not (Test-Path $index)) { exit 0 }
if (-not (Test-Path $stateDir)) { New-Item -ItemType Directory -Path $stateDir -Force | Out-Null }

$text = Get-Content $index -Raw -Encoding UTF8

# 並びを決める2か所を取り出して指紋を取る
$m1 = [regex]::Match($text, '(?s)const SORT_PRESALE.*?EVENTS\.sort\(\(a, b\) => \{.*?\n  \}\);')
$m2 = [regex]::Match($text, '(?s)function saleStartPending\(t\) \{.*?\n  \}')
if (-not $m1.Success) { exit 0 }
$blob = $m1.Value + "`n" + $m2.Value

$sha = [System.Security.Cryptography.SHA256]::Create()
$hash = [System.BitConverter]::ToString($sha.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($blob))).Replace('-', '')

if (-not (Test-Path $hashFile)) {
    Set-Content -Path $hashFile -Value $hash -Encoding utf8
    exit 0
}
$prev = (Get-Content $hashFile -Raw).Trim()
if ($prev -eq $hash) { exit 0 }

# 変わっている。ユーザーの承認印が今日付いているか
$today = (Get-Date).ToString('yyyy-MM-dd')
$ok = $false
if (Test-Path $approve) {
    if ((Get-Content $approve -Raw).Trim() -eq $today) { $ok = $true }
}
if ($ok) {
    Set-Content -Path $hashFile -Value $hash -Encoding utf8
    exit 0
}

$msg = "BLOCKED: 並び順ロジック(EVENTS.sort / saleStartPending)を書き換えました。ユーザーの指示は出ていません。`n`n" `
     + "並び順ルール(memory: feedback_display_order・2026-07-10 ユーザー決定):`n" `
     + "  日付を1本の時間軸にして早い順。同じ日付なら「発売開始」が上、「締切」が下。売切/終了は末尾。`n" `
     + "    7/11 発売開始 / 7/11 発売開始 / 7/11 締切 / 7/12 発売開始 / 7/12 締切`n`n" `
     + "2026-07-19、あたしはこれを自分の解釈で2回改造して並びを壊し、全部撤回した。`n" `
     + "「本日発売が先頭に出ない」等の症状は、たいてい **当日ヒールのやり忘れ** が原因で、`n" `
     + "並び順ロジックの問題ではない。まずこれを流すこと:`n" `
     + "  python tools/heal_stale_deadlines.py --build`n" `
     + "  python tools/heal_stale_deadlines.py --apply`n" `
     + "  node tools/check_order.js`n`n" `
     + "やること: 直前のバックアップ(index.html.bak_*)から sort ブロックを戻す。`n" `
     + "本当に変更が要るなら、ユーザーに仕様を確認してから（表示ルール変更は事前確認が必須）。"
[Console]::Error.WriteLine($msg)
exit 2
