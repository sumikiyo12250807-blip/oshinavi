param([string]$out = "C:\Users\user\oshinavi\tmp\xshot.png", [int]$x = 0, [int]$y = 0, [int]$clicks = 0)
# Bring Chrome to front, optionally click (x,y) N times, then take a full-screen shot.
# Aborts if the foreground window is not Chrome. ASCII only.
[void][Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms")
[void][Reflection.Assembly]::LoadWithPartialName("System.Drawing")
Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;
public class XS {
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
[void][XS]::SetForegroundWindow($p.MainWindowHandle)
Start-Sleep -Milliseconds 700
$sb = New-Object System.Text.StringBuilder 512
[void][XS]::GetWindowText([XS]::GetForegroundWindow(), $sb, 512)
if ($sb.ToString() -notmatch 'Google Chrome') { Write-Output ("ABORT: fg=" + $sb.ToString()); exit 1 }
for ($i = 0; $i -lt $clicks; $i++) {
  [void][XS]::SetCursorPos($x, $y)
  Start-Sleep -Milliseconds 250
  [XS]::mouse_event(0x0002, 0, 0, 0, [IntPtr]::Zero)
  [XS]::mouse_event(0x0004, 0, 0, 0, [IntPtr]::Zero)
  Start-Sleep -Milliseconds 800
}
Start-Sleep -Milliseconds 900
$b = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bmp = New-Object System.Drawing.Bitmap $b.Width, $b.Height
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($b.X, $b.Y, 0, 0, $b.Size)
$bmp.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
Write-Output ("OK fg=" + $sb.ToString() + " size=" + $b.Width + "x" + $b.Height + " -> " + $out)
