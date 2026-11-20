# -*- coding: utf-8 -*-
# 試し動画＝書き出した out_x.mp4 の頭 12 秒（音つき）→ clip.mp4
import subprocess
import imageio_ffmpeg
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-y', '-v', 'error', '-i', D + 'out_x.mp4', '-t', '12', '-c:v', 'libx264', '-b:v', '1500k',
                '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', D + 'clip.mp4'], check=True)
