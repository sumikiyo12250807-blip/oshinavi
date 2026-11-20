# -*- coding: utf-8 -*-
# 11/13 お笑い（TikTok 用）：①背景 73197（夜のビル街・窓の明かりの粒・明るさ 57〜75・640×360・20.02秒）を縦 1080×1920 に
#   粒が細かく字の後ろでうるさい＝ぼかし 5・0.55 倍（白／黄の字と縁取りが読める・上も粒が残る＝上が暗く空かない）
#   ②ループの長さ 20.0 秒 ③タップ画面（50272 とろサーモン久保田 初ソロトークライブ・11/13 10:00 一般発売・前の夜の時計 11/12 20:00）
import io, os, re, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
env = dict(os.environ, PYTHONIOENCODING='utf-8')
out = io.open(D + 'prep1113a.txt', 'w', encoding='utf-8')


def run(f, *a):
    r = subprocess.run([sys.executable, D + f] + list(a), capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    out.write('== %s %s rc %s\n%s\n%s\n' % (f, a, r.returncode, r.stdout[-2500:], r.stderr[-2500:]))
    out.flush()
    return r.returncode


def sub(f, pairs):
    s = io.open(D + f, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (f, a)
        s = s.replace(a, b)
    io.open(D + f, 'w', encoding='utf-8').write(s)


sub('bg_prep.py', [("gblur=sigma=3,colorchannelmixer=rr=0.6:gg=0.6:bb=0.6'   # 11/10 緑", "gblur=sigma=5,colorchannelmixer=rr=0.55:gg=0.55:bb=0.55'   # 11/13 夜のビル街 73197（窓の粒が字の後ろでうるさい＝ぼかし5・0.55倍）／11/10 緑")])
run('bg_prep.py')
s = io.open(D + 'bg_video.py', encoding='utf-8').read()
out.write('bg_video FPS 行: %s\n' % re.findall(r'FPS, L, XF = .*', s))
s = re.sub(r'FPS, L, XF = [\d.]+, [\d.]+, [\d.]+', 'FPS, L, XF = 30.0, 20.0, 0.6', s, count=1)
io.open(D + 'bg_video.py', 'w', encoding='utf-8').write(s)
sb = io.open(D + 'shoot_badge.py', encoding='utf-8').read()
out.write('shoot_badge 設定: %s %s\n' % (re.findall(r"CID, Q, MD = .*", sb), re.findall(r"new D\([\d,]+\)", sb)))
sb = re.sub(r"CID, Q, MD = .*", "CID, Q, MD = 50272, 'とろサーモン', '11/13'", sb, count=1)
sb = re.sub(r"new D\(2026,\d+,\d+,20,0\)", "new D(2026,10,12,20,0)", sb)
io.open(D + 'shoot_badge.py', 'w', encoding='utf-8').write(sb)
run('shoot_badge.py')
out.close()
open(D + 'prep1113a.done', 'w').close()
