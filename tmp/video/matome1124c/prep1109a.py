# -*- coding: utf-8 -*-
# 11/9 お笑いまとめ：①背景 222382（黒地に青い雨粒・640×360・25.03秒）を縦 1080×1920 に（暗く・ぼかす）②テンポ
#   ③タップ画面（41576 マルコポロリ！20周年記念LIVE・11/9 18:00 先着先行）④歌詞の時刻（whisper small）
import io, os, re, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
env = dict(os.environ, PYTHONIOENCODING='utf-8')
out = io.open(D + 'prep1109a.txt', 'w', encoding='utf-8')


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


sub('bg_prep.py', [("gblur=sigma=1.5'   # 11/8", "gblur=sigma=6,colorchannelmixer=rr=0.5:gg=0.5:bb=0.5'   # 11/9 雨粒 222382（黒地に青い粒・拡大で大きくなる＝ぼかして半分の明るさ）／11/8")])
run('bg_prep.py')
sub('bg_video.py', [('FPS, L, XF = 30.0, 11.05, 0.6', 'FPS, L, XF = 30.0, 25.0, 0.6')])
run('tempo_check.py')
sub('shoot_badge.py', [("CID, Q, MD = 45605, '南海キャンディーズ寄席', '11/8'", "CID, Q, MD = 41576, 'マルコポロリ', '11/9'"),
                       ('new D(2026,10,7,20,0)', 'new D(2026,10,8,20,0)')])
run('shoot_badge.py')
# タップの箱は shoot_badge が測った screen_badge.json から読む（決め打ちの古い箱を使わない）
sub('badge_tap.py', [("BOXES = [[78, 617, 1036, 852]]", "import json as _j\nBOXES = _j.load(open(D + 'screen_badge.json'))['boxes'][:1] or [[78, 617, 1036, 852]]   # 11/9 測った箱")])
run('transcribe2.py')
out.write(io.open(D + 'lyrics_times2.txt', encoding='utf-8').read())
out.close()
open(D + 'prep1109a.done', 'w').close()
