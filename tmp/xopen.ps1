param([string]$url, [string]$shot)
# Navigate the current Chrome tab to $url (clipboard + Ctrl+L), wait, shot. ASCII only.
$s = 'C:\Users\user\oshinavi\tmp'
Set-Clipboard -Value $url
powershell -NoProfile -ExecutionPolicy Bypass -File $s\xkeys2.ps1 -keys "^l" | Out-Null
powershell -NoProfile -ExecutionPolicy Bypass -File $s\xkeys2.ps1 -keys "^v{ENTER}" | Out-Null
Start-Sleep -Seconds 5
powershell -NoProfile -ExecutionPolicy Bypass -File $s\xkeys2.ps1 -shot $shot
