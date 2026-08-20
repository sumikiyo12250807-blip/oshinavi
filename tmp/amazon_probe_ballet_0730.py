# -*- coding: utf-8 -*-
"""バレエ演目のAmazon検索語を実測する（audit本体が drop と出した3496/3497の裏取り）。
クラシック/バレエは「演目(曲名)」で探すのが正＝神奈川フィルの第九で確立した方針
（[[reference_amazon_affiliate]]）。audit の短縮ロジックは「公演名がほぼ演目そのもの」の型に弱い。
"""
import sys

sys.path.insert(0, 'tools')
from amazon_audit import probe2

CAND = [
    ('白鳥の湖', False),
    ('白鳥の湖', True),
    ('瀕死の白鳥', False),
    ('光と影のプルミエール', False),
]
for kw, cd in CAND:
    n, err = probe2(kw, cd)
    print('%-14s CD=%-5s -> hit %s %s' % (kw, cd, n, err))
