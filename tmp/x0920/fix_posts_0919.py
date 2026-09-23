# ユーザー指示（9/19夜）で投稿を直す
#  02＝「公演分」「〜の分」を使わない／長い ?q= のリンクを入れない（▼チケット情報はこちら は oshinavi.jp）
#  07・09＝「他にも1件あるわ」→ その1件を時刻の順に書く
import io, sys
sys.stdout.reconfigure(encoding='utf-8')


def fix(p, pairs):
    s = io.open(p, encoding='utf-8').read()
    for a, b in pairs:
        assert s.count(a) == 1, (p, a)
        s = s.replace(a, b)
    io.open(p, 'w', encoding='utf-8').write(s)


fix('tmp/x0920/post02.txt', [
    ('来年4月から9月までの分が明日一般発売よ。', '来年4月から9月までの公演が明日一般発売よ。'),
    ('2027年4月1日から9月30日までの公演分の一般発売が、', '2027年4月1日から9月30日までの公演の一般発売が、'),
    ('oshinavi.jp/?q=%E3%83%90%E3%83%83%E3%82%AF%E3%83%BB%E3%83%88%E3%82%A5%E3%83%BB%E3%82%B6%E3%83%BB%E3%83%95%E3%83%A5%E3%83%BC%E3%83%81%E3%83%A3%E3%83%BC\n',
     'oshinavi.jp\n'),
])
fix('tmp/x0920/post07.txt', [
    ('10:00 天満天神繁昌亭／大阪\n15:00 月例 三三独演／東京（先行）\n他にも1件あるわ。\n',
     '10:00 天満天神繁昌亭／大阪\n11:00 新宿末廣亭10月余一会／東京（先行）\n15:00 月例 三三独演／東京（先行）\n'),
])
fix('tmp/x0920/post09.txt', [
    ('11:00 TJHiroshimaチケット企画／広島 10/25〜（先行）\n他にも1件あるわ。\n',
     '11:00 TJHiroshimaチケット企画／広島 10/25〜（先行）\n12:00 ONE ASIA WORLD メダリストセレブレーション／愛知\n'),
])
print('ok')
