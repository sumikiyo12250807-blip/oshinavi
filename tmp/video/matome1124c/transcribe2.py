# -*- coding: utf-8 -*-
# 歌詞を手がかり（initial_prompt）にして文字起こしし直す（matome1026s/transcribe2.py の写し）＝言葉ごとの時刻と、81秒より後に何を歌っているか
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
from faster_whisper import WhisperModel
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
P = io.open(D + 'mine.txt', encoding='utf-8').read()
P = ' '.join(l for l in P.splitlines() if l and not l.startswith('['))
out = io.open(D + 'lyrics_times2.txt', 'w', encoding='utf-8')
for model in ('small',):
    m = WhisperModel(model, device='cpu', compute_type='int8')
    for vad in (False,):
        segs, _ = m.transcribe(D + 'song.mp3', language='ja', vad_filter=vad, word_timestamps=True, initial_prompt=P)
        out.write('==== %s vad=%s\n' % (model, vad))
        for s in segs:
            out.write('%6.2f %6.2f %s\n' % (s.start, s.end, s.text))
            out.write('   ' + ' '.join('%.1f:%s' % (w.start, w.word) for w in s.words) + '\n')
        out.flush()
out.close()
print('done')
