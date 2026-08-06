# -*- coding: utf-8 -*-
"""動画から音声だけを wav で抜き出す（H3が出した声を"声の見本"として保存するため）。

  python tools/extract_audio.py <in.mp4> <out.wav>

H3の参照音声は 2〜15秒・WAV/MP3・15MB以下（[[project_odoku_x_video]]）。
ffmpeg は imageio_ffmpeg 同梱のものを使う（PATHには無い）。
"""
import io, os, subprocess, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import imageio_ffmpeg

src, dst = sys.argv[1], sys.argv[2]
exe = imageio_ffmpeg.get_ffmpeg_exe()
cmd = [exe, "-y", "-i", src, "-vn", "-ac", "1", "-ar", "24000",
       "-acodec", "pcm_s16le", dst]
p = subprocess.run(cmd, capture_output=True)
if p.returncode != 0:
    sys.stdout.write(p.stderr.decode("utf-8", "replace")[-1500:])
    sys.exit("ffmpeg が失敗した")
n = os.path.getsize(dst)
print("%s  %d bytes  約%.1f秒" % (dst, n, n / 2.0 / 24000))
