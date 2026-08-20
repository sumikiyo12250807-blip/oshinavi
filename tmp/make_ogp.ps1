# X(Twitter)/OGP用のカード画像 og-image.png を作る。1200x630（大きいカードの推奨比 1.91:1）。
# サイトの配色に合わせる: 背景#0a0a0a / アクセント紫#e040fb / 水色#00e5ff
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

$W = 1200; $H = 630
$bmp = New-Object System.Drawing.Bitmap($W, $H)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = 'AntiAlias'
$g.TextRenderingHint = 'ClearTypeGridFit'
$g.InterpolationMode = 'HighQualityBicubic'

# 背景（黒→少し明るい黒のグラデーション）
$rect = New-Object System.Drawing.Rectangle(0, 0, $W, $H)
$bg = New-Object System.Drawing.Drawing2D.LinearGradientBrush(
    $rect,
    [System.Drawing.ColorTranslator]::FromHtml('#0a0a0a'),
    [System.Drawing.ColorTranslator]::FromHtml('#1a1024'), 45)
$g.FillRectangle($bg, $rect)

# 右下にうっすら紫の光
$glow = New-Object System.Drawing.Drawing2D.GraphicsPath
$glow.AddEllipse(820, 300, 620, 560)
$pg = New-Object System.Drawing.Drawing2D.PathGradientBrush($glow)
$pg.CenterColor = [System.Drawing.Color]::FromArgb(70, 224, 64, 251)
$pg.SurroundColors = @([System.Drawing.Color]::FromArgb(0, 10, 10, 10))
$g.FillPath($pg, $glow)

# 上端のアクセントライン（紫→水色）
$lineRect = New-Object System.Drawing.Rectangle(0, 0, $W, 8)
$lineBrush = New-Object System.Drawing.Drawing2D.LinearGradientBrush(
    $lineRect,
    [System.Drawing.ColorTranslator]::FromHtml('#e040fb'),
    [System.Drawing.ColorTranslator]::FromHtml('#00e5ff'), 0)
$g.FillRectangle($lineBrush, $lineRect)

# ロゴ（左側に円形で配置）
$logoPath = 'C:/Users/user/oshinavi/logo.png'
if (Test-Path $logoPath) {
    $logo = [System.Drawing.Image]::FromFile($logoPath)
    $size = 250; $lx = 95; $ly = ($H - $size) / 2
    $clip = New-Object System.Drawing.Drawing2D.GraphicsPath
    $clip.AddEllipse($lx, $ly, $size, $size)
    $g.SetClip($clip)
    # ロゴPNGは透過部分があり、そのまま置くと市松模様が透けて見える。先に黒で塗りつぶす
    $fill = New-Object System.Drawing.SolidBrush([System.Drawing.ColorTranslator]::FromHtml('#0a0a0a'))
    $g.FillEllipse($fill, $lx, $ly, $size, $size)
    # logo.png は四隅に市松模様(透過表現)が焼き付いているので、中央だけを切り出して使う
    $srcMargin = [int]($logo.Width * 0.06)
    $srcRect = New-Object System.Drawing.Rectangle($srcMargin, $srcMargin, ($logo.Width - $srcMargin * 2), ($logo.Height - $srcMargin * 2))
    $dstRect = New-Object System.Drawing.Rectangle($lx, $ly, $size, $size)
    $g.DrawImage($logo, $dstRect, $srcRect, [System.Drawing.GraphicsUnit]::Pixel)
    $g.ResetClip()
    $penL = New-Object System.Drawing.Pen([System.Drawing.ColorTranslator]::FromHtml('#e040fb'), 4)
    $g.DrawEllipse($penL, $lx, $ly, $size, $size)
    $logo.Dispose()
}

$textX = 410
$white = New-Object System.Drawing.SolidBrush([System.Drawing.ColorTranslator]::FromHtml('#f0f0f0'))
$muted = New-Object System.Drawing.SolidBrush([System.Drawing.ColorTranslator]::FromHtml('#9a9a9a'))
$accent = New-Object System.Drawing.SolidBrush([System.Drawing.ColorTranslator]::FromHtml('#00e5ff'))

# メインコピー
$f1 = New-Object System.Drawing.Font('Yu Gothic UI', 46, [System.Drawing.FontStyle]::Bold, 'Pixel')
$g.DrawString('推しの"発売日"', $f1, $white, $textX, 150)
$g.DrawString('見逃さない', $f1, $white, $textX, 215)

# サービス名
$f2 = New-Object System.Drawing.Font('Segoe UI', 62, [System.Drawing.FontStyle]::Bold, 'Pixel')
$nameRect = New-Object System.Drawing.Rectangle($textX, 300, 560, 90)
$nameBrush = New-Object System.Drawing.Drawing2D.LinearGradientBrush(
    $nameRect,
    [System.Drawing.ColorTranslator]::FromHtml('#e040fb'),
    [System.Drawing.ColorTranslator]::FromHtml('#00e5ff'), 0)
$g.DrawString('OSHINAVI', $f2, $nameBrush, $textX, 300)

# 説明
$f3 = New-Object System.Drawing.Font('Yu Gothic UI', 25, [System.Drawing.FontStyle]::Regular, 'Pixel')
$g.DrawString('チケット発売日情報', $f3, $muted, ($textX + 6), 395)

# 下部の帯
$f4 = New-Object System.Drawing.Font('Yu Gothic UI', 23, [System.Drawing.FontStyle]::Bold, 'Pixel')
$g.DrawString('ライブ・舞台・スポーツ・展覧会を毎日更新', $f4, $accent, ($textX + 6), 460)
$f5 = New-Object System.Drawing.Font('Segoe UI', 24, [System.Drawing.FontStyle]::Bold, 'Pixel')
$g.DrawString('oshinavi.jp', $f5, $white, ($textX + 6), 512)

$out = 'C:/Users/user/oshinavi/og-image.png'
$bmp.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()

$fi = Get-Item $out
"作成: $($fi.Name)  $([math]::Round($fi.Length/1KB))KB  1200x630"
