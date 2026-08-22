# shift_guard.ps1 — 便（朝/昼/夜）のやり忘れを止める番人（2026-08-22 新設）
#
# なぜ要るか:
#   2026-08-21・08-22 と2日連続で昼のヒールと昼のpushをすっぽかした。
#   真因は「時計を一度も叩かない」こと。会話の中に時刻は流れてこないので、
#   memory や plan.md に書いても気づく手段にならない（feedback_noon_heal_missed_twice）。
#   → Stop フック＝Claudeがターンを終える瞬間に、機械が時刻を見て止める。
#
# 何を見るか（どちらも客観的な事実だけ。余計な帳簿は作らない）:
#   A 昼のヒール … tmp/heal_stale.json の更新時刻が「今日の11:00以降」か
#   B 昼のpush   … 未pushコミットがあるのに origin/main の先端が「今日の11:00以降」でないか
#
# 鳴り方: 条件ごとに 1日1回だけ exit 2 でブロックする（.claude/state/ に印）。
#         2回目からは黙る＝作業の邪魔をしない（newpool_guard と同じ考え方）。
#
# ⚠️このファイルは **UTF-8 BOM付き・CRLF** で保存すること。
#   BOM無しだと PowerShell 5.1 が ANSI として読んで日本語が化ける。
#   ヒアストリング（@"..."@）は LF 混在で壊れるので使わない。

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$repo = 'C:/Users/user/oshinavi'
$state = Join-Path $repo '.claude/state'
if (-not (Test-Path $state)) { New-Item -ItemType Directory -Force -Path $state | Out-Null }

$now = Get-Date
$today = $now.Date
$eleven = $today.AddHours(11)
$stamp = $now.ToString('yyyyMMdd')
$nowStr = $now.ToString('HH:mm')

function Already([string]$key) {
  return (Test-Path (Join-Path $state ("shift_" + $key + "_" + $stamp + ".txt")))
}
function Mark([string]$key) {
  Set-Content -Path (Join-Path $state ("shift_" + $key + "_" + $stamp + ".txt")) -Value $nowStr -Encoding UTF8
}

$msgs = @()

# ---------- A 昼のヒール ----------
# 12時を過ぎたら見る。23:30を過ぎたら今日はもう手遅れなので黙る（夜の締めの邪魔をしない）。
if ($now.Hour -ge 12 -and $now -lt $today.AddHours(23).AddMinutes(30) -and -not (Already 'heal')) {
  $healJson = Join-Path $repo 'tmp/heal_stale.json'
  $healOk = $false
  if (Test-Path $healJson) {
    if ((Get-Item $healJson).LastWriteTime -ge $eleven) { $healOk = $true }
  }
  if (-not $healOk) {
    $a = @()
    $a += '🚨 昼の隠れ枠ヒールが今日まだ済んでいません（今 ' + $nowStr + '）。'
    $a += '   tmp/heal_stale.json が「今日の11:00以降」に更新されていない＝--build を回していないということ。'
    $a += ''
    $a += '   ぴあは発売時刻を過ぎてから締切を出すので、朝のヒールだけだと'
    $a += '   当日発売の枠が「本日発売」のまま締切なしで残ります（memory: feedback_harvest_today_sale_enddate）。'
    $a += ''
    $a += '   やること:'
    $a += '     python tools/heal_stale_deadlines.py --build'
    $a += '     python tools/heal_stale_deadlines.py --apply'
    $a += '     node tools/check_order.js'
    $a += '   ※その日いちばん遅い当日発売時刻（例 18:00）より後に回すのが正解。'
    $msgs += ($a -join "`n")
    Mark 'heal'
  }
}

# ---------- B 昼のpush ----------
if ($now.Hour -ge 13 -and -not (Already 'push')) {
  $unpushed = @()
  $tip = ''
  try {
    $unpushed = @(& git -C $repo log --oneline origin/main..HEAD 2>$null)
    $tip = (& git -C $repo log -1 --format=%cI origin/main 2>$null)
  } catch { }
  if ($unpushed.Count -gt 0) {
    $pushedRecently = $false
    if ($tip) {
      try {
        if ([datetime]::Parse($tip) -ge $eleven) { $pushedRecently = $true }
      } catch { }
    }
    if (-not $pushedRecently) {
      $b = @()
      $b += '🚨 未pushコミットが ' + $unpushed.Count + ' 本あり、今日の11:00以降のpushがありません（今 ' + $nowStr + '）。'
      $b += '   pushは朝・昼・夜の3回が約束です（memory: feedback_push）。'
      $b += '   ユーザーは携帯からサイトを見ているので、昼を飛ばすとその日の成果が夕方まで届きません。'
      $b += ''
      $b += '   やること（push直前のゲートを忘れずに）:'
      $b += '     python tools/build_ai_page.py         # EVENTSを触ったなら必須'
      $b += '     python tools/reconcile_pia.py --new   # push直前に必ず'
      $b += '     node tools/check_zero_badge.js'
      $b += '     git push origin main'
      $msgs += ($b -join "`n")
      Mark 'push'
    }
  }
}

if ($msgs.Count -gt 0) {
  [Console]::Error.WriteLine(($msgs -join "`n`n"))
  [Console]::Error.WriteLine('')
  [Console]::Error.WriteLine('（この警告は条件ごとに1日1回だけ出ます。片付けてから締めてください。）')
  exit 2
}
exit 0
