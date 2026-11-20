# -*- coding: utf-8 -*-
# 11/8 お笑いまとめ：①背景 97396（花火・640×360・11.11秒）を縦 1080×1920 に ②テンポ ③歌詞の時刻（whisper small）④タップ画面（45605 南海キャンディーズ寄席 11/8 10:00）
import io, os, re, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
env = dict(os.environ, PYTHONIOENCODING='utf-8')
out = io.open(D + 'prep1108a.txt', 'w', encoding='utf-8')


def run(f, *a):
    r = subprocess.run([sys.executable, D + f] + list(a), capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    out.write('== %s %s rc %s\n%s\n%s\n' % (f, a, r.returncode, r.stdout[-2500:], r.stderr[-2500:]))
    out.flush()


def sub(f, pairs):
    s = io.open(D + f, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (f, a)
        s = s.replace(a, b)
    io.open(D + f, 'w', encoding='utf-8').write(s)


sub('bg_prep.py', [("gblur=sigma=2'   # 11/6", "gblur=sigma=1.5'   # 11/8 花火 97396（黒地＝暗くしない）／11/6")])
run('bg_prep.py')
sub('bg_video.py', [('FPS, L, XF = 30.0, 9.05, 0.6', 'FPS, L, XF = 30.0, 11.05, 0.6')])
run('tempo_check.py')
sub('shoot_badge.py', [("CID, Q, MD = 46888, '家でやりなはれ', '11/7'", "CID, Q, MD = 45605, '南海キャンディーズ寄席', '11/8'"),
                       ('new D(2026,10,6,20,0)', 'new D(2026,10,7,20,0)')])
run('shoot_badge.py')
run('transcribe2.py')
out.write(io.open(D + 'lyrics_times2.txt', encoding='utf-8').read())
out.close()
open(D + 'prep1108a.done', 'w').close()
