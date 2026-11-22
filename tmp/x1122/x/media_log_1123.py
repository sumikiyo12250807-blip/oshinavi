# -*- coding: utf-8 -*-
# 11/22 夜に予約した 11/23 発売の X（5本の新しい形）の動画を x_media_log.json の rows に足す
import io, json
P = 'C:/Users/user/oshinavi/tmp/x_media_log.json'
d = json.load(io.open(P, encoding='utf-8'))
for post, f in (('mat02 まとめ お笑い（19:51）', 'oshinavi_1123_owarai_matome_x.mp4'), ('mat03 まとめ 音楽＝J-POP・クラシック・ロック・アイドル（20:01）', 'oshinavi_1123_jpoprock_matome_x.mp4')):
    d['rows'].append({'date': '2026-11-22', 'post': post, 'media': 'video', 'file': 'Downloads/' + f,
                      'note': '前に作った動画（TikTok先出しの分）を最初から付けて予約・この日から1晩5本（トレンド・スポーツ/おでかけ/舞台・お笑い・音楽・主役1本）'})
io.open(P, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1))
print(len(d['rows']))
