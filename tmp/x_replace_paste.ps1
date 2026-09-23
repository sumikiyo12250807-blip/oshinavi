# Bring Chrome to front and replace the focused text box contents with the clipboard.
# Ctrl+A then Ctrl+V. No Japanese characters in this file (PowerShell 5.1 reads it as ANSI).
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class FW2 {
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int n);
}
"@
$p = Get-Process chrome -ErrorAction SilentlyContinue |
     Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
if (-not $p) { Write-Output "no chrome window"; exit 1 }
[FW2]::ShowWindow($p.MainWindowHandle, 9) | Out-Null
[FW2]::SetForegroundWindow($p.MainWindowHandle) | Out-Null
Start-Sleep -Milliseconds 500
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.SendKeys]::SendWait("^a")
Start-Sleep -Milliseconds 300
[System.Windows.Forms.SendKeys]::SendWait("^v")
Start-Sleep -Milliseconds 500
Write-Output "sent ctrl+a ctrl+v"
