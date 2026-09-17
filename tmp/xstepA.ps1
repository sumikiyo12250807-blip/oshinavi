param([string]$file, [int]$hour, [string]$minute, [string]$shot)
# Step A for one scheduled post: paste the post, open schedule dialog, set hour/minute, take a shot.
# Hour default in X = current hour + 1, so press DOWN (hour - default) times. ASCII only.
$s = 'C:\Users\user\oshinavi\tmp'
Get-Content -Raw -Encoding UTF8 $file | Set-Clipboard
powershell -NoProfile -ExecutionPolicy Bypass -File $s\xkeys.ps1 -action paste
powershell -NoProfile -ExecutionPolicy Bypass -File $s\xkeys2.ps1 -x 635 -y 674
Start-Sleep -Milliseconds 800
$def = (Get-Date).AddHours(1).Hour
$n = $hour - $def
if ($n -lt 0) { Write-Output "ABORT: target hour earlier than default"; exit 1 }
$k = ('{DOWN}' * $n) + '{ENTER}'
powershell -NoProfile -ExecutionPolicy Bypass -File $s\xkeys2.ps1 -x 546 -y 374
powershell -NoProfile -ExecutionPolicy Bypass -File $s\xkeys2.ps1 -keys $k
powershell -NoProfile -ExecutionPolicy Bypass -File $s\xkeys2.ps1 -x 660 -y 374
powershell -NoProfile -ExecutionPolicy Bypass -File $s\xkeys2.ps1 -keys ($minute + '{ENTER}') -shot $shot
Write-Output ("stepA done default_hour=" + $def + " down=" + $n)
