param([int]$x = 680, [int]$y = 500, [int]$notches = -5, [string]$shot = "")
# Mouse wheel over (x,y) when chrome is in front, then optional shot. ASCII only.
[void][Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms")
[void][Reflection.Assembly]::LoadWithPartialName("System.Drawing")
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class XW {
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint f, uint dx, uint dy, int d, IntPtr e);
}
"@
$pid2 = 0
[void][XW]::GetWindowThreadProcessId([XW]::GetForegroundWindow(), [ref]$pid2)
$pr = Get-Process -Id $pid2 -ErrorAction SilentlyContinue
if (-not ($pr -and $pr.ProcessName -eq 'chrome')) { Write-Output "ABORT: fg not chrome"; exit 1 }
[void][XW]::SetCursorPos($x, $y); Start-Sleep -Milliseconds 200
[XW]::mouse_event(0x0800, 0, 0, 120 * $notches, [IntPtr]::Zero)
Start-Sleep -Milliseconds 1200
if ($shot -ne "") {
  $b = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
  $bmp = New-Object System.Drawing.Bitmap $b.Width, $b.Height
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.CopyFromScreen($b.X, $b.Y, 0, 0, $b.Size)
  $bmp.Save($shot, [System.Drawing.Imaging.ImageFormat]::Png)
  $g.Dispose(); $bmp.Dispose()
}
Write-Output "wheel ok"
