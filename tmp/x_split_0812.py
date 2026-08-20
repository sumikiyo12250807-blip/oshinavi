# -*- coding: utf-8 -*-
"""Fableの8本を1本ずつのファイルに割る（予約する順に p2..p8）。"""
import os
import re

D = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(D, 'x_posts_0812.txt'), 'r', encoding='utf-8') as f:
    raw = f.read()

blocks = re.split(r'^===(.+?)===\s*$', raw, flags=re.M)[1:]
posts = {}
for i in range(0, len(blocks), 2):
    key = blocks[i].strip().split()[0]          # 先頭の番号
    body = re.sub(r'^\[全\d+字\]\s*$', '', blocks[i + 1], flags=re.M).strip('\n')
    posts[key] = body

# 予約する順（キー=Fableの番号） -> 出力名, 予約時刻
PLAN = [
    ('4', 'p2_rise',        '10:15'),
    ('1', 'p3_kyuso',       '10:45'),
    ('2', 'p4_candytune',   '11:15'),
    ('8', 'p5_jo0ji',       '11:35'),
    ('5', 'p6_cinemastaff', '11:50'),
    ('6', 'p7_dezert',      '12:20'),
    ('7', 'p8_sistershigh', '18:45'),
]

for key, name, when in PLAN:
    body = posts[key]
    p = os.path.join(D, name + '.txt')
    with open(p, 'w', encoding='utf-8', newline='\n') as f:
        f.write(body)
    print('%s  %s  %d字' % (when, name, len(body)))
