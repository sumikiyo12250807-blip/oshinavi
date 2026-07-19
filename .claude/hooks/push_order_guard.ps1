# PreToolUse hook: git push の直前に並び順を実日付で検査し、壊れていたら push を止める。
# memory: feedback_display_order（push前に並び順の違反0を確認してから出す）を機械的に強制する。
#
# 2026-07-19 の事故＝ユーザー「順番が変わってる 初めは本日発売で 次が本日まで販売 何で変えるの？」。
# 真因は並び順ロジックではなく **当日ヒールのやり忘れ**：ぴあは発売時刻後に締切を出すため、
# 朝ヒールだけだと今日発売の枠が startDate==date のまま残り、「本日発売🔵」ではなく
# 「本日まで販売🟢」として並ぶ（さらに翌日には画面から消える）。
# 既存の tmp/test_sort_0710.js は today が 2026-07-10 固定で「違反0」と出るため見落とした。
# よって **実日付で** 検査する tools/check_order.py を push の関所に置く。
$ErrorActionPreference = 'SilentlyContinue'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$raw = [Console]::In.ReadToEnd()
if (-not $raw) { exit 0 }
try { $data = $raw | ConvertFrom-Json } catch { exit 0 }

# git push のときだけ働く
$cmd = $data.tool_input.command
if (-not $cmd) { exit 0 }
if ($cmd -notmatch 'git\s+push') { exit 0 }

Push-Location 'C:/Users/user/oshinavi'
$out = & node tools/check_order.js 2>&1 | Out-String
$code = $LASTEXITCODE
Pop-Location

if ($code -eq 2) {
    $msg = "BLOCKED: 並び順が壊れたまま push しようとしています。`n`n" `
         + $out + "`n" `
         + "並び順ルール（memory: feedback_display_order）= 日付が早い順・同じ日なら「発売開始」が上、「締切」が下。`n" `
         + "直してから push すること。当日ヒール漏れが原因のことが多い:`n" `
         + "  python tools/heal_stale_deadlines.py --build`n" `
         + "  python tools/heal_stale_deadlines.py --apply"
    [Console]::Error.WriteLine($msg)
    exit 2
}

if ($code -eq 1) {
    # 隠れ枠あり＝警告だけ出して push は通す（削除候補待ち等が正当に残るため）
    [Console]::Error.WriteLine("※並び順は正常。ただし隠れ枠が残っています（当日ヒール漏れの可能性）:`n" + $out)
}
exit 0
