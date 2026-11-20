# -*- coding: utf-8 -*-
# 11/10 お笑いまとめ：①背景 104570（緑〜青の波・明るい 152・640×360・30.02秒）を縦 1080×1920 に（ぼかして 0.6 倍の明るさ＝白／黄の字と縁取りが読める）
#   ②テンポ ③タップ画面（50254 M-1グランプリ2026 準々決勝・11/10 11:00 抽選先行）④歌詞の時刻（whisper small）
import io, os, re, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
env = dict(os.environ, PYTHONIOENCODING='utf-8')
out = io.open(D + 'prep1110a.txt', 'w', encoding='utf-8')


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


sub('bg_prep.py', [("gblur=sigma=6,colorchannelmixer=rr=0.5:gg=0.5:bb=0.5'   # 11/9", "gblur=sigma=3,colorchannelmixer=rr=0.6:gg=0.6:bb=0.6'   # 11/10 緑〜青の波 104570（明るい 152＝0.6 倍で約 90・波の形は残す）／11/9")])
run('bg_prep.py')
sub('bg_video.py', [('FPS, L, XF = 30.0, 25.0, 0.6', 'FPS, L, XF = 30.0, 30.0, 0.6')])
run('tempo_check.py')
sub('shoot_badge.py', [("CID, Q, MD = 41576, 'マルコポロリ', '11/9'", "CID, Q, MD = 50254, 'M-1グランプリ', '11/10'"),
                       ('new D(2026,10,8,20,0)', 'new D(2026,10,9,20,0)')])
run('shoot_badge.py')
run('transcribe2.py')
out.write(io.open(D + 'lyrics_times2.txt', encoding='utf-8').read())
out.close()
open(D + 'prep1110a.done', 'w').close()
