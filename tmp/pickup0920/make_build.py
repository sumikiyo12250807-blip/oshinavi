# 先週の組み立て（tmp/pickup0913/build_section.py）を 9/20号用に書き換えて tmp/pickup0920/build_section.py を作る
import io, re
s = io.open('tmp/pickup0913/build_section.py', encoding='utf-8', newline='').read().replace('\r\n', '\n')
rep = [
    ('"tmp/pickup0913/draft.md"', '"tmp/pickup0920/draft.md"'),
    ('"tmp/pickup0913/section.html"', '"tmp/pickup0920/section.html"'),
    ('"2026-09-14", "2026-09-20"', '"2026-09-21", "2026-09-27"'),
    ('9/14(月)〜9/20(日)にチケットの発売が始まるアーティスト紹介', '9/21(月・祝)〜9/27(日)にチケットの発売が始まるアーティスト紹介'),
    ('secs["今週の深掘り"]', 'secs["深掘り"]'),
    ('      FIG_SUNTORY,\n', ''),
]
for a, b in rep:
    assert a in s, a
    s = s.replace(a, b)
n0 = s
s = re.sub(r'MAIN = \[.*?\]\)\]\n', 'MAIN = [("『アイカツスターズ！』10周年記念イベント「おめでたいたい！ありが10☆」", [7088]),\n'
           '        ("角野隼斗×アラン・ギルバート指揮 NDRエルプフィルハーモニー管弦楽団", [6988]),\n'
           '        ("矢野顕子", [4103]),\n'
           '        ("反田恭平＆ザルツブルク・モーツァルテウム管弦楽団 日本ツアー2027", [3406]),\n'
           '        ("斉藤和義", [876])]\n', s, count=1, flags=re.S)
assert s != n0, 'MAIN'
s = re.sub(r'DEEP_IDS = \[.*?\n', 'DEEP_IDS = [2500]   # 深掘り＝ドラクエ ウインドオーケストラ\n', s)
s = re.sub(r'SHORT = \{.*?\}\n', 'SHORT = {2500: "12/30・1/1 年末年始特別公演（東京国際フォーラム ホールC）"}\n', s, flags=re.S)
s = re.sub(r'TILE_NAMES = \[.*?\]\n', '', s, flags=re.S)
s = re.sub(r'TILE_IDS = \[.*?\n', 'TILE_IDS = [4367, 2496, 5524, 1334, 685, 5332, 5526, 867, 801, 727, 3053, 5569]\n', s)
s = re.sub(r'bttf = \[.*?\nTILE_IDS\[-1\] = bttf\[0\]\["id"\]\n', '', s, flags=re.S)
# 名前タイルの段落（「ほかにも、」）は主役の本文から外す＝画面ではタイルで出す
a = '    B.append(br(paras_of(body)))'
assert a in s
s = s.replace(a, '    B.append(br([p for p in paras_of(body) if not p.startswith("ほかにも、")]))')
# 券種名「一般発売（WEB受付）（神奈川 R9年 3/15公演）」の括弧が2つで、箱の表示が「WEB受付）（神奈川」と崩れる＝表示だけ直す
a = '        lst = lst.replace("12/30〜R9年 1/5 大阪", "12/30・R9年 1/1〜1/5 大阪")'
assert a in s
s = s.replace(a, a + '\n        lst = lst.replace("WEB受付）（神奈川", "神奈川")')
# 🆕9/19＝導入の直後のリード段（## 年末年始の予定は…）を、9/6号と同じく「つづきを読む」直後に pk-lede で出す
a = """      '      <h3 class="pk-h2">今週の主役</h3>']"""
assert a in s, 'h3'
s = s.replace(a, """      ]
# 9/19 ユーザー「これが導入文だよ　変えなくていい　その後各アーティストの記事を書くの」
#   ＝「つづきを読む」を開いた先の導入文。見出しごとそのまま出して、すぐ主役の記事へ
# 9/19 さらに ユーザー＝この段は見出しのすぐ下（「秋の連休は〜」があった場所）へ移した＝ボタンの先には出さない
B.append('      <h3 class="pk-h2">今週の主役</h3>')""")
# 9/19 ユーザー「一番上の名前とイベントを並べただけのはいらない」「書き直さなくていい　いらない」＝見出し(pk-title)を出さない
a = """     '  <h2 class="pk-title">%s</h2>' % esc(title),\n"""
assert a in s, 'pk-title'
# 9/19 続けて ユーザー「見出しは　年末年始の予定は、涼しくなったいまのうちに」＝draft.md 1行目をその言葉にして見出しに出す
io.open('tmp/pickup0920/build_section.py', 'w', encoding='utf-8').write(s)
print('ok')
