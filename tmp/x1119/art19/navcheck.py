# -*- coding: utf-8 -*-
# 記事ページを携帯の幅で開き、下に読み進めたときに帯が上に残るか・矢印が出るか・押すと上に戻るかを確かめる
import io
from playwright.sync_api import sync_playwright
out = io.open('C:/Users/user/oshinavi/tmp/x1119/art19/navcheck.txt', 'w', encoding='utf-8')
with sync_playwright() as p:
    b = p.chromium.launch()
    for name in ('a/daibakushow.html', 'index.html', '2026-08-20.html', '2026-11-08/eliza.html'):
        pg = b.new_page(viewport={'width': 390, 'height': 760})
        pg.goto('file:///C:/Users/user/oshinavi/pickup/' + name)
        pg.mouse.wheel(0, 1500); pg.wait_for_timeout(600)
        y = pg.evaluate('window.scrollY')
        top = pg.evaluate("document.querySelector('header').getBoundingClientRect().top")
        show = pg.evaluate("document.getElementById('pkToTop').classList.contains('show')")
        if name == 'a/daibakushow.html':
            pg.screenshot(path='C:/Users/user/oshinavi/tmp/x1119/art19/navcheck.png')
        pg.click('#pkToTop'); pg.wait_for_timeout(1200)
        y2 = pg.evaluate('window.scrollY')
        out.write('%s 下へ=%d 帯の位置=%.0f 矢印=%s 押した後=%d\n' % (name, y, top, show, y2))
        pg.close()
    b.close()
out.close()
