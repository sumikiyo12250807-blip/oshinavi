# -*- coding: utf-8 -*-
"""X投稿の機械検品（台本の第4項）。
① 1行目の見出し／CTA／素のoshinavi.jp／タグ
② 「。」の直後が改行か（例外＝モーニング娘。）
③ 封印フレーズ・禁止語
④ HTMLエスケープの残骸（&amp; など）
⑤ 曜日を実カレンダーと照合
⑥ 🚨リストの各行が「素材に実在する」か＝素材に無い名前を書いていないか（いちばん大事）
"""
import re, sys, io, datetime, unicodedata

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

draft = open('tmp/x_draft_0903.txt', encoding='utf-8').read()
material = open('tmp/x_fable_material_0903.md', encoding='utf-8').read()

posts = {}
for m in re.finditer(r'===POST(\d+)===\n(.*?)(?=\n===POST|\Z)', draft, re.S):
    posts[int(m.group(1))] = m.group(2).strip('\n')

# 素材にある「時刻 名前／県」行を集める
mat_lines = set()
for ln in material.splitlines():
    ln = ln.strip()
    if re.match(r'^\d{1,2}:\d{2}\s', ln):
        ln = re.sub(r'\s*［.*$', '', ln).strip()
        mat_lines.add(ln)

HEAD = 'OSHINAVIの"9/4チケット発売"ピックアップ🎫'
BAN = ['あんた', '生で浴びる', '両方おさえる', '両方押さえ', 'https://oshinavi', 'oshinavi.jp?']
WD = '月火水木金土日'

ng = 0
for i in sorted(posts):
    p = posts[i]
    print('\n=== POST%d （%d字）===' % (i, len(p)))

    def bad(msg):
        global ng
        ng += 1
        print('   🚨 ' + msg)

    if not p.startswith(HEAD):
        bad('1行目の見出しが違う: ' + p.splitlines()[0][:40])
    if '▼チケット情報はこちら' not in p:
        bad('CTAが無い')
    if not re.search(r'^oshinavi\.jp$', p, re.M):
        bad('素のoshinavi.jp行が無い')
    if '#OSHINAVI #明日発売 #チケット' not in p:
        bad('タグが無い')
    for b in BAN:
        if b in p:
            bad('禁止語「%s」' % b)
    for esc in ['&amp;', '&quot;', '&lt;', '&gt;', '&#']:
        if esc in p:
            bad('HTMLエスケープの残骸「%s」' % esc)

    # 「。」の直後は改行
    for m in re.finditer(r'。(?!\n)(.)', p):
        ctx = p[max(0, m.start() - 12):m.start() + 2].replace('\n', '⏎')
        if 'モーニング娘' in ctx:
            continue
        bad('「。」の後ろが改行でない: …%s' % ctx)

    # 曜日照合
    for m in re.finditer(r'(\d{1,2})/(\d{1,2})\((.)\)', p):
        mm, dd, w = int(m.group(1)), int(m.group(2)), m.group(3)
        y = 2026 if mm >= 9 else 2027
        real = WD[datetime.date(y, mm, dd).weekday()]
        if w != real and w not in ('祝',):
            bad('曜日が違う %d/%d(%s) → 実際は(%s)' % (mm, dd, w, real))

    # リスト行が素材にあるか
    miss = []
    for ln in p.splitlines():
        ln = ln.strip()
        if not re.match(r'^\d{1,2}:\d{2}\s', ln):
            continue
        norm = unicodedata.normalize('NFKC', ln)
        hit = any(unicodedata.normalize('NFKC', x) == norm for x in mat_lines)
        if not hit:
            miss.append(ln)
    if miss:
        for x in miss:
            bad('素材に無いリスト行: %s' % x)
    else:
        print('   ✅ リスト行は全部が素材に実在')

print('\n=== 指摘 %d件 ===' % ng)
