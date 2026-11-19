import os, sys
SP = r'C:\Users\user\AppData\Local\Temp\claude\ac08c5b2b244d5f8\6d0ac969-eb80-4bf7-86e5-551288d024a5\scratchpad\pages2'
out = []
for fn in sys.argv[1].split(','):
    L = open(os.path.join(SP, fn + '.txt'), encoding='utf-8').read().splitlines()
    try:
        a = L.index('チケット情報')
    except ValueError:
        a = 0
    b = len(L)
    for i, l in enumerate(L):
        if l.startswith('アイコン説明'):
            b = i
            break
    seg = L[a:b]
    # drop the duplicated favorites-dialog lines
    seg = [l for l in seg if l not in ('通信中…', '通信エラーにより登録に失敗しました', '登録に失敗しました', '登録完了しました', '既に登録されています', '登録件数オーバーにより登録に失敗しました', '登録に失敗しました。', 'エラーコード：', 'ログイン後に登録動作をおこなってください', 'ログイン', '新規登録', '(', ')', 'メールで通知', 'リセールチケット購入へ')]
    out.append('##### ' + fn + ' ' + L[0][:80])
    out += seg
open(os.path.join(SP, 'trim_' + sys.argv[2] + '.txt'), 'w', encoding='utf-8').write('\n'.join(out))
