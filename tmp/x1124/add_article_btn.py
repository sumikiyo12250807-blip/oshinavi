# -*- coding: utf-8 -*-
# 11/24 朝 すちこ「記事に載ってるアーティストのところに、記事に行けるぼたんをつけてもいいわね」
# ＝カードのアーティスト名のすぐ下に「📰 この公演の記事を読む」（PICKUP_BY_ID に id がある時だけ）。鍵の中で書く・CRLF を保つ
import io, os, sys, time, subprocess
os.chdir('C:/Users/user/oshinavi')
LK = 'tmp/x1112/index.lock'
while True:
    try:
        fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'article_btn'); os.close(fd); break
    except FileExistsError:
        time.sleep(10)
try:
    t = io.open('index.html', encoding='utf-8', newline='').read()
    css_a = '.hotel-wide-btn img{width:100%;height:auto;display:block}'
    css_b = css_a + '\r\n.article-btn{display:inline-block;margin:6px 0 2px;padding:5px 12px;border-radius:999px;background:#fff4d6;color:#7a4b00;border:1px solid #f0c060;font-size:13px;font-weight:700;text-decoration:none}\r\n.article-btn:active{transform:translateY(1px)}'
    tpl_a = '            <div class="event-name${ev.artist && ev.artist.trim() === (ev.name||\'\').trim() ? \' solo\' : \'\'}">${ev.name}</div>\r\n'
    tpl_b = tpl_a + '            ${PICKUP_BY_ID[ev.id] ? `<a class="article-btn" href="${PICKUP_BY_ID[ev.id]}">📰 この公演の記事を読む</a>` : \'\'}\r\n'
    assert t.count(css_a) == 1 and t.count(tpl_a) == 1, (t.count(css_a), t.count(tpl_a))
    if 'class="article-btn"' not in t:
        t = t.replace(css_a, css_b).replace(tpl_a, tpl_b)
        io.open('index.html', 'w', encoding='utf-8', newline='').write(t)
        print('ボタンを足した')
finally:
    os.remove(LK)
r = subprocess.run([sys.executable, 'tools/pickup_card_links.py', '--apply', '--lock', LK], capture_output=True, text=True, encoding='utf-8')
print(r.stdout, r.stderr[-800:])
