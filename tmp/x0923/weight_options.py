# -*- coding: utf-8 -*-
"""「1〜2秒画面が暗くなる」への打ち手を、減る量で並べる（2026-09-23 夜）。
🚨実装はしない＝数字を出すだけ。サイトの根幹（AIに読ませる仕組み）に触る案が入っているので
   ユーザーが決める（[[reference_oshinavi_ai_page]]／[[project_index_html_size_ceiling]]）。
使い方: python tmp/x0923/weight_options.py
"""
import io
import json
import re

P = 'index.html'
raw = io.open(P, 'rb').read()
s = raw.decode('utf-8')
total = len(raw)

m = re.search(r'(  const EVENTS = )(\[)', s)
start = m.start(2)
events, end = json.JSONDecoder().raw_decode(s, start)
ev_bytes = len(s[start:end].encode('utf-8'))

mssr = re.search(r'<!-- AI_SSR_START -->(.*?)<!-- AI_SSR_END -->', s, re.S)
ssr = mssr.group(1)
ssr_bytes = len(ssr.encode('utf-8'))
lis = re.findall(r'<li>.*?</li>', ssr, re.S)
per_li = ssr_bytes / max(1, len(lis))

compact = len(json.dumps(events, ensure_ascii=False, separators=(',', ':')).encode('utf-8'))
pub = [e for e in events if e.get('genre') != 'new']
pub_compact = len(json.dumps(pub, ensure_ascii=False, separators=(',', ':')).encode('utf-8'))


def mb(n):
    return '%.2f MB' % (n / 1024.0 / 1024)


rows = []
rows.append(('A 何もしない（いま）', total, ''))
rows.append(('B EVENTSを詰めて書く', total - ev_bytes + compact,
             '表示は変わらない。道具は indent=2 のままで、push直前だけ詰める'))
rows.append(('C B＋新着%d件を公開用から外す' % (len(events) - len(pub)), total - ev_bytes + pub_compact,
             '振り分け前の分は元々タブに出していない'))
for n in (300, 500, 1000):
    keep = int(per_li * n)
    rows.append(('D SSRを先頭%d件に絞る（Bと一緒に）' % n, total - ev_bytes + compact - ssr_bytes + keep,
                 'AIがトップで読めるのが%d件になる。残りは ai_*.html 325ページにある' % n))

out = []
out.append('「1〜2秒画面が暗くなる」への打ち手（%s・%d件・SSR %d件）' % (mb(total), len(events), len(lis)))
out.append('')
out.append('%-34s %10s %10s' % ('案', '全体', '減る量'))
for name, sz, note in rows:
    out.append('%-34s %10s %10s' % (name, mb(sz), mb(total - sz) if total != sz else '-'))
    if note:
        out.append('    %s' % note)
out.append('')
out.append('※暗い1〜2秒＝①ダウンロード ②JSONのパース ③初回描画 の合計。')
out.append('  B・Cは①に効く。Dは①に大きく効く（人間の画面には出ない部分だから）。')
out.append('  ②③まで効かせるなら「最初に見える分だけ読む」作りに変える（大改修・別の日に）。')
out.append('')
out.append('🚨Dは [[reference_oshinavi_ai_page]] の「AIにトップを読ませる」仕組みを削る案＝')
out.append('  検索やAIからの見つかりやすさに関わる。ユーザーが決めること。')

txt = '\n'.join(out) + '\n'
io.open('tmp/x0923/weight_options.txt', 'w', encoding='utf-8').write(txt)
print(txt)
