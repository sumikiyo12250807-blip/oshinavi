# -*- coding: utf-8 -*-
# 拍の測り直し（matome1024j/tempo_check.py の写し）
#   低音（キック 40〜150Hz）と全帯域の立ち上がりで、60〜200BPM の候補ごとに「拍の格子に乗る立ち上がりの強さ」を測って上位を出す
import io, json, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import imageio_ffmpeg
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
SR, HOP, NFFT = 22050, 128, 2048
raw = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-v', 'error', '-i', D + 'song.mp3', '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'],
                     capture_output=True, stdin=subprocess.DEVNULL).stdout
y = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
win = np.hanning(NFFT).astype(np.float32)
n = 1 + (len(y) - NFFT) // HOP
fr = np.lib.stride_tricks.as_strided(y, shape=(n, NFFT), strides=(y.strides[0] * HOP, y.strides[0]))
S = np.abs(np.fft.rfft(fr * win, axis=1))
freqs = np.fft.rfftfreq(NFFT, 1 / SR)
fps = SR / HOP


def onset(lo, hi):
    b = np.log1p(10 * S[:, (freqs >= lo) & (freqs < hi)])
    f = np.maximum(0, np.diff(b, axis=0)).sum(axis=1)
    f = np.concatenate([[0], f])
    f = f - np.convolve(f, np.ones(32) / 32, mode='same')
    f = np.maximum(f, 0)
    return f / (f.max() + 1e-9)


res = {}
for name, (lo, hi) in {'kick': (30, 150), 'snare': (150, 4000), 'all': (30, 11000)}.items():
    f = onset(lo, hi)
    sc = []
    for bpm10 in range(600, 2001, 2):
        bpm = bpm10 / 10
        P = 60 / bpm * fps
        best = (0, 0)
        for ph in np.linspace(0, P, 24, endpoint=False):
            idx = np.round(np.arange(ph, len(f) - 1, P)).astype(int)
            s = f[idx].mean()
            if s > best[0]:
                best = (s, ph / fps)
        sc.append((best[0] / f.mean(), bpm, best[1]))
    sc.sort(reverse=True)
    top = []
    for s, b, p in sc:
        if all(abs(b - x[1]) > 3 for x in top):
            top.append((round(s, 2), b, round(p, 3)))
        if len(top) == 6:
            break
    res[name] = top
    print(name, top)
# 音の大きさ（0.5秒ごと）＝曲の終わりの静かな所・歌の切れ目を見る
rms = [float(np.sqrt(np.mean(y[i:i + SR // 2] ** 2))) for i in range(0, len(y), SR // 2)]
res['rms'] = [round(v, 3) for v in rms]
print('rms', ' '.join('%.1f:%.2f' % (i * 0.5, v) for i, v in enumerate(rms)))
json.dump(res, io.open(D + 'tempo_check.json', 'w'))
