# -*- coding: utf-8 -*-
"""バッジ0の14件について、ぴあを**アーティスト名で**掃き直して未登録のeventCdを探す。

登録してあるURLだけ見ても 0枠 なので、[[feedback_pia_bundle_hides_shows]] の型
（＝ぴあが別のeventCdに生きた枠を持っている）を疑う。
2026-08-21 の調査で 4175 THE PREDATORS が実際にこの型だった（登録2626509は0枠だが
2632152 に受付中の枠があった）。
"""
import io, sys, time, subprocess
sys.stdout.reconfigure(encoding='utf-8')

TARGETS = [
    (1601, '藍井エイル'), (3473, 'AA='), (4050, 'Bray me'),
    (4080, '澤野弘之'), (4098, '高木いくの'), (4100, 'Khalid'),
    (4106, '徹子の部屋'), (4114, 'Yung Kai'), (4115, 'THE MACKSHOW'),
    (4159, 'わーすた'), (4165, 'ETERNAL FIGHTER'), (4167, 'Ken Yokoyama'),
    (4175, 'THE PREDATORS'), (4424, 'シャッポ'),
]
out = []
for i, (eid, kw) in enumerate(TARGETS, 1):
    try:
        subprocess.run([sys.executable, 'tools/pia_kw_search.py', kw],
                       capture_output=True, timeout=180)
        txt = io.open('tmp/pia_kw_search.txt', encoding='utf-8').read()
    except Exception as ex:
        txt = '(検索できず: %s)' % ex
    out.append('\n########## id=%d  検索語=%s ##########\n%s' % (eid, kw, txt))
    print('[%d/%d] %s' % (i, len(TARGETS), kw))
    time.sleep(4)          # 429対策（キーワード間に間隔を空ける）
io.open('tmp/kw14_result.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('wrote tmp/kw14_result.txt')
