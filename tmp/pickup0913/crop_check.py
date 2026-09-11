# -*- coding: utf-8 -*-
"""人数を目で数えるための確認用の切り出し（記事には使わない・scratchpadに出す）。左半分と右半分を拡大して保存。"""
import sys
from PIL import Image
SRC = sys.argv[2] if len(sys.argv) > 2 else r'C:\Users\user\Downloads\ChatGPT Image 2026年9月11日 21_48_33.png'
OUT = sys.argv[1]
im = Image.open(SRC).convert('RGB')
im.crop((0, 420, 850, 700)).save(OUT + r'\left.png')
im.crop((850, 420, 1672, 700)).save(OUT + r'\right.png')
print('ok')
