param([string]$action = "open", [string]$url = "https://x.com/home")
# Chrome helper. ASCII only.
#  open   : maximize Chrome, new tab (Ctrl+T), paste URL from clipboard, Enter
#  paste  : Esc, "n" (new post, caret in textbox), Ctrl+V   (clipboard must already hold the post)
#  keys   : send the raw SendKeys string given in -url
[void][Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms")
Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;
public class XK {
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
}
"@
$p = Get-Process chrome -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -ne '' } | Select-Object -First 1
if (-not $p) { Write-Output "ABORT: no chrome"; exit 1 }
if ($action -eq "open") { [void][XK]::ShowWindow($p.MainWindowHandle, 3) }
[void][XK]::SetForegroundWindow($p.MainWindowHandle)
Start-Sleep -Milliseconds 800
$sb = New-Object System.Text.StringBuilder 512
[void][XK]::GetWindowText([XK]::GetForegroundWindow(), $sb, 512)
if ($sb.ToString() -notmatch 'Google Chrome') { Write-Output ("ABORT: fg=" + $sb.ToString()); exit 1 }
$K = [System.Windows.Forms.SendKeys]
if ($action -eq "open") {
  Set-Clipboard -Value $url
  $K::SendWait("^t"); Start-Sleep -Milliseconds 900
  $K::SendWait("^l"); Start-Sleep -Milliseconds 300
  $K::SendWait("^v"); Start-Sleep -Milliseconds 300
  $K::SendWait("{ENTER}"); Start-Sleep -Milliseconds 4000
} elseif ($action -eq "paste") {
  $K::SendWait("{ESC}"); Start-Sleep -Milliseconds 800
  $K::SendWait("n"); Start-Sleep -Milliseconds 1800
  $K::SendWait("^v"); Start-Sleep -Milliseconds 2000
} elseif ($action -eq "keys") {
  $K::SendWait($url); Start-Sleep -Milliseconds 800
}
[void][XK]::GetWindowText([XK]::GetForegroundWindow(), $sb, 512)
Write-Output ("done " + $action + " fg=" + $sb.ToString())
