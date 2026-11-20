# -*- coding: utf-8 -*-
# 拍のずれの点検（すちこ「音楽にキャラクターのリズムがあってない」）
#   ①今の格子（134.0BPM・位相0.224）で、10秒ごとにいちばん合う位相を測る＝位相が流れていたらBPMが少しずれている
#   ②133.0〜135.0 を 0.01 刻み・位相 1ms 刻みでキックとスネアに当て直す
import io, json, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import imageio_ffmpeg
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
SR, HOP, NFFT = 22050, 64, 2048
raw = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-v', 'error', '-i', D + 'song.mp3', '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'], capture_output=True).stdout
y = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
win = np.hanning(NFFT).astype(np.float32)
n = 1 + (len(y) - NFFT) // HOP
fr = np.lib.stride_tricks.as_strided(y, shape=(n, NFFT), strides=(y.strides[0] * HOP, y.strides[0]))
S = np.abs(np.fft.rfft(fr * win, axis=1))
freqs = np.fft.rfftfreq(NFFT, 1 / SR)
fps = SR / HOP
t_of = lambda i: (i + NFFT / 2 / HOP) / fps   # フレームの真ん中の時刻


def onset(lo, hi):
    b = np.log1p(10 * S[:, (freqs >= lo) & (freqs < hi)])
    f = np.maximum(0, np.diff(b, axis=0)).sum(axis=1)
    f = np.concatenate([[0], f])
    f = f - np.convolve(f, np.ones(64) / 64, mode='same')
    return np.maximum(f, 0) / (np.maximum(f, 0).max() + 1e-9)


K, SN = onset(30, 150), onset(150, 4000)
T = np.array([t_of(i) for i in range(len(K))])


def fit(env, bpm, t0=0, t1=1e9, step=0.001):
    P = 60 / bpm
    m = (T >= t0) & (T < t1)
    best = (0, 0)
    for ph in np.arange(0, P, step):
        g = np.arange(ph, T[-1], P)
        g = g[(g >= t0) & (g < t1)]
        idx = np.clip(np.searchsorted(T, g), 0, len(env) - 1)
        s = env[idx].mean() / (env[m].mean() + 1e-9)
        if s > best[0]:
            best = (s, ph)
    return best
print('① 134.0BPM で10秒ごとの最良位相（キック）')
for a in range(0, 90, 10):
    s, ph = fit(K, 134.0, a, a + 10)
    print('  %2d〜%2d秒 位相 %.3f 点 %.2f' % (a, a + 10, ph, s))
print('② 細かく当て直し')
for name, env in (('kick', K), ('snare', SN)):
    sc = sorted(((fit(env, b, 2, 92, 0.002) + (b,)) for b in np.arange(133.0, 135.01, 0.05)), reverse=True)[:5]
    print(' ', name, [(round(s, 2), round(b, 2), round(p, 3)) for s, p, b in sc])
