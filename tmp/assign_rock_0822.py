# -*- coding: utf-8 -*-
"""洋楽ロックの2件を rock に移す（2026-08-22 ユーザー決定「ロック系ならロックに入れてもいい／二つのカテゴリ」）。

  4947 EUROPE …………………… スウェーデンのハードロックバンド
  4959 マイケル・シェンカー・グループ … ドイツ出身のギタリスト率いるハードロックバンド

どちらもぴあのサブは「音楽/海外ROCK・POPS」で、名前そのものが「ROCK」の側。
迷う余地が無いのでここだけ動かす。国内の判断が要るものは今日は触らない。

🚨読み書きはテキストモードで統一（[[feedback_index_html_crcrlf_trap]]）。
"""
import json
import re
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')

TARGET = {4947: 'EUROPE', 4959: 'マイケル・シェンカー・グループ'}

path = 'index.html'
h = open(path, encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
by = {e['id']: e for e in EVENTS}

for i in sorted(TARGET):
    e = by[i]
    assert e.get('genre') == 'yougaku', (i, e.get('genre'))
    e['genre'] = 'rock'
    e['verifiedAt'] = '2026-08-22'
    print('id%s %s : yougaku → rock' % (i, e['name']))

shutil.copyfile(path, path + '.bak_0822_rock')
open(path, 'w', encoding='utf-8').write(
    h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
print('適用した（backup: index.html.bak_0822_rock）')
