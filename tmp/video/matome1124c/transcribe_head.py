# -*- coding: utf-8 -*-
# 頭の 0〜32秒だけ切り出して文字起こし（全体の起こしは 30.2 秒より前が抜けた）→ lyrics_times_head.txt
import io, subprocess, sys
import imageio_ffmpeg
from faster_whisper import WhisperModel
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-y', '-i', D + 'song.mp3', '-t', '32', '-ac', '1', '-ar', '16000', D + 'head.wav'], capture_output=True)
L = [l for l in io.open(D + 'mine.txt', encoding='utf-8').read().splitlines() if l and not l.startswith('[')]
P = ' '.join(L[:12])
m = WhisperModel('small', device='cpu', compute_type='int8')
out = io.open(D + 'lyrics_times_head.txt', 'w', encoding='utf-8')
for vad in (False, True):
    segs, _ = m.transcribe(D + 'head.wav', language='ja', vad_filter=vad, word_timestamps=True, initial_prompt=P)
    out.write('==== vad=%s\n' % vad)
    for s in segs:
        out.write('%6.2f %6.2f %s\n' % (s.start, s.end, s.text))
        out.write('   ' + ' '.join('%.1f:%s' % (w.start, w.word) for w in s.words) + '\n')
out.close()
