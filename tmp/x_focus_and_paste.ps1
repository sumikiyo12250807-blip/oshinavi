# Bring Chrome to front, cycle tabs until the title matches, then send Ctrl+V.
# No Japanese characters in this file (PowerShell 5.1 reads it as ANSI and breaks).
param(
  [string]$Match = "compose",
  [int]$MaxTabs = 12,
  [switch]$NoPaste
)

Add-Type @"
using System;
using System.Text;
using System.Runtime.InteropServices;
public class FW {
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int n);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern int GetWindowTextLength(IntPtr h);
}
"@

function Get-FrontTitle {
  $h = [FW]::GetForegroundWindow()
  $len = [FW]::GetWindowTextLength($h)
  if ($len -le 0) { return "" }
  $sb = New-Object System.Text.StringBuilder ($len + 2)
  [void][FW]::GetWindowText($h, $sb, $sb.Capacity)
  return $sb.ToString()
}

$w = Get-Process chrome -ErrorAction SilentlyContinue |
     Where-Object { $_.MainWindowTitle -ne '' } |
     Select-Object -First 1
if (-not $w) { Write-Output "no chrome window"; exit 1 }

[void][FW]::ShowWindow($w.MainWindowHandle, 9)
[void][FW]::SetForegroundWindow($w.MainWindowHandle)
Start-Sleep -Milliseconds 700

Add-Type -AssemblyName System.Windows.Forms

$title = Get-FrontTitle
Write-Output ("start tab: " + $title)

$hit = $false
if ($title -like "*$Match*") { $hit = $true }

$i = 0
while (-not $hit -and $i -lt $MaxTabs) {
  [System.Windows.Forms.SendKeys]::SendWait("^{TAB}")
  Start-Sleep -Milliseconds 550
  $title = Get-FrontTitle
  Write-Output ("  tab " + ($i + 1) + ": " + $title)
  if ($title -like "*$Match*") { $hit = $true }
  $i++
}

if (-not $hit) { Write-Output ("NOT FOUND: " + $Match); exit 2 }
Write-Output ("FOUND: " + $title)

if ($NoPaste) { Write-Output "no paste (check only)"; exit 0 }

Start-Sleep -Milliseconds 400
[System.Windows.Forms.SendKeys]::SendWait("^v")
Start-Sleep -Milliseconds 1500
Write-Output "sent ctrl+v"
