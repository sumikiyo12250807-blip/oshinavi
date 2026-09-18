# -*- coding: utf-8 -*-
"""音源から縦型の動画を作る（X/リールに上げる用・課金ゼロ・ffmpegだけ）。

  python tools/audio_to_video.py <音源> --start 30 --dur 20 --out tmp/mv/a.mp4
  python tools/audio_to_video.py <音源> --start 30 --dur 20 --cover tmp/mv/cover.jpg

## 作り

1080×1920（Xの縦）。背景＝ジャケットを大きくぼかしたもの／中央＝ジャケット／
下＝音の波形（showwaves）／上＝OSHINAVIのロゴ。
音は `--start` 秒から `--dur` 秒。**音源の残りが足りなければエラーで止める**
（足りない分を無音で埋めると「音が切れた不良品」に見えるので作らない）。

ffmpegはPATHに無いので `imageio_ffmpeg.get_ffmpeg_exe()` で引く（[[project_odoku_x_video]]）。
"""
import argparse
import io
import os
import re
import subprocess
import sys

import imageio_ffmpeg

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
FF = imageio_ffmpeg.get_ffmpeg_exe()


def duration_of(path):
    r = subprocess.run([FF, '-hide_banner', '-i', path], capture_output=True)
    m = re.search(r'Duration:\s*(\d+):(\d+):(\d+\.\d+)', r.stderr.decode('utf-8', 'replace'))
    if not m:
        return None
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))


def extract_cover(src, out):
    subprocess.run([FF, '-y', '-hide_banner', '-loglevel', 'error', '-i', src,
                    '-an', '-vcodec', 'copy', out], check=False)
    return out if os.path.exists(out) and os.path.getsize(out) > 1000 else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('--start', type=float, default=0)
    ap.add_argument('--dur', type=float, default=30)
    ap.add_argument('--out', default='tmp/mv/out.mp4')
    ap.add_argument('--cover', default='')
    ap.add_argument('--logo', default='logo.png')
    ap.add_argument('--wave-color', default='0xff7ad9')
    # 🚨2026-09-18 ユーザー指示＝「キャラは小さめ・アップにしない・カメラに近づかない・
    #    小さいまま おどる・かわいく・画面全体に動き回って」
    #    ＝**大きさは一定**（寄る＝拡大は禁止）。動きは 左右の往復＋ゆっくり上下＋跳ねる＋小さく傾く。
    ap.add_argument('--chara', default='', help='透過PNGのキャラ（切り抜き済み）')
    ap.add_argument('--chara-h', type=int, default=430, help='キャラの高さ(px)・1920の約22%%＝小さめ')
    a = ap.parse_args()

    total = duration_of(a.src)
    if total is None:
        print('音源の長さが読めない'); return 2
    left = total - a.start
    print('音源 %.2f秒 ／%.0f秒から使えるのは %.2f秒' % (total, a.start, left))
    if left < a.dur - 0.05:
        print('🚨足りない＝%.0f秒から%.0f秒は取れない（残り%.2f秒）。'
              '--dur を %.0f 以下にするか --start を前にずらして。' % (a.start, a.dur, left, left))
        return 2

    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    cover = a.cover or extract_cover(a.src, 'tmp/mv/_cover.jpg')
    if not cover:
        print('ジャケットが無いので --cover で絵を渡して'); return 2

    # 背景＝ジャケットを埋めてぼかす／中央＝ジャケット／下＝波形／上＝ロゴ
    fc = (
        '[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,'
        'gblur=sigma=28,eq=brightness=-0.06[bg];'
        '[0:v]scale=880:880[cv];'
        '[bg][cv]overlay=(W-w)/2:380[b1];'
        '[2:a]showwaves=s=1080x260:mode=cline:colors=%s:rate=25[wv];'
        '[b1][wv]overlay=0:1340[b2];'
        '[1:v]scale=-1:150[lg];'
        '[b2][lg]overlay=(W-w)/2:140[b3];'
    ) % a.wave_color

    ins = [FF, '-y', '-hide_banner', '-loglevel', 'error',
           '-loop', '1', '-i', cover,
           '-loop', '1', '-i', a.logo,
           '-ss', '%.3f' % a.start, '-t', '%.3f' % a.dur, '-i', a.src]
    if a.chara:
        ins += ['-loop', '1', '-i', a.chara]
        # 大きさは固定＝寄らない。パッドしてから小さく傾ける（回転で角が切れないように）
        fc += (
            '[3:v]scale=-1:%d,pad=iw+120:ih+120:60:60:color=#00000000,format=rgba,'
            "rotate='0.13*sin(2*PI*t/1.15)':c=none[ch];"
            # 左右は7秒で往復・上下は11秒でゆっくり移動・0.65秒ごとに跳ねる＝画面全体を動き回る
            "[b3][ch]overlay=eval=frame"
            ":x='(W-w)/2+(W-w)/2*sin(2*PI*t/7)'"
            ":y='170+(H-h-340)*(0.5+0.5*sin(2*PI*t/11))-46*abs(sin(2*PI*t/0.65))'[b4];"
            '[b4]format=yuv420p[v]'
        ) % a.chara_h
    else:
        fc += '[b3]format=yuv420p[v]'

    cmd = ins + ['-filter_complex', fc,
           '-map', '[v]', '-map', '2:a',
           '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-r', '25',
           '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart',
           a.out]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        print('ffmpegが落ちた:\n' + r.stderr.decode('utf-8', 'replace')[-1200:])
        return 2
    print('できた: %s （%.1fMB・%.0f秒）' % (a.out, os.path.getsize(a.out) / 1e6, a.dur))
    return 0


if __name__ == '__main__':
    sys.exit(main())
