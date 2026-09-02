# Chrome を前面に出して画面を撮る。
# 🚨2026-09-01の事故＝Chromeを掴む処理が失敗したのに後続のキー送信だけ走り、
#   ユーザーが編集中のメモ帳に Ctrl+A→Ctrl+V を撃ち込んだ。
#   SetForegroundWindow のあと GetForegroundWindow でタイトルを読み、Chrome でなければ即中止する。
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;
public class W {
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
}
"@
$p = Get-Process chrome -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -ne '' } | Select-Object -First 1
if (-not $p) { Write-Output "ABORT: chrome window not found"; exit 1 }
[void][W]::ShowWindow($p.MainWindowHandle, 9)
[void][W]::SetForegroundWindow($p.MainWindowHandle)
Start-Sleep -Milliseconds 900
$fg = [W]::GetForegroundWindow()
$sb = New-Object System.Text.StringBuilder 512
[void][W]::GetWindowText($fg, $sb, 512)
$t = $sb.ToString()
if ($t -notmatch 'Google Chrome') { Write-Output ("ABORT: foreground is not Chrome -> " + $t); exit 1 }
Write-Output ("FG_OK: " + $t)
$b = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bmp = New-Object System.Drawing.Bitmap $b.Width, $b.Height
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($b.X, $b.Y, 0, 0, $b.Size)
$out = $args[0]
if (-not $out) { $out = "C:\Users\user\oshinavi\tmp\shot_0902.png" }
$bmp.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
Write-Output ("SAVED: " + $out)
