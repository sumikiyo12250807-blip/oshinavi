# -*- coding: utf-8 -*-
"""動画/音声の話し声の高さ(F0)を測って、男声か女声かの目安を出す。

  python tools/voice_pitch.py tmp/promo/morphic_0823.mp4

耳で聴けない時に「男の声になったか」を数字で確かめるための道具。
目安＝成人男性 85〜155Hz ／成人女性 165〜255Hz。
自己相関で有声フレームだけ拾って中央値を出す。
"""
import io, os, sys, subprocess, wave
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np
import imageio_ffmpeg

src = sys.argv[1]
wav = os.path.join(os.path.dirname(src) or ".", "_pitch_tmp.wav")
ff = imageio_ffmpeg.get_ffmpeg_exe()
subprocess.run([ff, "-y", "-i", src, "-ac", "1", "-ar", "16000", wav, "-loglevel", "error"],
               check=True)

with wave.open(wav, "rb") as w:
    sr = w.getframerate()
    x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64)

frame = int(0.040 * sr)      # 40ms
hop = int(0.020 * sr)
fmin, fmax = 60.0, 400.0
lag_min, lag_max = int(sr / fmax), int(sr / fmin)

f0s = []
for i in range(0, len(x) - frame, hop):
    seg = x[i:i + frame]
    if np.sqrt((seg ** 2).mean()) < 300:      # 無音・息はとばす
        continue
    seg = seg - seg.mean()
    ac = np.correlate(seg, seg, mode="full")[frame - 1:]
    if ac[0] <= 0:
        continue
    ac = ac / ac[0]
    region = ac[lag_min:lag_max]
    lag = int(np.argmax(region)) + lag_min
    if ac[lag] < 0.35:                        # 周期性が弱い＝有声でない
        continue
    f0s.append(sr / float(lag))

if not f0s:
    print("有声の区間が取れなかった（音声が無いか、小さすぎる）")
    sys.exit(1)

f0s = np.array(f0s)
med = float(np.median(f0s))
print("有声フレーム %d / 中央値 %.1f Hz / 下位25%% %.1f Hz / 上位25%% %.1f Hz"
      % (len(f0s), med, float(np.percentile(f0s, 25)), float(np.percentile(f0s, 75))))
if med < 160:
    print("→ 男性の声の範囲（85〜155Hzが成人男性の目安）")
elif med < 175:
    print("→ 男女の境目。耳で確かめたほうがいい")
else:
    print("→ 女性の声の範囲（165〜255Hzが成人女性の目安）")
os.remove(wav)
