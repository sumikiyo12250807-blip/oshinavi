# -*- coding: utf-8 -*-
"""e+のジャンル一覧（/sf/live/j-pop）のHTML構造を調べる。
9/20に eplus_harvest cards が0件で返った原因を突き止める（カードのクラス名が変わったのか、
それともJSで後入れになったのか）。
"""
import io, re

html = open('tmp/eplus_jpop.html', encoding='utf-8', errors='replace').read()
out = io.open('tmp/eplus_struct_0921.txt', 'w', encoding='utf-8')
out.write('size=%d\n\n' % len(html))

ids = re.findall(r'/sf/detail/([0-9A-Za-z-]+)', html)
out.write('detailリンク %d本 / ユニーク %d本\n' % (len(ids), len(set(ids))))
out.write('  例: %s\n\n' % list(dict.fromkeys(ids))[:5])

for k in ('block-card-ticket__trigger', 'card-inner__license', 'card-inner__title',
          'card-inner__text', 'block-card-ticket', 'js-', 'data-props', 'nuxt', 'NEXT_DATA',
          'application/ld+json', 'vue', 'react'):
    out.write('%-26s %d回\n' % (k, html.count(k)))

out.write('\n=== detailリンクの周り（先頭3つ・前後300字）===\n')
for m in list(re.finditer(r'/sf/detail/[0-9A-Za-z-]+', html))[:3]:
    s = max(0, m.start() - 300)
    out.write('--- \n%s\n' % html[s:m.end() + 300].replace('\n', ' '))

out.write('\n=== 「もっと見る」「読み込み」系 ===\n')
for m in re.finditer(r'.{120}(もっと見る|読み込|loadMore|infinite).{120}', html, re.S):
    out.write(m.group(0).replace('\n', ' ') + '\n---\n')
out.close()
print('wrote tmp/eplus_struct_0921.txt')
