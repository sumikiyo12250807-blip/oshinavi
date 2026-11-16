# -*- coding: utf-8 -*-
# 禁句・「。」のあと改行・経歴語・引用の一致・字数を機械で見る
import io, re
D = 'C:/Users/user/oshinavi/tmp/x1116/art16/'
NG = r'未就学|歳未満|歳以上有料|手数料|身分証|本人確認|電子チケット|スマチケ|発券|学生証|お支払|クレカ|会員登録|ぶん|の分|手帳|あんた|アンタ'
BIO = r'結成|脱退|退団|入団|デビュー|人組|加入|在籍|活動休止|解散'
SRC = {
 'takahashiyu': ['takahashiyu_official.txt', 'takahashiyu_special.txt', 'takahashiyu_pia.txt', 'takahashiyu_more_minnanouta.txt', 'takahashiyu_more_tori.txt', 'takahashiyu_more_news2.txt', 'takahashiyu_more_fss1.txt'],
 'sumidabasho': ['sumidabasho_official.txt', 'sumidabasho_official.html', 'sumidabasho_pia.txt', 'sumidabasho_more_timetable.txt', 'sumidabasho_more_jungyo.txt'],
 'freedomofchoice': ['freedomofchoice_cube.txt', 'freedomofchoice_hakataza.txt', 'freedomofchoice_toho.txt', 'freedomofchoice_cubetheater.txt', 'freedomofchoice_astage.txt'],
}
out = io.open(D + 'check.txt', 'w', encoding='utf-8')
for slug, srcs in SRC.items():
    L = io.open(D + slug + '.md', encoding='utf-8').read().splitlines()
    body = [x for x in L[5:] if x.strip()]
    src = ''.join(re.sub(r'\s+', '', io.open(D + s, encoding='utf-8').read()) for s in srcs)
    v1 = [x for x in io.open(D + slug + '_v1.md', encoding='utf-8').read().splitlines()[5:] if x.strip()]
    out.write('== %s 本文 %d字 %d行（前 %d字）\n' % (slug, sum(len(x) for x in body), len(body), sum(len(x) for x in v1)))
    for i, x in enumerate(L):
        for m in re.finditer(NG, x):
            out.write('  NG %d: %s\n' % (i + 1, m.group()))
        for m in re.finditer(BIO, x):
            out.write('  BIO %d: %s\n' % (i + 1, m.group()))
    for x in body:
        n = x.count('。')
        if not (n == 1 and x.endswith('。')) and not (n == 0 and x.endswith('✨')):
            out.write('  KUTEN: %s\n' % x)
        for q in re.findall(r'「([^」]{12,})」', x):
            out.write('  QUOTE %s: %s\n' % ('OK' if re.sub(r'\s+', '', q) in src else 'NOT FOUND', q))
