# -*- coding: utf-8 -*-
"""index.html の「今週のピックアップ」セクションを作り直す。

ユーザー指示（2026-08-20）:
  ・「続きの先が長いわ　ピックアップだから」＝9組は多い → **主役5組＋名前リスト**に圧縮
  ・「発売になる公演…ここ押したら、OSHINAVIの中のバッチに飛ぶようにできる？」
    → 押すと **その名前で検索した状態**になり、結果まで画面が動く（data-pk-search）
      カードは無限スクロールで後から描画されるので、アンカーより検索のほうが確実。
"""
import io, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def act(name, sale, lead, shows, tail, search, top=False, sale_cls='', most=False):
    b = []
    b.append('      <div class="pk-act%s">' % (' pk-top' if top else ''))
    b.append('        <h4 class="pk-name">%s%s</h4>' % (
        name, '<span class="pk-most">今週最多</span>' if most else ''))
    b.append('        <span class="pk-sale%s">%s</span>' % (sale_cls, sale))
    if lead:
        b.append('        <p>%s</p>' % lead)
    b.append('        <a class="pk-shows" href="#" data-pk-search="%s">' % search)
    b.append('          <b>発売になる公演<span class="pk-go">タップで探す →</span></b>')
    b.append('          %s' % shows)
    b.append('        </a>')
    if tail:
        b.append('        <p>%s</p>' % tail)
    b.append('      </div>')
    return '\n'.join(b)

parts = []
parts.append('      <h3 class="pk-h2">今週の主役</h3>')

parts.append(act(
    'EXILE', '8/29(土) 10:00 一般発売',
    '結成25周年の「EXILE 25th ANNIVERSARY BEST LIVE ～LDH PERFECT YEAR 2026～」よ。',
    '埼玉・ベルーナドーム　11/14(土)・11/15(日) の2公演',
    'オリジナルメンバーのMATSU、ÜSA、MAKIDAIまで揃う顔ぶれ。<br>同じツアーで12/5・12/6には大阪・京セラドーム大阪の公演もあるのよ。',
    'EXILE', top=True))

parts.append(act(
    '布袋寅泰', '8/29(土) 10:00 に5公演ぶん一斉',
    '活動45周年記念『HOTEI the LIVE 2026 "45th Celebration GIGS" STAY WILD TOUR』。<br>全国21都市27公演の大きなツアーよ。',
    '宮城 9/22・9/23 ／ 埼玉 10/16・10/17 ／ 東京 11/14',
    'OSHINAVIには全16会場ぶんが載っていて、千秋楽は12/6。',
    '布袋寅泰', top=True))

parts.append(act(
    '真心ブラザーズ', '8/29(土) 10:00 に8公演ぶん一気に',
    '今週いちばん多いのがここ。',
    '埼玉 11/23 ／ 岡山 12/5 ／ 香川 12/6 ／ 静岡 12/25 ／<br>愛知 2027/1/16 ／ 岩手 2027/1/23 ／ 宮城 2027/1/24 ／ 東京 2027/1/30',
    '全国9会場、千秋楽は2027年1月30日の東京・LINE CUBE SHIBUYA。<br>年をまたぐ長い旅だから、近くの会場を見逃さないでね。',
    '真心ブラザーズ', top=True, most=True))

parts.append(act(
    'モーニング娘。&#39;26', '8/29(土) 10:00 に3公演',
    'コンサートツアー秋「超 Heartful 11」（9/5〜11/30）から発売よ。<br>そう、さっきの「老舗人気グループ」はこの子たち。',
    '大阪 9/21 ／ 愛知 9/23 ／ 茨城 9/26',
    '',
    'モーニング娘'))

parts.append(act(
    'シルク・ドゥ・ソレイユ「クーザ」', '8/29(土) 10:00 セブン-イレブン先行',
    'お台場ビッグトップの公演が、7つの期間に分かれて一斉に受付開始よ。',
    '2027年 2/24-2/28 ／ 3/1-3/9 ／ 3/11-3/20 ／ 3/21-3/30 ／<br>4/2-4/10 ／ 4/11-4/20 ／ 4/21-4/25',
    '来年の春の予定を、ここで先に押さえられるわ。',
    'クーザ'))

# ── 名前だけのリスト（押すと検索）
others = [
    ('凛として時雨', '8/29 10:00・3公演'),
    ('徳永英明', '8/29 10:00・3公演'),
    ('7ORDER', '8/29 <b>12:00</b>・2公演'),
    ('プロレスリング・ノア', '<b>8/24(月)</b> 12:00・3公演'),
    ('ORANGE RANGE', '8/29 10:00・2公演'),
    ('加藤ミリヤ', '8/29 10:00'),
    ('岩崎宏美', '8/28 10:00'),
    ('松平健', '8/28 10:00'),
    ('coldrain', '8/29 10:00'),
    ('フラワーカンパニーズ', '8/29 10:00・3公演'),
    ('大原櫻子', '8/29 10:00'),
    ('浜崎貴司', '8/29 10:00・4公演'),
]
parts.append('      <h3 class="pk-h2">今週はほかにも</h3>')
parts.append('      <p class="pk-others-note">名前を押すと、そのアーティストのチケットを探せるわ。</p>')
parts.append('      <div class="pk-others">')
for n, when in others:
    parts.append('        <a href="#" data-pk-search="%s"><span class="pk-o-name">%s</span><span class="pk-o-when">%s</span></a>'
                 % (n.replace('・', '・'), n, when))
parts.append('      </div>')

# ── 深掘り
parts.append('      <h3 class="pk-h2">深掘り：高嶋ちさ子 12人のヴァイオリニスト</h3>')
parts.append(act(
    '結成20周年の記念ツアー', '8/29(土) 10:00 発売',
    '「FJネクスト Presents ～結成20周年記念～ 高嶋ちさ子 12人のヴァイオリニスト コンサートツアー 2026～2027」。<br>'
    '出演は高嶋ちさ子、12人のヴァイオリニスト、近藤亜紀（ピアノ）。<br>'
    '<strong>会場によってゲストが違う</strong>のが面白いところで、山本耕史や城田優が出る回もあるの。',
    '富山・石川・福井・長野　10/29〜11/3公演<br>全席指定 8,000円（税込）',
    'OSHINAVIには全15会場が載っていて、千秋楽は2027年2月21日。<br>先の先まで続くから、今から予定を立てられるのがいいのよね。',
    '高嶋ちさ子'))

parts.append('      <div class="pk-tail">この週は全部で245公演ぶんの発売があるわ。</div>')

io.open('tmp/pickup_section_body.html', 'w', encoding='utf-8').write('\n\n'.join(parts))
print('本文を生成 %d文字 / 主役5組＋ほかに%d組＋深掘り' % (
    sum(len(p) for p in parts), len(others)))
