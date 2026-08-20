# push前の並び順ガードが本当に働くかテストする。
$ErrorActionPreference = 'Continue'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$g = 'C:/Users/user/oshinavi/.claude/hooks/push_order_guard.ps1'
$fail = 0

function Try-Cmd($cmd) {
    $json = @{ tool_input = @{ command = $cmd } } | ConvertTo-Json -Compress
    $json | powershell -NoProfile -ExecutionPolicy Bypass -File $g 2>$null | Out-Null
    return $LASTEXITCODE
}

Write-Host "=== 1) git push 以外は素通り（git status）==="
$c = Try-Cmd 'git status'
if ($c -eq 0) { Write-Host "  OK: exit 0" } else { Write-Host "  NG: exit $c"; $fail++ }

Write-Host "`n=== 2) 今の並びは正常なので git push は通る ==="
$c = Try-Cmd 'git push origin main'
if ($c -eq 0) { Write-Host "  OK: exit 0（通過）" } else { Write-Host "  NG: exit $c"; $fail++ }

Write-Host "`n=== 3) 7/19の事故を再現（今日発売の枠を隠れ枠に戻す）→ git push は止まる ==="
$idx = 'C:/Users/user/oshinavi/index.html'
$save = 'C:/Users/user/oshinavi/tmp/_index_pushguard_test.html'
Copy-Item $idx $save -Force
try {
    # 当日ヒール前の状態を再現＝今日発売の枠の締切を発売日と同じに戻す（startDate==date）。
    # こうすると「本日発売🔵」が締切扱いになり、先頭から消える＝7/19に起きたことそのもの。
    $py = @'
import re,io,sys,datetime
p='C:/Users/user/oshinavi/index.html'
t=io.open(p,encoding='utf-8').read()
today=datetime.date.today().isoformat()
# "startDate": "今日" を持つ枠の直前の "date" を今日に書き換える
t,n=re.subn(r'"startDate": "'+today+r'",(\s*)"date": "\d{4}-\d{2}-\d{2}"', '"startDate": "'+today+r'",\1"date": "'+today+'"', t)
io.open(p,'w',encoding='utf-8').write(t)
print('隠れ枠に戻した', n, '枠')
'@
    $py | Out-File -FilePath 'C:/Users/user/oshinavi/tmp/_break.py' -Encoding utf8
    & python 'C:/Users/user/oshinavi/tmp/_break.py' | Out-Null
    $c = Try-Cmd 'git push origin main'
    if ($c -eq 2) { Write-Host "  OK: exit 2 でブロック" } else { Write-Host "  NG: exit $c（止まらなかった）"; $fail++ }
}
finally {
    Copy-Item $save $idx -Force
    Remove-Item $save -ErrorAction SilentlyContinue
}

Write-Host "`n=== 4) 復元後、また通る ==="
$c = Try-Cmd 'git push origin main'
if ($c -eq 0) { Write-Host "  OK: exit 0" } else { Write-Host "  NG: exit $c"; $fail++ }

Write-Host "`n===================="
if ($fail -eq 0) { Write-Host "全テスト合格" } else { Write-Host "失敗 $fail 件" }
