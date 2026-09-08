# -*- coding: utf-8 -*-
"""渡された音声を10秒ごとに区切って「声の高さ」と「音量」を測る。
H3の参照音声は合計15秒までなので、どこを切るかを決めるために使う。
使い方: python tools/audio_probe.py <in.mp3> [--seg 10]
出力はファイル（コンソールはcp932で日本語が化けるため）。
"""
import io, os, sys, math, wave, array, subprocess, argparse
import imageio_ffmpeg

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def to_wav(src, dst, sr=16000):
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([ff, "-y", "-i", src, "-ac", "1", "-ar", str(sr), dst],
                   capture_output=True, check=True)


def f0_median(samples, sr):
    """自己相関で基本周波数の中央値を出す（tools/voice_pitch.py と同じ考え方）。"""
    win = int(sr * 0.04)
    hop = int(sr * 0.02)
    lo, hi = int(sr / 400), int(sr / 60)      # 60〜400Hz を探す
    vals = []
    for s in range(0, max(0, len(samples) - win), hop):
        w = samples[s:s + win]
        e = sum(x * x for x in w) / win
        if e < 1e-4:
            continue
        best, bestv = 0, 0.0
        for lag in range(lo, min(hi, win - 1)):
            v = 0.0
            for i in range(0, win - lag, 4):
                v += w[i] * w[i + lag]
            if v > bestv:
                bestv, best = v, lag
        if best:
            vals.append(sr / best)
    vals.sort()
    return vals[len(vals) // 2] if vals else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--seg", type=float, default=10.0)
    ap.add_argument("--out", default="tmp/audio_probe.txt")
    a = ap.parse_args()

    tmpwav = "tmp/_probe.wav"
    os.makedirs("tmp", exist_ok=True)
    to_wav(a.src, tmpwav)

    w = wave.open(tmpwav, "rb")
    sr = w.getframerate()
    n = w.getnframes()
    raw = w.readframes(n)
    w.close()
    arr = array.array("h")
    arr.frombytes(raw)
    data = [x / 32768.0 for x in arr]
    dur = n / sr

    o = io.open(a.out, "w", encoding="utf-8")
    o.write("=== %s ===\n" % os.path.basename(a.src))
    o.write("長さ %.1f秒 / %dHz\n\n" % (dur, sr))
    o.write("| 区間 | 音量(RMS) | 声の高さ中央値 | 目安 |\n|---|---|---|---|\n")
    t = 0.0
    while t < dur:
        s0, s1 = int(t * sr), int(min(dur, t + a.seg) * sr)
        seg = data[s0:s1]
        if not seg:
            break
        rms = math.sqrt(sum(x * x for x in seg) / len(seg))
        f0 = f0_median(seg, sr)
        if f0 == 0:
            label = "無音に近い"
        elif f0 < 165:
            label = "男性の範囲"
        elif f0 <= 255:
            label = "女性の範囲"
        else:
            label = "かなり高い"
        o.write("| %.0f〜%.0f秒 | %.3f | %.0fHz | %s |\n"
                % (t, min(dur, t + a.seg), rms, f0, label))
        t += a.seg
    o.close()
    print("wrote %s (%.1fs)" % (a.out, dur))


if __name__ == "__main__":
    main()
