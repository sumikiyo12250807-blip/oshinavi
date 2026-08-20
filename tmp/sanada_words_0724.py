# -*- coding: utf-8 -*-
"""真田ナオキのe+ word頁から全公演の-P detail URLを機械抽出する。
word頁は「真田ナオキのチケット」一覧＝真実ソース。JSで隠れる分も生HTMLには
/sf/detail/ リンクが入っていることが多いので生HTMLをgrepする。"""
import re, sys, json
sys.path.insert(0, 'tools')
from eplus_harvest import fetch, parse_ld
sys.stdout.reconfigure(encoding='utf-8')

WORD = 'https://eplus.jp/sf/word/0000126164'
h = fetch(WORD)

# 生HTMLから /sf/detail/<base>-P.... を全部拾う（重複除去・順序維持）
urls = []
for m in re.finditer(r'/sf/detail/([0-9A-Za-z\-]+)', h):
    u = 'https://eplus.jp/sf/detail/' + m.group(1)
    if u not in urls:
        urls.append(u)

print(f'word頁から detail URL {len(urls)}件抽出')
for u in urls:
    print('  ', u)

json.dump(urls, open('tmp/sanada_urls.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
