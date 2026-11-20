# -*- coding: utf-8 -*-
# 試し動画をページ用に小さく（540×960・crf 28）→ clip_names_s.mp4・clip_end_s.mp4、mk_page をその2本で
import io, os, subprocess
import imageio_ffmpeg
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
ff = imageio_ffmpeg.get_ffmpeg_exe()
for k in ('names', 'end'):
    subprocess.run([ff, '-y', '-v', 'error', '-i', D + 'clip_%s.mp4' % k, '-vf', 'scale=540:960', '-c:v', 'libx264', '-crf', '28', '-preset', 'medium',
                    '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', D + 'clip_%s_s.mp4' % k], check=True)
    print(k, os.path.getsize(D + 'clip_%s.mp4' % k) // 1024, '→', os.path.getsize(D + 'clip_%s_s.mp4' % k) // 1024, 'KB')
s = io.open(D + 'mk_page.py', encoding='utf-8').read()
s = s.replace("(('names', 'clip_names.mp4'), ('end', 'clip_end.mp4'))", "(('names', 'clip_names_s.mp4'), ('end', 'clip_end_s.mp4'))")
io.open(D + 'mk_page.py', 'w', encoding='utf-8').write(s)
