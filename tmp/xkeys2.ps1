param([string]$keys = "", [int]$x = 0, [int]$y = 0, [string]$shot = "")
# Send keys / click only when the FOREGROUND window belongs to chrome.exe (works while a native
# <select> dropdown is open, when MainWindowTitle is empty). If chrome is not in front, try to
# bring the chrome window with a title to the front first. ASCII only.
[void][Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms")
[void][Reflection.Assembly]::LoadWithPartialName("System.Drawing")
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class XK2 {
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint f, uint dx, uint dy, uint d, IntPtr e);
}
"@
function FgIsChrome {
  $pid2 = 0
  [void][XK2]::GetWindowThreadProcessId([XK2]::GetForegroundWindow(), [ref]$pid2)
  $pr = Get-Process -Id $pid2 -ErrorAction SilentlyContinue
  return ($pr -and $pr.ProcessName -eq 'chrome')
}
if (-not (FgIsChrome)) {
  $p = Get-Process chrome -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -ne '' } | Select-Object -First 1
  if ($p) { [void][XK2]::SetForegroundWindow($p.MainWindowHandle); Start-Sleep -Milliseconds 700 }
}
if (-not (FgIsChrome)) { Write-Output "ABORT: foreground is not chrome"; exit 1 }
if ($x -gt 0) {
  [void][XK2]::SetCursorPos($x, $y); Start-Sleep -Milliseconds 250
  [XK2]::mouse_event(0x0002, 0, 0, 0, [IntPtr]::Zero); [XK2]::mouse_event(0x0004, 0, 0, 0, [IntPtr]::Zero)
  Start-Sleep -Milliseconds 900
}
if ($keys -ne "") {
  if (-not (FgIsChrome)) { Write-Output "ABORT before keys: foreground is not chrome"; exit 1 }
  [System.Windows.Forms.SendKeys]::SendWait($keys); Start-Sleep -Milliseconds 900
}
if ($shot -ne "") {
  Start-Sleep -Milliseconds 700
  $b = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
  $bmp = New-Object System.Drawing.Bitmap $b.Width, $b.Height
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.CopyFromScreen($b.X, $b.Y, 0, 0, $b.Size)
  $bmp.Save($shot, [System.Drawing.Imaging.ImageFormat]::Png)
  $g.Dispose(); $bmp.Dispose()
}
Write-Output ("ok click=" + $x + "," + $y + " keys=" + $keys)
