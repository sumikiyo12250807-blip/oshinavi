# -*- coding: utf-8 -*-
"""振り分け済みエントリに残った下書きフィールド(_genre/_extraGenres/_piaSub/_srcgenre)を掃除する。
   genre:"new" のエントリは対象外（下書きは振り分けに必要）。
   index.html の CRLF を壊さない（memory: feedback_index_html_crlf_preserve）。
   使い方: python tmp/clean_drafts_0727.py [--apply]
"""
import sys, io, re, json, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PATH = 'index.html'
DRAFT_FIELDS = ('_genre', '_extraGenres', '_piaSub', '_srcgenre')
apply = '--apply' in sys.argv

src = open(PATH, encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in src else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
assert m, 'EVENTS配列が見つからない'
events = json.loads(m.group(2))

targets = [e for e in events
           if e.get('genre') != 'new' and any(f in e for f in DRAFT_FIELDS)]
print(f'下書きが残っている振り分け済みエントリ: {len(targets)}件')

# 🚨 下書きと確定ジャンルが食い違っていないか確認（食い違い＝振り分けミスの痕跡）
mismatch = [e for e in targets if e.get('_genre') and e['_genre'] != e.get('genre')]
if mismatch:
    print(f'\n⚠️ 下書きと確定genreが違う {len(mismatch)}件（消す前に中身を見ること）:')
    for e in mismatch:
        print(f"   id{e['id']} 確定={e.get('genre')} / 下書き={e.get('_genre')}  {e.get('name','')[:44]}")
else:
    print('  下書きと確定genreの食い違い: なし')

c = collections.Counter()
for e in targets:
    for f in DRAFT_FIELDS:
        if f in e:
            c[f] += 1
print('\n消すフィールド内訳:', dict(c))

if not apply:
    print('\n(--apply で書き込み)')
    sys.exit(0)

for e in targets:
    for f in DRAFT_FIELDS:
        e.pop(f, None)

dumped = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl)
out = src[:m.start(2)] + dumped + src[m.end(2):]
open(PATH, 'w', encoding='utf-8', newline='').write(out)
print(f'\n書き込み完了: {len(targets)}件から下書きを除去')
