# -*- coding: utf-8 -*-
# 11/23 夜に予約した 11/24 発売の X（4本）の動画を x_media_log.json の rows に足す
import io, json
P = 'C:/Users/user/oshinavi/tmp/x_media_log.json'
d = json.load(io.open(P, encoding='utf-8'))
for post, f in (('mat01 まとめ スポーツ・おでかけ・舞台（19:31）', 'oshinavi_1124_classic_matome_x.mp4'), ('mat03 まとめ 音楽＝J-POP・クラシック・ロック・アイドル（20:01）', 'oshinavi_1124_live_matome_x.mp4')):
    d['rows'].append({'date': '2026-11-23', 'post': post, 'media': 'video', 'file': 'Downloads/' + f,
                      'note': '1晩4本（トレンド枠なし）・15分おき。クラシックとおでかけの動画はスポーツ・おでかけ・舞台のまとめに付けた'})
io.open(P, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1))
