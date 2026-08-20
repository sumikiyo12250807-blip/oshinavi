# -*- coding: utf-8 -*-
"""X投稿5本の機械検品（2026-08-20発売分）。
 ①字数（250〜330）②「。」の直後に文字が続いていないか ③冒頭ピックアップ・CTA・署名・タグ
 ④本文に出てくる「M/D(曜)」を実カレンダーと照合 ⑤5本で重複する特徴語
"""
import re, sys, glob, datetime, collections
sys.stdout.reconfigure(encoding='utf-8')

WD = '月火水木金土日'
CTA = '▼チケット情報はこちら'
SIGN = '推しの"発売日"見逃さない｜OSHINAVI'
URL = 'https://oshinavi.jp'

files = sorted(glob.glob('tmp/post0820_*.txt'))
bodies = []
for p in files:
    t = open(p, encoding='utf-8').read().strip('\n')
    bodies.append((p, t))

for p, t in bodies:
    n = len(t)
    print('=== %s  全体%d字' % (p, n))
    # ③ 3点チェック
    for label, cond in (('冒頭ピックアップ', t.startswith('OSHINAVIの"8/20発売"ピックアップ🎫')),
                        ('CTA', CTA in t), ('URL', URL in t), ('署名', SIGN in t),
                        ('タグ', bool(re.search(r'^#\S', t.split('\n')[-1])))):
        print('   %s %s' % ('OK ' if cond else '🚨NG', label))
    # ② 句点の直後
    bad = [m.start() for m in re.finditer(r'。(?=[^\s])', t)]
    print('   %s 句点の直後に文字（%d件）' % ('OK ' if not bad else '🚨NG', len(bad)))
    for b in bad:
        print('        …%s' % t[max(0, b - 12):b + 12].replace('\n', '⏎'))
    # ④ 曜日照合
    for m in re.finditer(r'(\d{1,2})月(\d{1,2})日\((.)\)|(\d{1,2})/(\d{1,2})\((.)\)', t):
        if m.group(1):
            mm, dd, w = int(m.group(1)), int(m.group(2)), m.group(3)
        else:
            mm, dd, w = int(m.group(4)), int(m.group(5)), m.group(6)
        # 年は文脈から：1月・2月は2027年、それ以外は2026年
        y = 2027 if mm <= 3 else 2026
        if '2027年' in t[max(0, m.start() - 8):m.start()]:
            y = 2027
        real = WD[datetime.date(y, mm, dd).weekday()]
        ok = (real == w)
        print('   %s %d/%d(%s) 実際=%s%s' % ('OK ' if ok else '🚨NG', mm, dd, w, real, '' if ok else '  ←直すこと'))

# ⑤ 5本で重複する特徴語
print('\n=== 5本で2回以上出る特徴語（手癖チェック）===')
words = collections.Counter()
for _, t in bodies:
    seen = set()
    for w in re.findall(r'[ぁ-んァ-ヶ一-龠]{2,6}(?=わ|の|よ|て|に|で|を|は|、|。)', t):
        if w in seen:
            continue
        seen.add(w)
        words[w] += 1
for w, c in words.most_common(12):
    if c >= 3:
        print('   %s ×%d本' % (w, c))
