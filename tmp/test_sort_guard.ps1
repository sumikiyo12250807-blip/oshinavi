# 並び順ロジックの番人(sort_guard)と鍵(sort_approval)が働くかテストする。
$ErrorActionPreference = 'Continue'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
# native コマンドへパイプする時のエンコーディング。これが cp932 のままだと日本語が壊れて
# 鍵の判定が誤爆する（テスト側だけの都合。本番は Claude Code が hook に直接 JSON を渡す）
$OutputEncoding = [System.Text.Encoding]::UTF8
$g = 'C:/Users/user/oshinavi/.claude/hooks/sort_guard.ps1'
$a = 'C:/Users/user/oshinavi/.claude/hooks/sort_approval.ps1'
$state = 'C:/Users/user/oshinavi/.claude/state'
$hash = "$state/sort_hash.txt"
$ok = "$state/sort_approved.txt"
$idx = 'C:/Users/user/oshinavi/index.html'
$save = 'C:/Users/user/oshinavi/tmp/_idx_sortguard.html'
$fail = 0

function Run-Guard { & powershell -NoProfile -ExecutionPolicy Bypass -File $g 2>$null | Out-Null; return $LASTEXITCODE }
# JSON は文字列リテラルで組む（ConvertTo-Json 経由だとパイプで日本語が壊れて誤判定する）
function Say($t) { ('{"prompt":"' + $t + '"}') | powershell -NoProfile -ExecutionPolicy Bypass -File $a }

Copy-Item $idx $save -Force
Remove-Item $hash, $ok -ErrorAction SilentlyContinue

try {
    Write-Host "=== 1) 初回は指紋を記録して通る ==="
    $c = Run-Guard
    if ($c -eq 0) { Write-Host "  OK: exit 0" } else { Write-Host "  NG: exit $c"; $fail++ }

    Write-Host "`n=== 2) 触らなければ通る ==="
    $c = Run-Guard
    if ($c -eq 0) { Write-Host "  OK: exit 0" } else { Write-Host "  NG: exit $c"; $fail++ }

    Write-Host "`n=== 3) 並び順ロジックを改造したらブロック（7/19の事故の再現）==="
    $t = [System.IO.File]::ReadAllText($idx, [System.Text.UTF8Encoding]::new($false))
    $broken = $t.Replace('if (ca.kind !== cb.kind) return ca.kind - cb.kind;', 'if (ca.kind !== cb.kind) return cb.kind - ca.kind;')
    [System.IO.File]::WriteAllText($idx, $broken, [System.Text.UTF8Encoding]::new($false))
    $c = Run-Guard
    if ($c -eq 2) { Write-Host "  OK: exit 2 でブロック" } else { Write-Host "  NG: exit $c（止まらなかった）"; $fail++ }

    Write-Host "`n=== 4) 「並び順がおかしい」では鍵は開かない（直せ、であって改造しろ、ではない）==="
    Remove-Item $ok -ErrorAction SilentlyContinue
    Say '並び順がおかしい　今日に近い順だよ' | Out-Null
    if (Test-Path $ok) { Write-Host "  NG: 開いてしまった"; $fail++ } else { Write-Host "  OK: 開かない" }

    Write-Host "`n=== 5) 「並び順を変えて」なら鍵が開く ==="
    Say '並び順のルールを変えて' | Out-Null
    if (Test-Path $ok) { Write-Host "  OK: 承認印あり" } else { Write-Host "  NG: 開かない"; $fail++ }

    Write-Host "`n=== 6) 承認後は改造が通る ==="
    $c = Run-Guard
    if ($c -eq 0) { Write-Host "  OK: exit 0" } else { Write-Host "  NG: exit $c"; $fail++ }
}
finally {
    Copy-Item $save $idx -Force
    Remove-Item $save -ErrorAction SilentlyContinue
    Remove-Item $hash, $ok -ErrorAction SilentlyContinue
    & powershell -NoProfile -ExecutionPolicy Bypass -File $g 2>$null | Out-Null
}

Write-Host "`n===================="
if ($fail -eq 0) { Write-Host "全テスト合格" } else { Write-Host "失敗 $fail 件" }
