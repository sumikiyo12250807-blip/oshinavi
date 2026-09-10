# Focus Chrome, reopen the composer with the "n" shortcut (which focuses the text box
# by itself), then paste. Keyboard only - no ref clicks in between, so focus is never lost.
# No Japanese characters in this file (PowerShell 5.1 reads it as ANSI and breaks).

Add-Type @"
using System;
using System.Text;
using System.Runtime.InteropServices;
public class FW2 {
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int n);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern int GetWindowTextLength(IntPtr h);
}
"@

$w = Get-Process chrome -ErrorAction SilentlyContinue |
     Where-Object { $_.MainWindowTitle -ne '' } |
     Select-Object -First 1
if (-not $w) { Write-Output "no chrome window"; exit 1 }
Write-Output ("front: " + $w.MainWindowTitle)

[void][FW2]::ShowWindow($w.MainWindowHandle, 9)
[void][FW2]::SetForegroundWindow($w.MainWindowHandle)
Start-Sleep -Milliseconds 900

Add-Type -AssemblyName System.Windows.Forms

# close whatever dialog is open
[System.Windows.Forms.SendKeys]::SendWait("{ESC}")
Start-Sleep -Milliseconds 800

# "n" opens the composer and puts the caret in the text box
[System.Windows.Forms.SendKeys]::SendWait("n")
Start-Sleep -Milliseconds 1600

[System.Windows.Forms.SendKeys]::SendWait("^v")
Start-Sleep -Milliseconds 2000
Write-Output "sent n + ctrl+v"
