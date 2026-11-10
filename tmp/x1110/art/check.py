# -*- coding: utf-8 -*-
# 記事3本の機械チェック：曜日・書かない言葉・出典に値があるか
import io, re, datetime, sys
sys.stdout.reconfigure(encoding='utf-8')
D = 'C:/Users/user/oshinavi/tmp/x1110/art/'
S = 'C:/Users/user/AppData/Local/Temp/claude/ac08c5b2b244d5f8/402b246e-9e52-46c7-9b59-f5c4808ec0be/scratchpad/'
W = '月火水木金土日'
BAN = r'未就学|歳未満|歳以上有料|手数料|身分証|本人確認|電子チケット|スマチケ|発券|学生証|お支払|クレカ|会員登録|ぶん|の分|手帳|ドリンク|禁止|撮影'
src = {
 'kyary': [S + 'art/kyary_pia.txt', S + 'art/kyary_news.txt', 'C:/Users/user/oshinavi/tmp/x1110/x/src_kyary.txt'],
 'lions': [S + 'art/lions_pia.txt', 'C:/Users/user/oshinavi/tmp/x1110/x/src_lions.txt'],
 'ozaki': [S + 'art/ozaki_all.txt'],
}
for k in ('kyary', 'lions', 'ozaki'):
    t = io.open(D + k + '.md', encoding='utf-8').read()
    print('==', k)
    for m in re.finditer(r'(R9年 )?(\d{1,2})/(\d{1,2})\((.)', t):
        mo, d, w = int(m.group(2)), int(m.group(3)), m.group(4)
        y = 2027 if (m.group(1) or mo < 11) else 2026
        real = W[datetime.date(y, mo, d).weekday()]
        if real != w:
            print('  曜日ちがい', m.group(0), '→', real)
    for m in re.finditer(BAN, t):
        print('  書かない言葉', m.group(0), t[max(0, m.start()-15):m.end()+10].replace('\n', ' '))
    st = ''.join(io.open(f, encoding='utf-8').read() for f in src[k])
    nums = set(re.findall(r'\d{1,3},\d{3}|\d{1,2}:\d{2}', t))
    st2 = st.replace('\u3000', ' ')
    for n in sorted(nums):
        if n not in st2:
            print('  出典に無い数', n)
print('done')
