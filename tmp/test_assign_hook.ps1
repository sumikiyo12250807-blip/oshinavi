# assign_approval.ps1 が実際のユーザー発言で解錠できるかを検証する
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$hook = 'C:/Users/user/oshinavi/.claude/hooks/assign_approval.ps1'
$approve = 'C:/Users/user/oshinavi/.claude/state/assign_approved.txt'

$cases = @(
    '今日販売はいつまでか出てるのあるし、うりきれたのもあるよ　それ確認して直して　振り分けてOK',
    '振り分けて',
    '振り分けOK',
    'いいよ'
)

foreach ($c in $cases) {
    if (Test-Path $approve) { Remove-Item $approve -Force }
    $json = @{ prompt = $c } | ConvertTo-Json -Compress
    $json | & powershell -NoProfile -ExecutionPolicy Bypass -File $hook
    $got = if (Test-Path $approve) { (Get-Content $approve -Raw).Trim() } else { '(解錠されず)' }
    Write-Output ("[{0}] -> {1}" -f $c.Substring(0, [Math]::Min(28, $c.Length)), $got)
}

# newpool_guard 側の日付比較がBOMで壊れていないかも確認
Write-Output ''
Write-Output '--- newpool_guard の日付比較テスト ---'
$today = (Get-Date).ToString('yyyy-MM-dd')
if (Test-Path $approve) {
    $raw = (Get-Content $approve -Raw).Trim()
    $bytes = [System.IO.File]::ReadAllBytes($approve)
    $head = ($bytes[0..2] | ForEach-Object { $_.ToString('x2') }) -join ''
    Write-Output ("ファイル先頭3バイト: {0} (efbbbf ならBOM付き)" -f $head)
    Write-Output ("読んだ値 == 今日 ? : {0}" -f ($raw -eq $today))
}
