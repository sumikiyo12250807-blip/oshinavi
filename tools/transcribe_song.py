"""歌の文字起こし（時刻つき）。python tools/transcribe_song.py <mp3> [model]"""
import sys
from faster_whisper import WhisperModel
sys.stdout.reconfigure(encoding='utf-8')
m = WhisperModel(sys.argv[2] if len(sys.argv) > 2 else 'small', device='cpu', compute_type='int8')
segs, _ = m.transcribe(sys.argv[1], language='ja', vad_filter=False, word_timestamps=True,
                       initial_prompt='推し活なら Oshinavi.jp 推しに会いたい チケット カウントダウン')
for s in segs:
    print("   " + " ".join("%.1f:%s" % (w.start, w.word) for w in s.words))
    print('%6.2f %6.2f %s' % (s.start, s.end, s.text))
