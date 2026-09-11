# -*- coding: utf-8 -*-
"""投稿のリスト行（時刻 名前／県）の「県」が47都道府県の名前になっているか確かめる（読むだけ）。"""
import glob, io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
P = ('北海道 青森 岩手 宮城 秋田 山形 福島 茨城 栃木 群馬 埼玉 千葉 東京 神奈川 新潟 富山 石川 福井 山梨 長野 岐阜 静岡 愛知 三重 '
     '滋賀 京都 大阪 兵庫 奈良 和歌山 鳥取 島根 岡山 広島 山口 徳島 香川 愛媛 高知 福岡 佐賀 長崎 熊本 大分 宮崎 鹿児島 沖縄').split()
ng = 0
for f in sorted(glob.glob('tmp/x0912/post*.txt')):
    for k, ln in enumerate(io.open(f, encoding='utf-8-sig').read().splitlines(), 1):
        m = re.match(r'^(?:\d{1,2}:\d{2}|時刻未定) .*／([^／]+)$', ln)
        if not m:
            continue
        s = re.sub(r'（先行）$', '', m.group(1))
        s = re.sub(r'\s*\d{1,2}/\d{1,2}〜.*$', '', s)
        bad = [x for x in s.split('・') if x not in P]
        if bad:
            ng += 1
            print('%s:%d %s  → %s' % (f[-10:], k, ln[:60], bad))
print('県名がおかしい行 %d' % ng)
