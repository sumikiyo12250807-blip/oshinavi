# -*- coding: utf-8 -*-
"""ボタンの文字を短くする（2026-09-14 夜 ユーザー「ボタンにそんな長い文章きついでしょ　もう少し短めで買いたくなる文字」→「案①でいいわ」）。
押すと出るもの（飛び先）は変えない＝文字だけ。飛び先に合う言葉だけにした（feedback_button_label_matches_result）。
画像ボタン（BTN_IMG）は文字で画像を引くので、明日ユーザーがこの文字で9枚作り直す。今までの2枚（btn_hotel/btn_uchiwa）は旧文言。
使い方: python tmp/relabel_buttons_0914.py [--apply]
"""
import io
import sys

sys.stdout.reconfigure(encoding='utf-8')
REPL = [  # (旧, 新, 出てくる回数)
    ('"会場近くのホテルを探す"', '"遠征の宿を探す"', 2),
    ('label: "応援うちわを作る"', 'label: "推しうちわを作る"', 1),
    ('label: "応援グッズをそろえる"', 'label: "推し活グッズ"', 1),
    ('label: "耳栓を用意する"', 'label: "ライブ用耳栓"', 1),
    ('label: "オペラグラスを用意する"', 'label: "オペラグラス"', 1),
    ('label: "フェスの持ち物をそろえる"', 'label: "フェスの必需品"', 1),
    ('label: "花火の持ち物をそろえる"', 'label: "花火の必需品"', 1),
    ('label: "観戦グッズをそろえる"', 'label: "観戦グッズ"', 2),
    ('label: "ぬりえを見る"', 'label: "ぬりえ"', 1),
]
OLD_NOTE = ('    //   そろったら下の2行を戻し、残り7枚を1行ずつ足す（img/btn_hotel.png・img/btn_uchiwa.png は置いたまま）。\r\n'
            '    //   "会場近くのホテルを探す": "img/btn_hotel.png",\r\n'
            '    //   "応援うちわを作る": "img/btn_uchiwa.png",\r\n')
NEW_NOTE = ('    //   🆕2026-09-14 夜 ユーザー決定＝ボタンの文字を短くした（案①）。画像は新しい文字で9枚作り直す＝そろったら9行足す。\r\n'
            '    //   遠征の宿を探す／推しうちわを作る／推し活グッズ／ライブ用耳栓／オペラグラス／フェスの必需品／花火の必需品／観戦グッズ／ぬりえ\r\n'
            '    //   （img/btn_hotel.png・img/btn_uchiwa.png は旧文言「会場近くのホテルを探す」「応援うちわを作る」の画像＝使わない）\r\n')
src = io.open('index.html', encoding='utf-8', newline='').read()
assert src.count(OLD_NOTE) == 1, '画像のメモの場所が見つからない'
src = src.replace(OLD_NOTE, NEW_NOTE)
for old, new, n in REPL:
    c = src.count(old)
    assert c == n, '%s が %d回（想定 %d回）' % (old, c, n)
    src = src.replace(old, new)
    print('✅ %s → %s（%d か所）' % (old, new, n))
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
io.open('index.html', 'w', encoding='utf-8', newline='').write(src)
print('書き込み完了')
