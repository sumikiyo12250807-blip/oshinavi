# -*- coding: utf-8 -*-
"""縦長の写真（高嶋ちさ子）の右に本文を回り込ませる。

ユーザー指示（2026-08-20）＝「高島千佐子の写真の脇から記事かけない？空白無くして」
＝縦長ポートレートの右側が空いていて、もったいない。

実装:
  ・.pk-portrait を float:left にして本文を回り込ませる
  ・pk-detail に clearfix を入れて、次のブロックに食い込ませない
  ・狭い画面（〜359px）では float を解除して従来どおり縦積み
  ・クレジットは幅が狭くなるぶん少し小さくする（消さない＝ライセンスの条件）
"""
import io, sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

SRC = 'index.html'
raw = open(SRC, 'rb').read()
before = raw.count(b'\r\n')
assert raw.count(b'\n') - before == 0
h = raw.decode('utf-8')
NL = '\r\n'

OLD = '    .pickup .pk-portrait img { max-width: 190px; }' + NL
NEW = (
    '    .pickup .pk-portrait { float: left; width: 148px; margin: 2px 15px 4px 0; }' + NL +
    '    .pickup .pk-portrait img { width: 100%; }' + NL +
    '    .pickup .pk-portrait figcaption { font-size: 9.5px; line-height: 1.55; }' + NL +
    '    .pickup .pk-detail::after { content: ""; display: block; clear: both; }' + NL +
    '    @media (max-width: 359px) {' + NL +
    '      .pickup .pk-portrait { float: none; width: 168px; margin-right: 0; }' + NL +
    '    }' + NL
)
assert h.count(OLD) == 1, 'pk-portrait の CSS が見つからない'
h = h.replace(OLD, NEW)

out = h.encode('utf-8')
lf = out.count(b'\n') - out.count(b'\r\n')
assert lf == 0
open(SRC, 'wb').write(out)
print('回り込みを設定 / CRLF %d → %d（LF-only %d）' % (before, out.count(b'\r\n'), lf))
