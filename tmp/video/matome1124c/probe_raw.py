# -*- coding: utf-8 -*-
import io, subprocess
import imageio_ffmpeg
ff = imageio_ffmpeg.get_ffmpeg_exe()
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
out = []
for f in ('raw1.mp4', 'raw2.mp4'):
    r = subprocess.run([ff, '-hide_banner', '-i', D + f], capture_output=True, text=True, errors='replace')
    out.append(f + '\n' + r.stderr[-600:])
io.open(D + 'probe_raw.txt', 'w', encoding='utf-8').write('\n'.join(out))
