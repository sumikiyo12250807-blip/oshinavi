# -*- coding: utf-8 -*-
# 文字起こしで拾えなかった所だけ切り出して、その所の歌詞（USLT の並び）を手がかりに言葉の頭を取り直す → lyrics_part.txt
#   ① 26.0〜31.0 秒（ちょこれーとぷらねっと とうきょう → たかあんどとし とうきょう → まゆりか とうきょう → くうきかいだん）
#   ② 7.5〜12.5 秒（おわらい いうわね）
import io, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
import imageio_ffmpeg
from faster_whisper import WhisperModel
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
ff = imageio_ffmpeg.get_ffmpeg_exe()
PARTS = [(26.0, 31.0, 'ちょこれーとぷらねっと とうきょう たかあんどとし とうきょう まゆりか とうきょう くうきかいだん とうきょう'),
         (7.5, 12.5, 'はつばいの おわらい いうわね')]
m = WhisperModel('small', device='cpu', compute_type='int8')
out = io.open(D + 'lyrics_part.txt', 'w', encoding='utf-8')
for i, (a, b, pr) in enumerate(PARTS):
    w = D + 'part%d.wav' % i
    subprocess.run([ff, '-y', '-v', 'error', '-ss', str(a), '-t', str(b - a), '-i', D + 'song.mp3', '-ac', '1', '-ar', '16000', w], check=True)
    for model_pr in (pr, None):
        segs, _ = m.transcribe(w, language='ja', vad_filter=False, word_timestamps=True, initial_prompt=model_pr)
        out.write('==== %.1f〜%.1f prompt=%s\n' % (a, b, bool(model_pr)))
        for s in segs:
            out.write('%6.2f %6.2f %s\n' % (a + s.start, a + s.end, s.text))
            out.write('   ' + ' '.join('%.2f:%s' % (a + x.start, x.word) for x in s.words) + '\n')
out.close()
# 音の大きさ（0.1 秒ごと・26〜31 秒）
import numpy as np
raw = subprocess.run([ff, '-v', 'error', '-ss', '26', '-t', '5', '-i', D + 'song.mp3', '-ac', '1', '-ar', '16000', '-f', 's16le', '-'], capture_output=True).stdout
y = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768
io.open(D + 'lyrics_part.txt', 'a', encoding='utf-8').write('rms26-31 ' + ' '.join('%.1f:%.2f' % (26 + i / 10, float(np.sqrt(np.mean(y[i * 1600:(i + 1) * 1600] ** 2)))) for i in range(50)) + '\n')
print('done')
