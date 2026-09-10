Add-Type @"
using System;
using System.Text;
using System.Runtime.InteropServices;
public class WinList {
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
  [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern int GetWindowTextLength(IntPtr h);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern int GetClassName(IntPtr h, StringBuilder s, int n);
}
"@

$found = New-Object System.Collections.ArrayList
$cb = [WinList+EnumProc]{
  param($h, $l)
  if ([WinList]::IsWindowVisible($h)) {
    $len = [WinList]::GetWindowTextLength($h)
    if ($len -gt 0) {
      $sb = New-Object System.Text.StringBuilder ($len + 2)
      [void][WinList]::GetWindowText($h, $sb, $sb.Capacity)
      $cn = New-Object System.Text.StringBuilder 256
      [void][WinList]::GetClassName($h, $cn, 256)
      if ($cn.ToString() -like "Chrome_WidgetWin*") {
        [void]$found.Add([pscustomobject]@{ Handle = $h; Title = $sb.ToString() })
      }
    }
  }
  return $true
}
[void][WinList]::EnumWindows($cb, [IntPtr]::Zero)
$found | Format-Table -AutoSize | Out-String -Width 250
