# -*- coding: utf-8 -*-
"""8/23発売の全52件を、ジャンル別の「全部のせ」投稿に組む（2026-08-22 ユーザー指示）。

ユーザー明示「５本目は、明日発売のチケットを全部のせる　長くなる時は分けて投稿して」。
＝[[project_sns_promotion]]の「全件列挙は読まれない」より**ユーザーの指示が優先**。
長さは1本あたり本文550字を上限に、ジャンルの切れ目で割る。

表記を縮める時も**勝手な言い換えはしない**（[[feedback_no_fake_info]]）。
公式名が長いものだけ、識別できる範囲で前半を残して「…」を付けずに切る。
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

T = '2026-08-23'
h = open('index.html', encoding='utf-8').read()
E = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))

# 一覧で長すぎる公式名だけ、識別できる範囲に縮めた表記（勝手な創作はしない）
SHORT = {
    '新宿文化センター×東京フィルハーモニー交響楽団 小林研一郎 新宿区名誉区民顕彰記念コンサート ベートーヴェン「交響曲第九番」':
        '東京フィル×小林研一郎「第九」',
    'サンケイホールブリーゼ米朝一門落語会シリーズ2026 噺家生活55周年記念「桂雀三郎独演会」': '桂雀三郎独演会',
    '劇団四季ファミリーミュージカル「はじまりの樹の神話～こそあどの森の物語～」／福岡': '劇団四季『はじまりの樹の神話』',
    '劇団四季ミュージカル『コーラスライン』／全国ツアー': '劇団四季『コーラスライン』',
    'NES-FES. ～ EXILE THE SECOND Special ～': 'EXILE THE SECOND『NES-FES.』',
    'TOMOVSKY トモフ出航60周年記念ツアー 『3度目のハタチ』“大阪編”': 'TOMOVSKY『3度目のハタチ』',
    'KBS京都75周年記念「京都フォーク・デイズ ライブ～うたとことば つなぐ～」': '京都フォーク・デイズ',
    '神奈川フィルハーモニー管弦楽団 みなとみらいシリーズ定期演奏会第419回': '神奈川フィル みなとみらい定期419回',
    'フォトエッセイ発売記念の集い たびびとすぴ ～探し物のつづき～': 'たびびとすぴ 発売記念の集い',
    'ヨーロッパ企画特別興行「世界の終わりかけとスリーコード」': 'ヨーロッパ企画「世界の終わりかけとスリーコード」',
    'ミュージカル『星影の人』-沖田総司・まぼろしの青春-': 'ミュージカル『星影の人』',
    '第六回『五節句の会』 ～星まつりから住吉の神へ～': '第六回『五節句の会』',
    '隅田川馬石 11月のコツコツ的毎月連続落語会『子別れ 中・下』他': '隅田川馬石 11月連続落語会',
    '隅田川馬石 12月のコツコツ的毎月連続落語会 『淀五郎』他': '隅田川馬石 12月連続落語会',
    '第6回 宝井琴鶴・田辺いちか二人会 テーマ「愛」、トーク付き': '宝井琴鶴・田辺いちか 二人会',
    '吉原あさひ・鈴々舎美馬 二人会 お楽しみトーク付き': '吉原あさひ・鈴々舎美馬 二人会',
    'THE SECOND ライブツアー2026～今、全盛期の漫才師達～': 'THE SECOND ライブツアー2026',
    'こまつ座第160回公演 『頭痛肩こり樋口一葉』': 'こまつ座『頭痛肩こり樋口一葉』',
    'タクフェス第14弾 『北の島から』小樽公演': 'タクフェス『北の島から』小樽',
    'タクフェス第14弾『北の島から』': 'タクフェス『北の島から』',
    'M&Oplaysプロデュース『ブランク』': 'M&Oplays『ブランク』',
    '箏合奏新曲リサイタル 大川義秋 作品集VOL.1': '大川義秋 箏合奏新曲リサイタル',
    '大分交響楽団第49回定期演奏会': '大分交響楽団 第49回定期',
    'ミュージカル『新テニスの王子様』The Final Stage': '新テニミュ The Final Stage',
    '劇団四季『アラジン』東京公演': '劇団四季『アラジン』東京',
    '加藤登紀子 Songs for Love 2026': '加藤登紀子',
    'U-21 浦和対U-21 東京V U-21 Jリーグ': 'U-21 浦和 対 U-21 東京V',
    '新国立劇場オペラ「フィガロの結婚」': '新国立劇場オペラ「フィガロの結婚」',
}

rows = []
for e in E:
    hit = [t for t in (e.get('tickets') or [])
           if not t.get('soldout') and not t.get('saleEnded')
           and t.get('startDate') == T
           and re.search(r'\d{1,2}/\d{1,2}\s*\d{1,2}:\d{2}発売', t.get('type') or '')]
    if not hit:
        continue
    name = SHORT.get(e['name'], e['name'])
    name = re.sub(r'\s*20\d\d$', '', name)          # 末尾の年は落とす（画面の見やすさ）
    d = e['date']
    md = '%d/%d' % (int(d[5:7]), int(d[8:10]))
    if d[:4] == '2027':
        md = 'R9年' + md
    rows.append({'genre': e.get('genre'), 'name': name, 'pref': e.get('prefecture'), 'md': md})

# 同じ団体の連番公演は1行にまとめる（札響の定期が4件で4行を食うため）。事実は変えない。
sap = [r for r in rows if r['name'].startswith('札幌交響楽団 第')]
if len(sap) > 1:
    nums = sorted(int(re.search(r'第(\d+)回', r['name']).group(1)) for r in sap)
    mds = [r['md'] for r in sorted(sap, key=lambda r: int(re.search(r'第(\d+)回', r['name']).group(1)))]
    rows = [r for r in rows if r not in sap]
    rows.append({'genre': 'classic', 'pref': sap[0]['pref'],
                 'name': '札幌交響楽団 第%d〜%d回定期演奏会' % (nums[0], nums[-1]),
                 'md': '%s〜%s' % (mds[0], mds[-1])})

GROUPS = [
    ('音楽', ['jpop', 'rock'], '🎤'),
    ('クラシック', ['classic', 'dento'], '🎻'),
    ('落語・お笑い', ['owarai'], '🎙'),
    ('演劇', ['engeki'], '🎭'),
    ('ミュージカル・ほか', ['musical', 'sports'], '✨'),
]

HEAD = 'OSHINAVIの"8/23発売"ピックアップ🎫'
CTA = '▼チケット情報はこちら → https://oshinavi.jp'
SIGN = '推しの"発売日"見逃さない｜OSHINAVI'
TAGS = '#チケット発売 #8月23日発売'

out = io.open('tmp/x0823/list_posts.txt', 'w', encoding='utf-8')
n = len(GROUPS)
total = 0
for i, (label, gs, emoji) in enumerate(GROUPS, 1):
    items = [r for r in rows if r['genre'] in gs]
    total += len(items)
    lines = ['・%s（%s %s）' % (r['name'], r['pref'], r['md']) for r in
             sorted(items, key=lambda r: r['name'])]
    body = '\n'.join([
        HEAD,
        '明日8/23(日)発売のチケット、ぜんぶ出すわ。',
        '%s %s（%d/%d）%d件よ。' % (emoji, label, i, n, len(items)),
        '※かっこ内はエリアと最終公演日。',
        '',
        *lines,
        '',
        CTA,
        '',
        SIGN,
        TAGS,
    ])
    out.write('=== (%d/%d) %s : %d件 / %d字 ===\n%s\n\n' % (i, n, label, len(items), len(body), body))
out.write('合計 %d件\n' % total)
out.close()
print('合計 %d件 → tmp/x0823/list_posts.txt' % total)
