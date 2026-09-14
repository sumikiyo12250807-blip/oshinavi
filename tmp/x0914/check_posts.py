# -*- coding: utf-8 -*-
"""X投稿の機械検品（9/14夜・9/15発売ぶん）。tmp/x0914/post*.txt のうち 9/15 の見出しのものだけを見る
（同じフォルダに 9/13夜の 9/14発売ぶんが残っていることがあるので、見出しで分ける）。
見るもの＝台本 X_SCRIPT.md と memory の封印語・癖（feedback_x_user_edited_samples ほか）。
使い方: python tmp/x0914/check_posts.py
"""
import datetime, glob, io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
WD = '月火水木金土日'
HEAD = 'OSHINAVIの"9/15チケット発売"ピックアップ🎫'
TAGS = '#OSHINAVI #明日発売 #チケット'
BAN = ['生で浴び', 'あんた', '押さえ', '迷うなら両方', 'さっきの投稿', 'ひとつ前']
SOFT = ['ぶん', '動く', '動き', '開く', '開い', '枠が', '受付が', 'が全部', 'こそが', 'というもの', 'しなさい', 'しまいなさい']
files = [f for f in sorted(glob.glob('tmp/x0914/post*.txt'))
         if io.open(f, encoding='utf-8-sig').read().splitlines()[:1] == [HEAD]]
skipped = [f for f in sorted(glob.glob('tmp/x0914/post*.txt')) if f not in files]
bad = 0
phr = {}
for f in files:
    t = io.open(f, encoding='utf-8-sig').read()
    L = t.splitlines()
    ng = []
    if TAGS not in L[-1]:
        ng.append('最後の行がタグでない: %r' % L[-1])
    if '▼チケット情報はこちら' not in t:
        ng.append('CTA「▼チケット情報はこちら」が無い')
    else:
        i = [k for k, x in enumerate(L) if '▼チケット情報はこちら' in x][0]
        u = L[i + 1].strip() if i + 1 < len(L) else ''
        if not u.startswith('oshinavi.jp'):
            ng.append('CTAの次の行がURLでない: %r' % u)
    if 'https://' in t or 'http://' in t:
        ng.append('https:// が入っている')
    for k, x in enumerate(L):
        body = x.replace('モーニング娘。', 'モーニング娘')
        if re.search(r'。(?!$)', body):
            ng.append('「。」の後に改行が無い %d行目: %s' % (k + 1, x[:40]))
        if re.search(r'\d+\s*件(?!以上|あるわ|近く)', x) and not re.search(r'他にも', x):
            ng.append('件数らしき数字 %d行目: %s' % (k + 1, x[:40]))
        for m in re.finditer(r'(\d{1,2})/(\d{1,2})\s*[（(]([月火水木金土日])', x):
            mo, d, w = int(m.group(1)), int(m.group(2)), m.group(3)
            y = 2026 if mo >= 9 else 2027
            real = WD[datetime.date(y, mo, d).weekday()]
            if real != w:
                ng.append('曜日が違う %d行目: %s/%s(%s)→実は%s' % (k + 1, mo, d, w, real))
    for b in BAN:
        if b in t:
            ng.append('封印語「%s」' % b)
    soft = [s for s in SOFT if s in re.sub(r'【[^】]*】', '', t)]
    for s in re.split(r'[。\n]', t):
        s = s.strip()
        if len(s) >= 12 and not re.match(r'^\d{1,2}:\d{2} ', s) and s not in (HEAD, TAGS) and not s.startswith('oshinavi.jp') and '▼' not in s and '【' not in s:
            phr.setdefault(s, set()).add(f[-10:])
    print('■ %s  %d字  %s' % (f[-10:], len(t), 'OK' if not ng else 'NG %d' % len(ng)))
    for n in ng:
        print('   ❌ ' + n)
    if soft:
        print('   ⚠️ 読者目線か目で確かめる語: %s' % '・'.join(soft))
    bad += len(ng)
dup = {s: fs for s, fs in phr.items() if len(fs) > 1}
if dup:
    print('\n⚠️ 投稿をまたいで同じ文:')
    for s, fs in dup.items():
        print('   %s … %s' % (s[:40], sorted(fs)))
if skipped:
    print('\n（9/15 の見出しでないので見ていない: %s）' % ' '.join(f[-10:] for f in skipped))
print('\nNG合計 %d' % bad)
