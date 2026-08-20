# -*- coding: utf-8 -*-
"""任意のクエリでAmazonの当たり具合を実測する（amazon_audit の probe2 を再利用）。
🚨 amazon_audit の自動短縮は「デビュー35周年記念 横山幸雄ピアノ・リサイタル」を
「デビュー35」に切ってしまう（イベント語が名前より前に来る形に弱い）。
11件当たっても中身は別人のCD＝**機械の提案を鵜呑みにしない**ための実測。"""
import sys
import time

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import amazon_audit as A

CASES = [
    ('横山幸雄', True),
    ('横山幸雄', False),
    ('デビュー35', True),
    ('九州交響楽団', False),
]

out = []
for kw, cd in CASES:
    n, titles = A.probe2(kw, cd)
    out.append(f'k=「{kw}」 CD語={"付き" if cd else "なし"} → 検索語を含む商品 {n}件')
    for t in (titles or [])[:5]:
        out.append(f'      {t[:96]}')
    time.sleep(A.WAIT)

open('tmp/amz_probe_0730.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('wrote tmp/amz_probe_0730.txt')
