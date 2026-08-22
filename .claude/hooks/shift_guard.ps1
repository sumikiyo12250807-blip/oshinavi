# shift_guard.ps1 — 便（朝/昼/夜）のやり忘れを止める番人（2026-08-22 新設）
#
# なぜ要るか:
#   2026-08-21・08-22 と2日連続で昼のヒールと昼のpushをすっぽかした。
#   真因は「時計を一度も叩かない」こと。会話の中に時刻は流れてこないので、
#   memory や plan.md に書いても気づく手段にならない（feedback_noon_heal_missed_twice）。
#   → Stop フック＝Claudeがターンを終える瞬間に、機械が時刻を見て止める。
#
# 便の形（feedback_push / PLAYBOOK）:
#   朝＝朝ルーチンの成果 ／ 昼＝**昼ヒールの後**（14時ごろ）／ 夜＝その日の残り
#   「3回」は回数ではなく**時間帯の枠**。同じ枠で2回押すのは前借り（2026-08-20 の叱られ）。
#
# いつ鳴るか＝**その日の最遅の当日発売時刻＋30分**から（下限12:30）。
#   ぴあは発売時刻を過ぎてから締切を出すので、14:00発売がある日は14:30以降が正しい昼便
#   （feedback_harvest_today_sale_enddate）。実データから読むので日によって自動で動く。
#
# 何を見るか（客観的な事実だけ。自己申告の帳簿は作らない）:
#   A 昼のヒール … tmp/heal_stale.json の更新時刻が「今日の昼便の開始時刻以降」か
#   B 昼のpush   … 未pushコミットがあるのに origin/main の先端が同じ時刻以降でないか
#
# 鳴り方: 条件ごとに 1日1回だけ exit 2 でブロック（.claude/state/ に印）。
#
# ⚠️このファイルは UTF-8 BOM付き・CRLF で保存すること（PowerShell 5.1 が ANSI と誤読する）。
#   ヒアストリング（@"..."@）は LF 混在で壊れるので使わない。

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$repo = 'C:/Users/user/oshinavi'
$state = Join-Path $repo '.claude/state'
if (-not (Test-Path $state)) { New-Item -ItemType Directory -Force -Path $state | Out-Null }

$now = Get-Date
$today = $now.Date
$stamp = $now.ToString('yyyyMMdd')
$nowStr = $now.ToString('HH:mm')

# ---------- 今日の昼便が始まってよい時刻を実データから決める ----------
# index.html のバッジ文言「M/D HH:MM発売」のうち、M/D が今日のものの最遅時刻＋30分。
$noonStart = $today.AddHours(12).AddMinutes(30)
$latestSale = ''
try {
  $idx = Join-Path $repo 'index.html'
  if (Test-Path $idx) {
    $md = [string]$now.Month + '/' + [string]$now.Day
    $txt = [System.IO.File]::ReadAllText($idx, [System.Text.Encoding]::UTF8)
    $pat = [regex]::Escape($md) + ' (\d{1,2}):(\d{2})発売'
    $best = $null
    foreach ($m in [regex]::Matches($txt, $pat)) {
      $t = $today.AddHours([int]$m.Groups[1].Value).AddMinutes([int]$m.Groups[2].Value)
      if ($null -eq $best -or $t -gt $best) { $best = $t }
    }
    if ($best) {
      $latestSale = $best.ToString('HH:mm')
      # 🚨15時より後の発売は「昼便」の仕事ではなく夜便の仕事。ここで頭を打つ。
      #   （実データで最遅20:00の日があり、上限を入れないと昼便の開始が20:30になって意味が崩れた）
      $cap = $today.AddHours(15)
      if ($best -gt $cap) { $best = $cap }
      $cand = $best.AddMinutes(30)
      if ($cand -gt $noonStart) { $noonStart = $cand }
    }
  }
} catch { }

function Already([string]$key) {
  return (Test-Path (Join-Path $state ("shift_" + $key + "_" + $stamp + ".txt")))
}
function Mark([string]$key) {
  Set-Content -Path (Join-Path $state ("shift_" + $key + "_" + $stamp + ".txt")) -Value $nowStr -Encoding UTF8
}

$msgs = @()
$why = '（今日の最遅の当日発売は ' + $(if ($latestSale) { $latestSale } else { '無し' }) + ' なので、昼便は ' + $noonStart.ToString('HH:mm') + ' 以降）'

# ---------- A 昼のヒール ----------
# 昼便の開始時刻を過ぎたら見る。23:30を過ぎたら今日はもう手遅れなので黙る（夜の締めの邪魔をしない）。
if ($now -ge $noonStart -and $now -lt $today.AddHours(23).AddMinutes(30) -and -not (Already 'heal')) {
  $healJson = Join-Path $repo 'tmp/heal_stale.json'
  $healOk = $false
  if (Test-Path $healJson) {
    if ((Get-Item $healJson).LastWriteTime -ge $noonStart) { $healOk = $true }
  }
  if (-not $healOk) {
    $a = @()
    $a += '🚨 昼の隠れ枠ヒールが今日まだ済んでいません（今 ' + $nowStr + '）。' + $why
    $a += '   tmp/heal_stale.json がその時刻以降に更新されていない＝--build を回していないということ。'
    $a += ''
    $a += '   ぴあは発売時刻を過ぎてから締切を出すので、朝のヒールだけだと'
    $a += '   当日発売の枠が「本日発売」のまま締切なしで残ります（memory: feedback_harvest_today_sale_enddate）。'
    $a += ''
    $a += '   やること:'
    $a += '     python tools/heal_stale_deadlines.py --build'
    $a += '     python tools/heal_stale_deadlines.py --apply'
    $a += '     node tools/check_order.js'
    $msgs += ($a -join "`n")
    Mark 'heal'
  }
}

# ---------- B 昼のpush（昼ヒールの後・14時ごろ） ----------
if ($now -ge $noonStart.AddMinutes(30) -and -not (Already 'push')) {
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
        if ([datetime]::Parse($tip) -ge $noonStart) { $pushedRecently = $true }
      } catch { }
    }
    if (-not $pushedRecently) {
      $b = @()
      $b += '🚨 未pushコミットが ' + $unpushed.Count + ' 本あり、昼便のpushがまだです（今 ' + $nowStr + '）。' + $why
      $b += '   pushは朝・昼・夜の3回。2回目は**昼ヒールの後**（14時ごろ）が定位置です（memory: feedback_push）。'
      $b += '   「3回」は回数ではなく時間帯の枠＝夜に2回押すのは枠の前借りです（2026-08-20 の叱られ）。'
      $b += '   ユーザーは携帯からサイトを見ているので、昼を飛ばすとその日の成果が夜まで届きません。'
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
