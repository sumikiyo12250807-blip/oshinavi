# -*- coding: utf-8 -*-
"""記事(8/31〜9/6号)のファクトチェックで出た誤りを直す。
エージェントの独立チェック（出典URLを1本ずつ開いて照合）で見つかった分。"""
import io, sys
sys.stdout.reconfigure(encoding='utf-8')

FIX = [
    # 🚨誤り1＝THE MODS の一般発売は6公演ではなく7公演（大阪11/28が抜けていた）
    ("<p>9/5(土)10:00に一般発売になるのは6公演。<br>10/3(土)の静岡・Live House 浜松 窓枠で始まって、千秋楽は12/12(土)の東京・Shibuya LOVEZ。<br>6公演のうち5つが土曜日だから、遠くの街でも予定は立てやすいはずよ。",
     "<p>9/5(土)10:00に一般発売になるのは7公演。<br>10/3(土)の静岡・Live House 浜松 窓枠で始まって、千秋楽は12/12(土)の東京・Shibuya LOVEZ。<br>7公演のうち6つが土曜日だから、遠くの街でも予定は立てやすいはずよ。"),
    # 🚨誤り2＝夜の本気ダンス〈OKIBARI〉は7公演ではなく9公演（大阪11/1・兵庫2/23が抜けていた）
    ("9/5(土)10:00に一般発売になるのは、その〈OKIBARI〉の7公演。",
     "9/5(土)10:00に一般発売になるのは、その〈OKIBARI〉の9公演。"),
    # 🚨誤り3＝ベスト盤のDisc4は「ライブ映像10曲＋ボーナスMV2曲」（12曲ではない）
    ("残る1枚は1999年『JUNK YARD TOUR '99』のライブ映像12曲。",
     "残る1枚は1999年『JUNK YARD TOUR '99』のライブ映像10曲に、ボーナスのミュージックビデオ2曲。"),
    # ⚠️8＝アカペラ音頭の声優は9名（6名しか書いていなかった）
    ("<p>豊永利行、小野大輔、山寺宏一、佐藤拓也、古川慎、斉藤壮馬——この並びが一緒に音頭を録ってるの。",
     "<p>豊永利行、小野大輔、山寺宏一、佐藤拓也、古川慎、斉藤壮馬に、熊谷海麗、ふじたまみ、岡村明香——この9人が一緒に音頭を録ってるの。"),
    # ⚠️6＝「生涯愛読」は出典に無い断定
    ("歌詞は、ベートーヴェンが生涯愛読していた詩人シラーの詩『歓喜に寄す』。",
     "歌詞は、ベートーヴェンが若い頃から深く傾倒していた詩人シラーの詩『歓喜に寄す』。"),
    # ⚠️7＝9/1の先行が3公演共通に読める（実際は12/22チャリティーの枠）
    ("<p>気をつけたいのは9/1(火)10:00の先行ね。<br>これはぴあクラシックの「poco a poco」への入会（無料）が必要な、会員限定の先行なの。",
     "<p>気をつけたいのは、12/22のチャリティーコンサートに付いている9/1(火)10:00の先行ね。<br>これはぴあクラシックの「poco a poco」への入会（無料）が必要な、会員限定の先行なの。"),
    # ⚠️9＝条件つき枠（プリセール／会員先行）を一般発売と並べない
    ('<span class="pk-o-name">さだまさし</span><span class="pk-o-when">8/31(月)</span>',
     '<span class="pk-o-name">さだまさし</span><span class="pk-o-when">8/31(月) プリセール</span>'),
    ('<span class="pk-o-name">新日本フィルハーモニー交響楽団</span><span class="pk-o-when">9/1(火)〜</span>',
     '<span class="pk-o-name">新日本フィルハーモニー交響楽団</span><span class="pk-o-when">9/1(火) 会員先行／9/5(土) 一般</span>'),
    ('<span class="pk-o-name">大名古屋らくご祭2026</span><span class="pk-o-when">9/4(金)</span>',
     '<span class="pk-o-name">大名古屋らくご祭2026</span><span class="pk-o-when">9/4(金) プリセール</span>'),
    ("<p class=\"pk-others-note\">この2組のほかにも、今週はこの名前たちの発売が始まるのよ。</p>",
     "<p class=\"pk-others-note\">この2組のほかにも、今週はこの名前たちの受付が動くのよ。<br>「プリセール」「会員先行」と書いてあるものは条件つきの枠だから、そこだけ気をつけて。</p>"),
]

for path in ('tmp/pickup0830/section.html',):
    t = io.open(path, encoding='utf-8', newline='').read()
    nl = '\r\n' if '\r\n' in t else '\n'
    s = t.replace('\r\n', '\n')
    miss = []
    for old, new in FIX:
        if old not in s:
            miss.append(old[:44]); continue
        s = s.replace(old, new, 1)
    if nl == '\r\n':
        s = s.replace('\n', '\r\n')
    io.open(path, 'w', encoding='utf-8', newline='').write(s)
    print('%s 直した %d / 見つからず %d' % (path, len(FIX) - len(miss), len(miss)))
    for m in miss:
        print('   ⚠️見つからない:', m)
