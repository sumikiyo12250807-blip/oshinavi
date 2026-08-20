# -*- coding: utf-8 -*-
"""「海外」はジャンルでなくエリア（ユーザー指摘 2026-08-14）。
 ・GENRE_LABEL / ジャンルボタン / GENRE_GROUPS から kaigai を撤去
 ・PREFECTURE_TO_REGION に「台湾」→kaigai、エリアボタンに「🌏 海外」を追加
 ・id4259 のジャンルは fanevent（ファンイベント）に。エリアは prefecture=台湾 から自動で海外になる
index.html は CRLF。newline='' で読み書きし挿入行も \r\n（feedback_index_html_crlf_preserve）。"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in h else '\n'
orig = h

def sub1(pat, rep, why):
    global h
    h2, n = re.subn(pat, rep.replace('\n', NL), h, count=1)
    assert n == 1, '%s: 置換%d件' % (why, n)
    h = h2
    print('  ✓', why)

# ① ジャンルから撤去
sub1(re.escape('    fanevent: "ファンイベント", kaigai: "海外"'),
     '    fanevent: "ファンイベント"',
     'GENRE_LABEL から kaigai を撤去')
sub1(re.escape('        <button class="filter-btn" data-genre="kaigai">海外</button>\r\n')
     .replace('\\\r\\\n', '\r\n') if False else
     r'\s*<button class="filter-btn" data-genre="kaigai">海外</button>\r?\n',
     '\n', 'ジャンルボタンから海外を撤去')
sub1(re.escape('    odekake: ["sports","art","kids","fes","hanabi","gourmet","kaigai"]'),
     '    odekake: ["sports","art","kids","fes","hanabi","gourmet"]',
     'GENRE_GROUPS.odekake から kaigai を撤去')

# ② エリアとして追加
sub1(re.escape('    "大分": "kyushu", "宮崎": "kyushu", "鹿児島": "kyushu","沖縄": "kyushu",'),
     '    "大分": "kyushu", "宮崎": "kyushu", "鹿児島": "kyushu","沖縄": "kyushu",\n'
     '    // 海外公演（ぴあが日本の県を持たない興行）。バッジの「（台湾 M/D公演）」から拾う\n'
     '    "台湾": "kaigai",',
     'PREFECTURE_TO_REGION に 台湾→kaigai')
sub1(re.escape('    <button class="filter-btn" data-region="zenkoku">🚌 全国ツアー</button>'),
     '    <button class="filter-btn" data-region="kaigai">🌏 海外</button>\n'
     '    <button class="filter-btn" data-region="zenkoku">🚌 全国ツアー</button>',
     'エリアボタンに 🌏 海外 を追加')

# ③ id4259 のジャンルを fanevent に
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EV = json.loads(m.group(2))
for e in EV:
    if e.get('id') == 4259:
        e['genre'] = 'fanevent'
        e.pop('extraGenres', None)
        print('  ✓ id4259 → genre=fanevent / prefecture=%s（エリア=海外）' % e.get('prefecture'))
new_arr = json.dumps(EV, ensure_ascii=False, indent=2).replace('\n', NL)
h = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]

open('index.html.bak_0814_kaigai_area', 'w', encoding='utf-8', newline='').write(orig)
open('index.html', 'w', encoding='utf-8', newline='').write(h)
print('→ 適用（backup index.html.bak_0814_kaigai_area）')
