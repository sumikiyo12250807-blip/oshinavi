# -*- coding: utf-8 -*-
# 最終版：mk_page_1111 の試し動画2本の段を、全編（Downloads/oshinavi_1111_owarai_matome.mp4）1本に替える・締めの1コマは全編から（ページの上限 16MB）
import io
p = 'C:/Users/user/oshinavi/tmp/video/matome1124c/mk_page_1111.py'
s = io.open(p, encoding='utf-8').read()
s = s.replace("vids = {k: base64.b64encode(open(D + 'clip_%s_s.mp4' % k, 'rb').read()).decode() for k in ('walk', 'end')}",
              "vids = {'final': base64.b64encode(open('C:/Users/user/Downloads/oshinavi_1111_owarai_matome.mp4', 'rb').read()).decode()}")
s = s.replace("end = Image.open(D + 'frames/h_073.7.png')", "end = Image.open(D + 'final/end_73.7.png')")
a = s.index("<section><h2>試し動画</h2>")
b = s.index("</div></section>", a) + len("</div></section>")
s = s[:a] + """<section><h2>全編（1分15秒）</h2><div class="vids">
<figure><video controls playsinline preload="metadata" src="data:video/mp4;base64,{vids['final']}"></video><figcaption>Downloads の oshinavi_1111_owarai_matome.mp4 と同じもの。長さ 1分15秒・8.0MB・音ずれなし・字幕は曲の歌詞と同じ順</figcaption></figure>
</div></section>""" + s[b:]
s = s.replace("<h1>11/11(水)発売 お笑いまとめ（今夜の X）の絵コンテ</h1>", "<h1>11/11(水)発売 お笑いまとめ（今夜の X）・ 全編</h1>")
s = s.replace("締めの1コマ（終わりの2秒前・73.7秒）", "締めの1コマ（全編の終わりの2秒前・73.7秒）")
assert "vids['final']" in s and 'end_73.7.png' in s
exec(compile(s, 'mk_page_1111f', 'exec'))
