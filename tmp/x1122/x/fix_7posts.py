# -*- coding: utf-8 -*-
# すちこ「主役は1本でいい」＝主役は shu01 好井まさおだけ・shu02 布袋・shu03 いれいすは外す（post_unused/ へ）→ 締めと予告を合わせる
import io, os, shutil
X = 'C:/Users/user/oshinavi/tmp/x1122/x/'
os.makedirs(X + 'post_unused', exist_ok=True)
for k in ('shu02', 'shu03'):
    if os.path.exists(X + 'post/' + k + '.txt'):
        shutil.move(X + 'post/' + k + '.txt', X + 'post_unused/' + k + '.txt')
FIX = {
 'mat06': [('このあとの投稿では、明日発売の主役を1組ずつ紹介するから', 'このあとの投稿では、明日発売の主役を紹介するから')],
 'shu01': [('このあとの投稿でも、明日発売の主役を紹介するから、あたしのXをフォローして待っていて。', '明日の夜も、あさって発売のチケットをジャンルごとに並べるから、あたしのXをフォローして待っていて。')],
}
for k, rs in FIX.items():
    s = io.open(X + 'post/' + k + '.txt', encoding='utf-8', newline='').read()
    for a, b in rs:
        assert s.count(a) == 1, (k, a)
        s = s.replace(a, b)
    io.open(X + 'post/' + k + '.txt', 'w', encoding='utf-8', newline='').write(s)
n = io.open(X + 'page_notes_1123.txt', encoding='utf-8').read()
n = n.replace('今夜は9本（', '今夜は7本＝すちこ「主役は1本でいい」（').replace('主役＝①好井まさおの怪談を浴びる会（FANY 一般 10:00・赤坂RED/THEATER 12/26〜12/29）②布袋寅泰（福岡 11/23 公演の当日料金 0:00 発売）③いれいす 全国上映会（e+ 先着一般 12:00・札幌）', '主役＝好井まさおの怪談を浴びる会（FANY 一般 10:00・赤坂RED/THEATER 12/26〜12/29）だけ・布袋寅泰といれいすはまとめの行に残した')
n += '独立FC 🔴2🟠2 → 直した：①広島ドラゴンフライズは6試合（琉球戦2試合）②神田伯山の行の切れ端「15から上がります」を外した ③スワローズ楽燕祭に（抽選）④南佳孝の同じ公演2行を1行に／予告の名前を外した（X_SCRIPT 9）\n'
io.open(X + 'page_notes_1123.txt', 'w', encoding='utf-8').write(n)
print('ok')
