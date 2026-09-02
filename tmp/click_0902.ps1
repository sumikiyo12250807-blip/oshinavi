# Chrome を前面に出して指定座標をクリックし、そのあと画面を撮る。
# 使い方: click_0902.ps1 <x> <y> <out.png> [clicks]
# 🚨前面が Chrome でなければ何もせず中止する（2026-09-01 のメモ帳事故の再発防止）。
param([int]$x, [int]$y, [string]$out = "C:\Users\user\oshinavi\tmp\shot.png", [int]$clicks = 1)
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;
public class C {
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint f, uint dx, uint dy, uint d, IntPtr e);
}
"@
$p = Get-Process chrome -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -ne '' } | Select-Object -First 1
if (-not $p) { Write-Output "ABORT: no chrome"; exit 1 }
[void][C]::SetForegroundWindow($p.MainWindowHandle)
Start-Sleep -Milliseconds 700
$sb = New-Object System.Text.StringBuilder 512
[void][C]::GetWindowText([C]::GetForegroundWindow(), $sb, 512)
if ($sb.ToString() -notmatch 'Google Chrome') { Write-Output ("ABORT: fg=" + $sb.ToString()); exit 1 }
if ($x -gt 0) {
  for ($i = 0; $i -lt $clicks; $i++) {
    [void][C]::SetCursorPos($x, $y)
    Start-Sleep -Milliseconds 250
    [C]::mouse_event(0x0002, 0, 0, 0, [IntPtr]::Zero)
    [C]::mouse_event(0x0004, 0, 0, 0, [IntPtr]::Zero)
    Start-Sleep -Milliseconds 700
  }
}
Start-Sleep -Milliseconds 900
$b = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bmp = New-Object System.Drawing.Bitmap $b.Width, $b.Height
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($b.X, $b.Y, 0, 0, $b.Size)
$bmp.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
Write-Output ("CLICKED " + $x + "," + $y + " x" + $clicks + " -> " + $out)
