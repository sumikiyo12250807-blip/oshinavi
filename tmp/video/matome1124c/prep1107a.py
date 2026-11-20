# -*- coding: utf-8 -*-
# 11/7 お笑いまとめ：①着物シートを切る（cut_alpha9 k）→ look_pose 3人ずつ ②背景のコマ（127888）③テンポ ④タップ画面（46888 家でやりなはれ ミキ 11/7 10:00）
import io, os, re, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
env = dict(os.environ, PYTHONIOENCODING='utf-8')
out = io.open(D + 'prep1107a.txt', 'w', encoding='utf-8')


def run(f, *a):
    r = subprocess.run([sys.executable, D + f] + list(a), capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    out.write('== %s %s rc %s\n%s\n%s\n' % (f, a, r.returncode, r.stdout[-2500:], r.stderr[-2500:]))
    out.flush()


def sub(f, pairs, regex=False):
    s = io.open(D + f, encoding='utf-8').read()
    for a, b in pairs:
        if regex:
            s, n = re.subn(a, b, s, count=1)
            assert n == 1, (f, a)
        else:
            assert a in s, (f, a)
            s = s.replace(a, b)
    io.open(D + f, 'w', encoding='utf-8').write(s)


run('cut_alpha9.py', 'sheet_k.png', 'k')
out.write(io.open(D + 'cut9_k.txt', encoding='utf-8').read())
sub('look_pose.py', [("for sh in 'de':", "for sh in 'k':")])
run('look_pose.py', 'k1,k2,k3', 'look_123')
run('look_pose.py', 'k4,k5,k6', 'look_456')
run('look_pose.py', 'k7,k8,k9', 'look_789')
# 背景
r = subprocess.run([__import__('imageio_ffmpeg').get_ffmpeg_exe(), '-i', D + 'bg_src.mp4'], capture_output=True, text=True, errors='replace').stderr
out.write('bg info ' + ' '.join(re.findall(r'Duration: [\d:.]+|\d+ fps|\d+x\d+', r)) + '\n')
sub('bg_prep.py', [(r"vf = '.*?'", "vf = 'fps=30,scale=-2:1920:flags=lanczos,crop=1080:1920,gblur=sigma=2'")], regex=True)
run('bg_prep.py')
run('tempo_check.py')
# タップ画面
sub('shoot_badge.py', [(r"CID, Q, MD = 41806, '又吉直樹', '11/6'", "CID, Q, MD = 46888, '家でやりなはれ', '11/7'"),
                       ('new D(2026,10,5,20,0)', 'new D(2026,10,6,20,0)')])
run('shoot_badge.py')
out.close()
open(D + 'prep1107a.done', 'w').close()
