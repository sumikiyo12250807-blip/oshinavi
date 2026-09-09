Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win {
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int n);
}
"@

$w = Get-Process chrome -ErrorAction SilentlyContinue |
     Where-Object { $_.MainWindowTitle -ne '' } |
     Select-Object -First 1
if (-not $w) { Write-Output "no chrome window"; exit 1 }
Write-Output ("front window: " + $w.MainWindowTitle)
[Win]::ShowWindow($w.MainWindowHandle, 9) | Out-Null
[Win]::SetForegroundWindow($w.MainWindowHandle) | Out-Null
Start-Sleep -Milliseconds 900

Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.SendKeys]::SendWait("^v")
Start-Sleep -Milliseconds 1500
Write-Output "sent ctrl+v"
