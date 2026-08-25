#requires -version 5
# X予約を1本ぶん進める（2026-08-24）。
# 使い方: powershell -File tmp/x_schedule_one.ps1 -Index 2 -Hour 20 -Minute 31 -Step post|paste|clock|time|confirm|schedule
#
# 🚨 memory: feedback_x_browser_operation / _addendum_0822
#   ・🕐と Schedule は1回目がホバー扱いで効かない＝押す→撮る→もう1回押す
#   ・押す前に必ず撮ってボタンの文字を読む（Post と Schedule の取り違え防止）
#   ・ズーム80%基準。y=95〜115 のクリックはブックマークを踏むので厳禁
param(
  [int]$Index = 1,
  [int]$Hour = 20,
  [int]$Minute = 1,
  [string]$Step = 'shot',
  [string]$Shot = 'z'
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms, System.Drawing
$sig = @"
using System;
using System.Runtime.InteropServices;
public class XOP {
  [DllImport("user32.dll")] public static extern void mouse_event(uint f, uint x, uint y, uint d, int e);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
}
"@
if (-not ([System.Management.Automation.PSTypeName]'XOP').Type) { Add-Type -TypeDefinition $sig }

$dir = 'C:\Users\user\AppData\Local\Temp\claude\C--Users-user-oshinavi\94b93ec7-9f5a-49dd-8bf2-88bbe2400940\scratchpad'

function Front {
  $p = Get-Process chrome | Where-Object { $_.MainWindowTitle -ne '' } | Select-Object -First 1
  if ($p) { [XOP]::SetForegroundWindow($p.MainWindowHandle) | Out-Null; Start-Sleep -Milliseconds 400 }
}
function Click($x, $y) {
  [XOP]::SetCursorPos($x, $y); Start-Sleep -Milliseconds 250
  [XOP]::mouse_event(0x0002, 0, 0, 0, 0); [XOP]::mouse_event(0x0004, 0, 0, 0, 0)
  Start-Sleep -Milliseconds 600
}
function Shot($name) {
  Start-Sleep -Milliseconds 1200
  $b = New-Object System.Drawing.Bitmap 1366, 768
  $g = [System.Drawing.Graphics]::FromImage($b)
  $g.CopyFromScreen(0, 0, 0, 0, $b.Size)
  $b.Save((Join-Path $dir ($name + '.png')))
  Write-Output ('shot -> ' + $name + '.png')
}

Front
switch ($Step) {
  'post'     { Click 269 611; Shot $Shot }
  'paste'    {
    Get-Content ("C:\Users\user\oshinavi\tmp\xpost_$Index.txt") -Raw -Encoding UTF8 | Set-Clipboard
    Click 650 275
    Start-Sleep -Milliseconds 400
    [System.Windows.Forms.SendKeys]::SendWait('^v')
    Shot $Shot
  }
  'clock'    { Click 625 671; Shot $Shot }
  'time'     {
    Click 656 408
    Start-Sleep -Milliseconds 400
    [System.Windows.Forms.SendKeys]::SendWait(('{0:D2}' -f $Minute))
    Start-Sleep -Milliseconds 400
    [System.Windows.Forms.SendKeys]::SendWait('{ENTER}')
    Shot $Shot
  }
  'hourup'   { Click 519 408; Start-Sleep -Milliseconds 300; [System.Windows.Forms.SendKeys]::SendWait('{UP}'); Start-Sleep -Milliseconds 300; [System.Windows.Forms.SendKeys]::SendWait('{ENTER}'); Shot $Shot }
  'hourdown' { Click 519 408; Start-Sleep -Milliseconds 300; [System.Windows.Forms.SendKeys]::SendWait('{DOWN}'); Start-Sleep -Milliseconds 300; [System.Windows.Forms.SendKeys]::SendWait('{ENTER}'); Shot $Shot }
  'confirm'  { Click 873 225; Shot $Shot }
  'schedule' { Click 854 671; Shot $Shot }
  default    { Shot $Shot }
}
