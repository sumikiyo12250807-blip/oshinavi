# -*- coding: utf-8 -*-
# 10/1夜の動画を台帳 tmp/x_media_log.json に足す（Mamma Mia 3本目＝J-POPまとめ）
import io, json
p = 'C:/Users/user/oshinavi/tmp/x_media_log.json'
d = json.load(io.open(p, encoding='utf-8'))
d['rows'].append({'date': '2026-10-01', 'post': 'post05 J-POP・ロック・K-POPまとめ（21:01）', 'media': 'video',
                  'file': 'tmp/video/mamma/clip3_x.mp4', 'len_sec': 10,
                  'note': 'Mamma Mia Midnight 3本目（clip3.mp4 10.7MB→6.3MBに縮めた）。最初に oshimade_full を付けかけてユーザー「動画　明日だよそれは」＝外して付け直した。oshimade_full_x.mp4（9MB・720p）は 10/2夜に使う'})
io.open(p, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1))
print('ok', len(d['rows']))
