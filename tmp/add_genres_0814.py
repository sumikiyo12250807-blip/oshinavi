# -*- coding: utf-8 -*-
"""ジャンル追加（ユーザー指示 2026-08-14）:
  ・fanevent「ファンイベント」→ エンタメ群
  ・kaigai  「海外」        → おでかけ群
  ・gourmet「グルメ」は既存（追加不要・id4260 をそこへ）
あわせて相談3件のジャンルを確定する。
index.html は CRLF。newline='' で読み書きし、挿入行も \r\n で書く
（memory: feedback_index_html_crlf_preserve）。
"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

P = 'index.html'
h = open(P, encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in h else '\n'
orig = h

def sub1(pat, rep, why):
    global h
    h2, n = re.subn(pat, rep.replace('\n', NL), h, count=1)
    assert n == 1, '%s: 置換%d件' % (why, n)
    h = h2
    print('  ✓', why)

# ① GENRE_LABEL
sub1(re.escape('    gourmet: "グルメ"'),
     '    gourmet: "グルメ",\n    fanevent: "ファンイベント", kaigai: "海外"',
     'GENRE_LABEL に fanevent / kaigai')

# ② フィルタボタン（エンタメ群の末尾＝VTuberの後 / おでかけ群の末尾＝グルメの後）
sub1(re.escape('        <button class="filter-btn" data-genre="vtuber">VTuber</button>'),
     '        <button class="filter-btn" data-genre="vtuber">VTuber</button>\n'
     '        <button class="filter-btn" data-genre="fanevent">ファンイベント</button>',
     'エンタメ群にファンイベントのボタン')
sub1(re.escape('        <button class="filter-btn" data-genre="gourmet">グルメ</button>'),
     '        <button class="filter-btn" data-genre="gourmet">グルメ</button>\n'
     '        <button class="filter-btn" data-genre="kaigai">海外</button>',
     'おでかけ群に海外のボタン')

# ③ GENRE_GROUPS
sub1(re.escape('    ento:    ["owarai","kaidan","dinnershow","aisatsu","youtuber","vtuber"],'),
     '    ento:    ["owarai","kaidan","dinnershow","aisatsu","youtuber","vtuber","fanevent"],',
     'GENRE_GROUPS.ento に fanevent')
sub1(re.escape('    odekake: ["sports","art","kids","fes","hanabi","gourmet"]'),
     '    odekake: ["sports","art","kids","fes","hanabi","gourmet","kaigai"]',
     'GENRE_GROUPS.odekake に kaigai')

# ④ Amazonリンク（ファンミはペンライトを使う。海外は物販の当たりが読めないので付けない）
sub1(re.escape('      "2.5ji":  PENLIGHT_AMAZON,'),
     '      "2.5ji":  PENLIGHT_AMAZON,\n      fanevent: PENLIGHT_AMAZON,',
     'GENRE_AMAZON_LINKS に fanevent')

# ⑤ 相談3件のジャンル確定
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EV = json.loads(m.group(2))
ASSIGN = {
    4259: ('kaigai', ['fanevent']),   # 台北開催のファンイベント＝主=海外・従=ファンイベント
    4260: ('gourmet', []),            # 地酒と美食の祭典（下書きのkidsは誤り）
    4258: ('fanevent', []),           # ファンミーティングツアー
}
done = []
for e in EV:
    if e.get('id') in ASSIGN:
        g, extra = ASSIGN[e['id']]
        e['genre'] = g
        if extra:
            e['extraGenres'] = extra
        for k in ('_genre', '_extraGenres', '_piaSub'):
            e.pop(k, None)
        done.append((e['id'], g, extra, e.get('name')))
assert len(done) == 3, done
new_arr = json.dumps(EV, ensure_ascii=False, indent=2).replace('\n', NL)
h = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]
for r in done:
    print('  ✓ id%s → genre=%s extra=%s  %s' % (r[0], r[1], r[2], (r[3] or '')[:34]))

open('index.html.bak_0814_genres', 'w', encoding='utf-8', newline='').write(orig)
open(P, 'w', encoding='utf-8', newline='').write(h)
print('→ 適用（backup index.html.bak_0814_genres）')
