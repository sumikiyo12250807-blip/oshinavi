# -*- coding: utf-8 -*-
"""id4045 ブランデー戦記を「札幌1公演」→「3会場ツアー」に差し替える。
既存の genre / _extraGenres 等の振り分け結果は保持し、公演情報だけ機械構築の結果で上書きする。
index.html は CRLF 維持（memory: feedback_index_html_crlf_preserve）。
"""
import re, json, io, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

built = json.load(io.open('tmp/entries_brandy_0813.json', encoding='utf-8'))[0]
assert built['id'] == 4045

h = io.open('index.html', encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in h else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
assert m, 'EVENTS配列が見つからない'
EVENTS = json.loads(m.group(2))

tgt = [e for e in EVENTS if e['id'] == 4045]
assert len(tgt) == 1, 'id4045 が %d件' % len(tgt)
e = tgt[0]
print('BEFORE genre=%s venue=%s tickets=%d' % (e.get('genre'), e.get('venue'), len(e.get('tickets') or [])))

# 公演情報だけ差し替え（ジャンル振り分けの結果は触らない）
for k in ('name', 'artist', 'date', 'dateLabel', 'venue', 'prefecture', 'tickets',
          'verified', 'verifiedAt'):
    e[k] = built[k]
# links は amazon 等の既存値を残しつつ pia を代表URLへ更新
links = e.get('links') or {}
links['pia'] = built['links']['pia']
for k, v in (built.get('links') or {}).items():
    if v and not links.get(k):
        links[k] = v
e['links'] = links

print('AFTER  genre=%s venue=%s tickets=%d' % (e.get('genre'), e.get('venue'), len(e.get('tickets') or [])))

bak = 'index.html.bak_%s_brandy' % datetime.date.today().strftime('%m%d')
io.open(bak, 'w', encoding='utf-8', newline='').write(h)
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
io.open('index.html', 'w', encoding='utf-8', newline='').write(
    h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print('差し替え完了 (backup %s)' % bak)
