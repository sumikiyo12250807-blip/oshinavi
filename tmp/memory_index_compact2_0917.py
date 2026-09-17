import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
P = r'C:\Users\user\.claude\projects\C--Users-user-oshinavi\memory\MEMORY.md'
lines = open(P, encoding='utf-8').read().split('\n')
NEW = {
10: '- 🚨 [昼のヒールとpushをすっぽかした＝真因は「時計を叩かない」](feedback_noon_heal_missed_twice.md) — 🚨🚨**予定を立てたら同じターンでその日の時刻を全部アラーム（CronCreate）に入れる**（昼・午後の発売・17時X準備・19:40予約締め・夜push）',
13: '- 🚨 [記事に経歴を書かない＝ツアーの中身と会場に差し替える](feedback_article_no_biography.md)／🎼[代わりに**曲順（セトリ）を載せてよい**](feedback_setlist_in_article.md)（2件以上で一致した時だけ・ネタバレ注意・出典明記・歌詞ゼロ）',
14: '- 🚨🚨 [記事を書き直したらチェックをやり直す＝前のチェックは前の文章のもの](feedback_article_recheck_after_rewrite.md)（故人を現役として書いた記事を公開した／感想はファクトチェックにかけない）',
73: '- 🎯🚨 [**「大物なのに載っていない」＝ローチケの週スキャン**](project_big_artist_crosscheck.md)（ぴあにも楽天にも無い大物がある／対バン名・フェス名で登録済みのことがある＝eventCd照合まで「未登録」と言わない）',
113: '- 🚨 [ユーザーが自分で決めた文言は言い換え案に混ぜない](feedback_keep_user_words_on_buttons.md)（ホテル＝「会場近くのホテルを探す」（9/16決定）・うちわ＝「推しうちわを作る」）',
125: '- 🎯🚨 [**楽天チケットも鉄壁にする**](project_rakuten_make_it_ironclad.md) — 優先順を決めるのは「後工程（ヒール・売り切れ打ち分け・削除照合・毎朝の再照合）が揃っているか」',
}
before = len('\n'.join(lines))
for n, s in NEW.items():
    key = s.split('](')[1].split(')')[0]
    assert key in lines[n - 1], (n, key)
    lines[n - 1] = s
txt = '\n'.join(lines)
open(P, 'w', encoding='utf-8', newline='').write(txt)
print('文字数', before, '→', len(txt))
