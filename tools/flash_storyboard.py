# -*- coding: utf-8 -*-
"""お毒姐さん「フラッシュダンス風」動画の参照画像（＝絵コンテ）を作る（2026-09-24）。

  python tools/flash_storyboard.py --char <キャラ画像> --out tmp/video/flash_0924/ref.png [--char-h 640]

1. 公開中の oshinavi.jp を headless Chrome で携帯の幅（540×960・2倍）で撮る＝1080×1920
2. キャラ画像の白い背景を外周から抜く（キャラ内部の白は残す）
3. 背景を少し暗くして、キャラを下の真ん中に小さく置く（ユーザー指定「キャラは大きくしない」）
"""
import argparse
import os
import subprocess
from collections import deque

from PIL import Image, ImageEnhance

CHROME_CANDIDATES = [
    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
]


def local_page(hide, out_dir):
    """手元の index.html を写して、隠したい部品（広告の帯・ピックアップ）を消した版を作る。
    🚨よその広告（トリバゴ・楽天トラベル）を宣伝動画に写さない。画像などは <base> で元の場所から読む。"""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    h = open(os.path.join(root, 'index.html'), encoding='utf-8').read()
    base = '<base href="file:///%s/">' % root.replace('\\', '/')
    css = '<style>%s{display:none!important}</style>' % ','.join(hide)
    h = h.replace('<head>', '<head>' + base + css, 1)
    p = os.path.join(os.path.abspath(out_dir), 'site_for_shot.html')
    open(p, 'w', encoding='utf-8').write(h)
    return 'file:///' + p.replace('\\', '/')


def shoot(url, out):
    chrome = next(p for p in CHROME_CANDIDATES if os.path.exists(p))
    subprocess.run([chrome, '--headless=new', '--hide-scrollbars', '--window-size=540,960',
                    '--force-device-scale-factor=2', '--virtual-time-budget=8000',
                    '--screenshot=' + os.path.abspath(out), url], check=True, timeout=120,
                   capture_output=True)
    return Image.open(out).convert('RGB')


def cutout_white(img, thr=238):
    """四隅から連結する「ほぼ白」だけを透明にする（外周フラッドフィル）。"""
    im = img.convert('RGBA')
    w, h = im.size
    px = im.load()
    seen = bytearray(w * h)
    q = deque([(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)])
    while q:
        x, y = q.popleft()
        if x < 0 or y < 0 or x >= w or y >= h or seen[y * w + x]:
            continue
        seen[y * w + x] = 1
        r, g, b, a = px[x, y]
        if min(r, g, b) < thr:
            continue
        px[x, y] = (r, g, b, 0)
        q.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    return im.crop(im.getbbox())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--char', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--url', default='https://oshinavi.jp/')
    ap.add_argument('--hide', default='.fixed-banner,.pickup',
                    help='消す部品のCSSセレクタ（カンマ区切り）。空なら公開版をそのまま撮る')
    ap.add_argument('--char-h', type=int, default=640)
    ap.add_argument('--chair', action='store_true', help='真ん中に木の椅子を置き、キャラはその右に立たせる')
    ap.add_argument('--dim', type=float, default=0.72, help='背景の明るさ（1=そのまま）')
    a = ap.parse_args()
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    url = a.url
    if a.hide:
        url = local_page(a.hide.split(','), os.path.dirname(a.out))
    bg = shoot(url, os.path.join(os.path.dirname(a.out), 'bg_site.png'))
    bg = ImageEnhance.Brightness(bg).enhance(a.dim)
    ch = cutout_white(Image.open(a.char))
    ch.save(os.path.join(os.path.dirname(a.out), 'char_cut.png'))
    r = a.char_h / ch.height
    ch = ch.resize((max(1, int(ch.width * r)), a.char_h), Image.LANCZOS)
    W, H = bg.size
    if a.chair:
        # 🆕2026-09-24 ユーザー「真ん中に椅子を置いて座ったりもさせて」＝椅子は真ん中・キャラはその右に立つ
        import sys as _s
        _s.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from draw_chair import chair
        c = chair(int(a.char_h * 0.62))
        bg = bg.convert('RGBA')
        bg.paste(c, ((W - c.width) // 2, H - c.height - 60), c)
        x, y = W // 2 + c.width // 2 - 40, H - ch.height - 60
    else:
        x, y = (W - ch.width) // 2, H - ch.height - 60
    bg.paste(ch, (x, y), ch)
    bg = bg.convert('RGB')
    bg.save(a.out)
    print('参照画像 %s  %dx%d  キャラ高さ %dpx（画面の%d%%）' % (a.out, W, H, a.char_h, round(100 * a.char_h / H)))


if __name__ == '__main__':
    main()
