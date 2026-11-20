# -*- coding: utf-8 -*-
# 確かめ用：試し動画 clip.mp4（20.5〜33.5秒）の音に、拍の時刻（beats.json）でクリック音を混ぜる → clip_click.mp4
#   小節の頭は高い音（1760Hz）・ほかの拍は 1320Hz・30ms
import io, json, os, subprocess, wave
import numpy as np
import imageio_ffmpeg
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
A, Bv = 18.0, 31.0
SR = 48000
spec = json.load(io.open(D + 'stage_1118_v.json', encoding='utf-8'))
import numpy as _n
_B = json.load(io.open(D + 'beats.json'))['beats']
_sh = [c['show'] for c in spec['chunks']]
_PH = min(range(4), key=lambda p: sum(min(abs(b - s) for b in _B[p::4]) for s in _sh))
bars = set(round(b, 3) for b in _B[_PH::4])
beats = json.load(io.open(D + 'beats.json'))['beats']
y = np.zeros(int((Bv - A) * SR), np.float32)
n = int(0.03 * SR)
env = np.exp(-np.arange(n) / (0.006 * SR)).astype(np.float32)
for b in beats:
    if A <= b < Bv:
        f = 1760 if round(b, 3) in bars else 1320
        i = int((b - A) * SR)
        s = (0.5 * np.sin(2 * np.pi * f * np.arange(n) / SR) * env).astype(np.float32)
        y[i:i + n] += s[:len(y[i:i + n])]
w = wave.open(D + 'click.wav', 'wb')
w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
ff = imageio_ffmpeg.get_ffmpeg_exe()
r = subprocess.run([ff, '-y', '-v', 'error', '-i', D + 'clip.mp4', '-i', D + 'click.wav', '-filter_complex',
                    '[0:a][1:a]amix=inputs=2:duration=first:normalize=0[a]', '-map', '0:v', '-map', '[a]', '-c:v', 'copy',
                    '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', D + 'clip_click.mp4'], capture_output=True, text=True, errors='replace')
print(r.returncode, r.stderr[-300:], os.path.getsize(D + 'clip_click.mp4') // 1024, 'KB')
