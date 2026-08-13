# Stop hook: Claude の発話に禁止二人称が含まれていたらブロックする番人。
# memory: feedback_tone_onee（二人称は省略する）を機械的に強制する。
#
# 【2026-08-10 全面改修】旧版が6回目の再発を素通りさせた真因を実ログで特定した：
#   ①stop_hook_summary の session_id が /clear 前の旧セッション（c913dd49）を指しており、
#     Stop hook に渡る transcript_path が**別セッションのログ**だった。旧ログの末尾は当然きれいなので
#     常に exit 0 ＝ 番人はずっと空振りしていた。→ transcript_path を鵜呑みにせず、
#     「直近に更新された .jsonl」を自分で選び直す。
#   ②旧版は「最後の assistant テキスト1件」しか見なかった。ツール呼び出しの合間に出す地の文
#     （報告の途中）は判定対象外＝過去の再発（1ターンで10回以上）の大半を取りこぼしていた。
#     → 直近のユーザー発言以降の assistant テキストを**全部**見る。
# 同じ違反で無限にブロックし続けないよう、通知済み uuid を state に記録する。
$ErrorActionPreference = 'Stop'

function Get-Texts($obj) {
    $out = @()
    $content = $obj.message.content
    if (-not $content) { return $out }
    if ($content -is [string]) { $out += $content; return $out }
    foreach ($b in $content) { if ($b.type -eq 'text' -and $b.text) { $out += $b.text } }
    return $out
}

try {
    $raw = [Console]::In.ReadToEnd()
    $data = $null
    if ($raw) { try { $data = $raw | ConvertFrom-Json } catch { $data = $null } }

    # --- 1. 見るべきトランスクリプトを決める -------------------------------
    # transcript_path は /clear をまたぐと旧セッションを指すことがある（実測済）。
    # 渡された path があってもディレクトリだけ借りて、最終更新が一番新しい .jsonl を採用する。
    $tp = $null
    if ($data -and $data.transcript_path) { $tp = $data.transcript_path }

    $dir = $null
    if ($tp -and (Test-Path -LiteralPath $tp)) { $dir = Split-Path -Parent $tp }
    if (-not $dir) {
        $cwd = if ($data -and $data.cwd) { $data.cwd } else { (Get-Location).Path }
        $slug = ($cwd -replace '[:\\/]', '-')
        $cand = Join-Path $env:USERPROFILE ".claude\projects\$slug"
        if (Test-Path -LiteralPath $cand) { $dir = $cand }
    }
    if (-not $dir) { exit 0 }

    $newest = Get-ChildItem -LiteralPath $dir -Filter '*.jsonl' -ErrorAction SilentlyContinue |
              Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $newest) { exit 0 }
    $tp = $newest.FullName

    # --- 2. 直近のユーザー発言以降の assistant テキストを全部集める ---------
    $lines = Get-Content -LiteralPath $tp -Encoding UTF8
    $msgs = @()   # @{ uuid; text }
    for ($i = $lines.Count - 1; $i -ge 0; $i--) {
        $ln = $lines[$i]
        if (-not $ln -or -not $ln.Trim()) { continue }
        try { $obj = $ln | ConvertFrom-Json } catch { continue }

        if ($obj.type -eq 'user') {
            # tool_result はユーザーの発言ではない。本物のユーザー入力が来たらそこで打ち切る。
            $c = $obj.message.content
            $isReal = $true
            if ($c -and -not ($c -is [string])) {
                $types = @($c | ForEach-Object { $_.type })
                if ($types -contains 'tool_result') { $isReal = $false }
            }
            if ($isReal) { break }
            continue
        }
        if ($obj.type -ne 'assistant') { continue }
        $t = Get-Texts $obj
        if ($t.Count -gt 0) { $msgs += @{ uuid = [string]$obj.uuid; text = ($t -join "`n") } }
    }
    if ($msgs.Count -eq 0) { exit 0 }

    # --- 3. 判定（通知済みは再ブロックしない） ------------------------------
    $needle = -join ([char]0x3042, [char]0x3093, [char]0x305F)   # 禁止二人称
    $stateDir = Join-Path (Split-Path -Parent (Split-Path -Parent $PSCommandPath)) 'state'
    if (-not (Test-Path -LiteralPath $stateDir)) { New-Item -ItemType Directory -Force -Path $stateDir | Out-Null }
    $seenFile = Join-Path $stateDir 'tone_seen.txt'
    $seen = @()
    if (Test-Path -LiteralPath $seenFile) { $seen = @(Get-Content -LiteralPath $seenFile -Encoding UTF8) }

    $fresh = @()
    $total = 0
    foreach ($m in $msgs) {
        if (-not $m.text.Contains($needle)) { continue }
        $total += ([regex]::Matches($m.text, $needle)).Count
        if ($seen -notcontains $m.uuid) { $fresh += $m.uuid }
    }

    if ($fresh.Count -gt 0) {
        ($seen + $fresh) | Select-Object -Last 200 | Set-Content -LiteralPath $seenFile -Encoding UTF8
        $msg = 'BLOCKED: 禁止された二人称を' + $total + '回使っている(memory: feedback_tone_onee)。' +
               '二人称は省略して書き直して。主語ごと落とすのが確実（「〜してもらえたら」「〜はどうする？」）。' +
               '検出範囲=直近のユーザー発言以降の全発話。'
        [Console]::Error.WriteLine($msg)
        exit 2
    }
    exit 0
}
catch {
    # 番人自体のエラーで作業を止めない（フェイルオープン）
    exit 0
}
