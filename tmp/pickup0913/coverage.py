# -*- coding: utf-8 -*-
"""①取りこぼしチェック（現物→本文）＝主役の各エントリで、窓（9/14〜9/20）に発売が始まる枠を全部並べ、
本文にその「公演日」と「発売日」が両方出てくるかを見る（読むだけ）。
あわせて決まりの機械チェック（経歴語・導入の禁句・「。」のあとの改行）。"""
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
FROM, TO = '2026-09-14', '2026-09-20'
IDS = {'ヨーヨー・マ': [7324], 'サントリーホールの年末年始': [4771, 4772, 4850, 4845], '女王蜂': [4802],
       'GENERATIONS': [3568], 'コーラスライン': [4898]}
d = io.open('tmp/pickup0913/draft.md', encoding='utf-8').read()
src = open('index.html', encoding='utf-8').read()
ev = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))}
miss = 0
for name, ids in IDS.items():
    for i in ids:
        for t in ev[i].get('tickets') or []:
            sd = t.get('startDate') or ''
            if not (FROM <= sd <= TO):
                continue
            mo, dd = int(sd[5:7]), int(sd[8:10])
            rel = '%d/%d' % (mo, dd)
            pm = re.search(r'（([^（）]*?)\s*(?:R\d+年\s*)?(\d{1,2}/\d{1,2})', t['type'])
            perf = pm.group(2) if pm else ''
            ok = (rel in d) and (perf in d)
            if not ok:
                miss += 1
            print('%s %s id%s | %s | 発売%s:%s 公演%s:%s' % ('✅' if ok else '❌', name, i, t['type'][:50], rel, rel in d, perf, perf in d))
bio = re.findall(r'結成|脱退|退団|入団|デビュー|人組|メンバー|加入|在籍|活動休止|解散|受賞|初演', d)
intro = '\n'.join(d.splitlines()[:6])
ban = [w for w in ['並ぶ', '走る', '年をまたぐ', '一斉に', 'まとめて出る', '集中'] if w in intro]
kuten = [ln for ln in d.splitlines() if re.search(r'。(?!$|」)', ln.replace('モーニング娘。', ''))]
print('\n取りこぼし %d ／ 経歴語 %s ／ 導入の禁句 %s ／ 「。」のあと改行なし %d行' % (miss, bio or 'なし', ban or 'なし', len(kuten)))
for k in kuten:
    print('   ', k[:60])
