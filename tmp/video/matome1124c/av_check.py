# -*- coding: utf-8 -*-
# 試し動画 clip.mp4 の音で、キックの立ち上がりと拍の時刻（＝キャラが一番沈むコマ）のずれを測る（音と絵の時刻合わせの点検）
#   ずれ L を -80〜+80ms で動かし、拍＋L の時刻のキックの強さが一番大きい L を出す。0 付近なら絵と音は合っている
import io, json, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import imageio_ffmpeg
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
A, Bv = 18.0, 31.0
SR, HOP, NFFT = 22050, 64, 2048
raw = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-v', 'error', '-i', D + 'clip.mp4', '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'], capture_output=True).stdout
y = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
win = np.hanning(NFFT).astype(np.float32)
n = 1 + (len(y) - NFFT) // HOP
fr = np.lib.stride_tricks.as_strided(y, shape=(n, NFFT), strides=(y.strides[0] * HOP, y.strides[0]))
S = np.abs(np.fft.rfft(fr * win, axis=1))
fq = np.fft.rfftfreq(NFFT, 1 / SR)
b = np.log1p(10 * S[:, (fq >= 30) & (fq < 150)])
k = np.maximum(0, np.diff(b, axis=0)).sum(axis=1)
k = np.concatenate([[0], k])
T = (np.arange(len(k)) + NFFT / 2 / HOP) / (SR / HOP)
beats = [x - A for x in json.load(io.open(D + 'beats.json'))['beats'] if A + 0.3 <= x < Bv - 0.3]
res = []
for L in np.arange(-0.08, 0.081, 0.004):
    idx = np.clip(np.searchsorted(T, np.array(beats) + L), 0, len(k) - 1)
    res.append((float(k[idx].mean() / k.mean()), round(L * 1000)))
res.sort(reverse=True)
print('一番合うずれ(ms)', res[0][1], '強さ', round(res[0][0], 2), ' 0ms の強さ', round(dict((l, s) for s, l in res)[0], 2), ' 上位', res[:5])
