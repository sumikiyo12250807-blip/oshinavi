# -*- coding: utf-8 -*-
# 最終版：mk_page2 の形で、試し動画2本の段を最終版（Downloads/oshinavi_1113_owarai_matome.mp4）1本に替える（ページの上限 16MB）
import io, re
p = 'C:/Users/user/oshinavi/tmp/video/matome1124c/mk_page2.py'
s = io.open(p, encoding='utf-8').read()
s = s.replace("for k in ('walk', 'end'):\n    subprocess.run(", "for k in ():\n    subprocess.run(")
s = s.replace("vids = {k: base64.b64encode(open(D + 'clip_%s_s.mp4' % k, 'rb').read()).decode() for k in ('walk', 'end')}",
              "vids = {'final': base64.b64encode(open('C:/Users/user/Downloads/oshinavi_1113_owarai_matome.mp4', 'rb').read()).decode()}")
s = s.replace("cw = [l for l in txt.splitlines() if l.startswith('clip_walk')][0].split()[1]\n", "")
s = s.replace("end = Image.open(D + 'frames/h_105.0.png')", "end = Image.open(D + 'final/end_105.png')")
a = s.index("<section><h2>試し動画</h2>")
b = s.index("</div></section>", a) + len("</div></section>")
s = s[:a] + """<section><h2>最終版（1分47秒）</h2><div class="vids">
<figure><video controls playsinline preload="metadata" src="data:video/mp4;base64,{vids['final']}"></video><figcaption>Downloads の oshinavi_1113_owarai_matome.mp4 と同じもの。長さ 1分47秒・音ずれなし・字幕は曲の歌詞と1行ずつ同じ</figcaption></figure>
</div></section>""" + s[b:]
s = s.replace("<h1>11/13(金)発売 お笑いまとめ（TikTok）の絵コンテ ・ 第2版</h1>", "<h1>11/13(金)発売 お笑いまとめ（TikTok）・ 最終版</h1>")
s = s.replace("歌詞は前より少し下げ、タップの文字も「あと3日」に重ならない所へずらした。",
              "歌詞は前より少し下げ、タップの文字も「あと3日」に重ならない所へずらした。全編の点検で、時刻が次の人の頭に付いて見えた字幕2か所（東京 13時・大阪 12時 先行よ）と、タップの場面の歌詞と文字の重なりも直した。")
assert "vids['final']" in s and 'end_105.png' in s
io.open('C:/Users/user/oshinavi/tmp/video/matome1124c/mk_page3_run.py', 'w', encoding='utf-8').write(s)
print('ok')
