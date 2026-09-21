# Find the top-level window whose title contains $Match (e.g. "/ X - Google Chrome"),
# bring it to front, then Esc -> n -> Ctrl+V (unless -NoPaste).
# Unlike x_focus_and_paste.ps1 this never cycles tabs with Ctrl+Tab, so it cannot
# end up typing into another app. No Japanese characters in this file.
param(
  [string]$Match = "/ X",
  [switch]$NoPaste
)

Add-Type @"
using System;
using System.Text;
using System.Collections.Generic;
using System.Runtime.InteropServices;
public class WX {
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc f, IntPtr l);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern int GetWindowTextLength(IntPtr h);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int n);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  public static List<KeyValuePair<IntPtr,string>> All() {
    var r = new List<KeyValuePair<IntPtr,string>>();
    EnumWindows((h, l) => {
      if (!IsWindowVisible(h)) return true;
      int n = GetWindowTextLength(h);
      if (n <= 0) return true;
      var sb = new StringBuilder(n + 2);
      GetWindowText(h, sb, sb.Capacity);
      r.Add(new KeyValuePair<IntPtr,string>(h, sb.ToString()));
      return true;
    }, IntPtr.Zero);
    return r;
  }
  public static string Front() {
    IntPtr h = GetForegroundWindow();
    int n = GetWindowTextLength(h);
    if (n <= 0) return "";
    var sb = new StringBuilder(n + 2);
    GetWindowText(h, sb, sb.Capacity);
    return sb.ToString();
  }
}
"@

$hit = [WX]::All() | Where-Object { $_.Value -like "*$Match*" -and $_.Value -like "*Chrome*" } | Select-Object -First 1
if (-not $hit) { Write-Output ("NOT FOUND: " + $Match); exit 2 }
[void][WX]::ShowWindow($hit.Key, 9)
[void][WX]::SetForegroundWindow($hit.Key)
Start-Sleep -Milliseconds 900
$front = [WX]::Front()
Write-Output ("front: " + $front)
if ($front -notlike "*$Match*") { Write-Output "FOCUS FAILED"; exit 3 }
if ($NoPaste) { exit 0 }

Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.SendKeys]::SendWait("{ESC}")
Start-Sleep -Milliseconds 800
[System.Windows.Forms.SendKeys]::SendWait("n")
Start-Sleep -Milliseconds 1600
[System.Windows.Forms.SendKeys]::SendWait("^v")
Start-Sleep -Milliseconds 2000
Write-Output "sent n + ctrl+v"
