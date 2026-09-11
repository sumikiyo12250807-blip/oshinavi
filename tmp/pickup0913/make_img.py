# -*- coding: utf-8 -*-
"""ユーザーがChatGPTで作った『コーラスライン』のイメージ画像（1.9MBのPNG）を、記事用のJPGに縮める。
加工はしない（切り抜き・文字入れなし）＝幅だけ1200pxに。"""
import sys
from PIL import Image
sys.stdout.reconfigure(encoding='utf-8')
# 21:48 の版＝ダンサーが客席を向き、演出家は客席の通路（ユーザー「まっいっか」で採用・ラインの上は18人）
# 21:10（演出家が女性・11人）／21:14（11人）／21:31（ダンサーが舞台の奥を向いている＝向きが逆）は使わない
SRC = r'C:\Users\user\Downloads\ChatGPT Image 2026年9月11日 21_48_33.png'
OUT = 'img/chorusline_ai.jpg'
im = Image.open(SRC).convert('RGB')
w, h = im.size
im = im.resize((1200, round(h * 1200 / w)), Image.LANCZOS)
im.save(OUT, 'JPEG', quality=82, optimize=True, progressive=True)
import os
print('%dx%d → %dx%d / %d KB' % (w, h, im.size[0], im.size[1], os.path.getsize(OUT) // 1024))
