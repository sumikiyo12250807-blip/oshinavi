# 番人(newpool_guard.ps1)と鍵(assign_approval.ps1)が本当に働くかテストする。
# 本番の index.html は触らず、退避→ダミー→復元でやる。
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$root  = 'C:/Users/user/oshinavi'
$guard = "$root/.claude/hooks/newpool_guard.ps1"
$appr  = "$root/.claude/hooks/assign_approval.ps1"
$state = "$root/.claude/state"
$cnt   = "$state/newpool_count.txt"
$ok    = "$state/assign_approved.txt"
$index = "$root/index.html"
$save  = "$root/tmp/_index_saved_for_test.html"

function Run-Guard {
    # 番人は stderr にメッセージを出して exit 2 する。ここでは終了コードだけ見る
    # （native の stderr を拾うと NativeCommandError になるので捨てる）
    $ErrorActionPreference = 'Continue'
    & powershell -NoProfile -ExecutionPolicy Bypass -File $guard 2>$null | Out-Null
    $c = $LASTEXITCODE
    $ErrorActionPreference = 'Stop'
    return $c
}
function Make-Index([int]$n) {
    $sb = New-Object System.Text.StringBuilder
    for ($i = 0; $i -lt $n; $i++) { [void]$sb.AppendLine('    "genre": "new",') }
    Set-Content -Path $index -Value $sb.ToString() -Encoding utf8
}

Copy-Item $index $save -Force
Remove-Item $cnt, $ok -ErrorAction SilentlyContinue
$fail = 0

try {
    Write-Host "`n=== 1) 初回47件を記録（通るはず）==="
    Make-Index 47
    $c = Run-Guard
    if ($c -eq 0) { Write-Host "  OK: exit 0" } else { Write-Host "  NG: exit $c"; $fail++ }

    Write-Host "`n=== 2) 47→0（振り分け事故の再現・ブロックされるはず）==="
    Make-Index 0
    $c = Run-Guard
    if ($c -eq 2) { Write-Host "  OK: exit 2 でブロック" } else { Write-Host "  NG: exit $c"; $fail++ }

    Write-Host "`n=== 3) 47→44（統合で3件減・通るはず）==="
    Set-Content -Path $cnt -Value 47 -Encoding utf8
    Make-Index 44
    $c = Run-Guard
    if ($c -eq 0) { Write-Host "  OK: exit 0" } else { Write-Host "  NG: exit $c"; $fail++ }

    Write-Host "`n=== 4) ユーザーが『振り分けて』と言う→鍵が開く ==="
    $json = '{"prompt":"新着チェックしたわ、振り分けてちょうだい"}'
    $json | powershell -NoProfile -ExecutionPolicy Bypass -File $appr
    if (Test-Path $ok) {
        $v = (Get-Content $ok -Raw).Trim()
        if ($v -eq (Get-Date).ToString('yyyy-MM-dd')) { Write-Host "  OK: 承認印=$v" } else { Write-Host "  NG: $v"; $fail++ }
    } else { Write-Host "  NG: 承認印が作られない"; $fail++ }

    Write-Host "`n=== 5) 承認あり→47→0でも通る（正当な振り分け）==="
    Set-Content -Path $cnt -Value 47 -Encoding utf8
    Make-Index 0
    $c = Run-Guard
    if ($c -eq 0) { Write-Host "  OK: exit 0" } else { Write-Host "  NG: exit $c"; $fail++ }

    Write-Host "`n=== 6) 曖昧な『いいよ』では鍵が開かない ==="
    Remove-Item $ok -ErrorAction SilentlyContinue
    '{"prompt":"うん、いいよ"}' | powershell -NoProfile -ExecutionPolicy Bypass -File $appr | Out-Null
    if (Test-Path $ok) { Write-Host "  NG: 開いてしまった"; $fail++ } else { Write-Host "  OK: 開かない" }

    Write-Host "`n=== 7) 削除OKでも振り分けの鍵は開かない ==="
    '{"prompt":"削除OK"}' | powershell -NoProfile -ExecutionPolicy Bypass -File $appr | Out-Null
    if (Test-Path $ok) { Write-Host "  NG: 開いてしまった"; $fail++ } else { Write-Host "  OK: 開かない" }
}
finally {
    Copy-Item $save $index -Force
    Remove-Item $save -ErrorAction SilentlyContinue
    Remove-Item $cnt, $ok -ErrorAction SilentlyContinue
    # 本番の現在値で記録し直す
    powershell -NoProfile -ExecutionPolicy Bypass -File $guard | Out-Null
}

Write-Host "`n===================="
if ($fail -eq 0) { Write-Host "全テスト合格" } else { Write-Host "失敗 $fail 件" }
