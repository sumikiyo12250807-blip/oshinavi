# -*- coding: utf-8 -*-
"""id5519 キム・チャンワンバンド の下書きジャンルを yougaku → kpop へ。
理由＝ぴあに K-POP 区分が無く「海外ROCK・POPS」に落ちるが、韓国のアーティストは kpop に読み替える
（feedback_kpop_vs_yougaku）。キム・チャンワンは韓国のバンド「산울림(サンウルリム)」のリーダー。
🚨 index.html は CRLF。json.dumps の LF を必ず元の改行へ戻す（feedback_index_html_crlf_preserve）。"""
import io, re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
PATH = 'index.html'
src = io.open(PATH, encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in src[:4000] else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
E = json.loads(m.group(2))
n = 0
for e in E:
    if e.get('id') == 5519:
        assert e.get('genre') == 'new', 'プールにいない'
        print('before:', e.get('name'), '|', e.get('_piaSub'), '|', e.get('_genre'))
        e['_genre'] = 'kpop'
        n += 1
assert n == 1, '対象が1件でない: %d' % n
dumped = json.dumps(E, ensure_ascii=False, indent=2).replace('\n', nl)
io.open(PATH, 'w', encoding='utf-8', newline='').write(src[:m.start(2)] + dumped + src[m.end(2):])
print('OK 書き戻した (改行=%r)' % nl)
