# -*- coding: utf-8 -*-
"""子ども向けの作品ごとの「〇〇グッズ」ボタンを index.html に入れる（2026-09-15 夜・ユーザー「グッズで作って」）
前提: python tmp/btn/btn_from_cd_0915.py --kids-goods で tmp/btn_tpl/kgNN_88.png ができていること
・画像を img/btn2_kgNN.png に置く
・KIDS_WORK_AMAZON のしまじろうの行の下に作品の行を足す（並び順は kids_goods.json の順＝シナモロール等をサンリオより前）
・BTN_IMG の「しまじろうグッズ」の行の下に画像の行を足す
・改行は CRLF のまま（newline=''）／書いたあと EVENTS の件数が変わっていないこと・足した行の数を数える
使い方: python apply_kids_goods_0915.py
"""
import json
import re
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')
KG_EXCLUDE = {"シンドバッドグッズ"}   # btn_from_cd_0915.py と同じ
P = 'index.html'
kg = [r for r in json.load(open('tmp/btn_tpl/kids_goods.json', encoding='utf-8')) if r['ok'] and r['label'] not in KG_EXCLUDE]


def events(text):
    return json.loads(re.search(r'  const EVENTS = (\[.*?\]);', text, re.S).group(1))


with open(P, encoding='utf-8', newline='') as f:
    text = f.read()
n_before = len(events(text))
shutil.copyfile(P, 'index.html.bak_0915_kids_goods')

work_lines, img_lines = [], []
for i, r in enumerate(kg):
    name = 'kg%02d' % (i + 1)
    shutil.copyfile('tmp/btn_tpl/%s_88.png' % name, 'img/btn2_%s.png' % name)
    assert '"' not in r['label'] and '/' not in r['event_re']
    work_lines.append('      { re: /%s/, url: "%s", label: "%s" },' % (r['event_re'], r['url'], r['label']))
    img_lines.append('      "%s": "img/btn2_%s.png",' % (r['label'], name))

lines = text.split('\r\n')
iw = [k for k, ln in enumerate(lines) if ln.startswith('      { re: /しまじろう/')]
ii = [k for k, ln in enumerate(lines) if ln.startswith('      "しまじろうグッズ": "img/btn2_shimajiro.png"')]
assert len(iw) == 1 and len(ii) == 1, (iw, ii)
assert not any('"img/btn2_kg' in ln for ln in lines), 'もう入っている'
# 後ろ側から挿す（前を挿すと後ろの行番号がずれる）
for k, add in sorted([(iw[0], work_lines), (ii[0], img_lines)], reverse=True):
    lines[k + 1:k + 1] = add
new = '\r\n'.join(lines)
assert len(events(new)) == n_before, '件数が変わった'
with open(P, 'w', encoding='utf-8', newline='') as f:
    f.write(new)
print('足した作品 %d（ボタンの表 %d行・画像の割り当て %d行）' % (len(kg), len(work_lines), len(img_lines)))
for r in kg:
    print(' -', r['label'], r['hits'])
print('予備: index.html.bak_0915_kids_goods')
