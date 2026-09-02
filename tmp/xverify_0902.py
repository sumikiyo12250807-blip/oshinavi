# -*- coding: utf-8 -*-
"""X投稿5本の機械検品（2026-09-02 夜の便）。

見るもの:
  ① 明日9/3発売の素材の行が、担当の投稿にぜんぶ載っているか（1件も落ちていないか）
  ② 見出し／CTA／素のoshinavi.jp／タグ
  ③ 封印フレーズ・禁止語
  ④ 「。」の直後が改行になっているか
  ⑤ 曜日が実カレンダーと合っているか
  ⑥ 件数の実数表記（「33件発売」の類）が無いか
  ⑦ 投稿をまたいだ言い回しの使い回し
"""
import datetime, io, os, re, sys, unicodedata
sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAT = os.path.join(ROOT, 'tmp', 'x_material_0902.txt')
POSTS = [os.path.join(ROOT, 'tmp', 'x0902', 'post%d.txt' % i) for i in range(1, 6)]
BUNDLE2POST = {'音楽': 1, 'クラシック': 2, 'エンタメ': 3, 'おでかけ': 4}   # 0は主役枠
HEAD = 'OSHINAVIの"9/3チケット発売"ピックアップ🎫'


def norm(s):
    return re.sub(r'[\s　]+', '', unicodedata.normalize('NFKC', s or '')).lower()


def main():
    for p in POSTS:
        if not os.path.exists(p):
            print('!! %s が無い' % p)
            return 1
    bodies = [io.open(p, encoding='utf-8').read() for p in POSTS]
    nb = [norm(b) for b in bodies]
    ng = 0

    # ① 明日9/3の素材が全部載っているか
    mat = io.open(MAT, encoding='utf-8').read().splitlines()
    in_tomorrow = False
    cur = None
    total = 0
    missing = []
    for ln in mat:
        m = re.match(r'# (.+) に発売開始', ln)
        if m:
            in_tomorrow = m.group(1).startswith('明日')
            continue
        m = re.match(r'^【(.+?)】', ln.strip())
        if m:
            cur = m.group(1)
            continue
        m = re.match(r'^\s{2}(\d{1,2}:\d{2})\s(.+?)\s{3}\[id', ln)
        if not m or not in_tomorrow or cur is None:
            continue
        total += 1
        head = m.group(2).split('／')[0]
        idx = BUNDLE2POST.get(cur)
        if idx is None or norm(head) not in nb[idx]:
            missing.append((cur, m.group(2)))
    print('TOMORROW_ROWS=%d  MISSING=%d' % (total, len(missing)))
    for b, n in missing:
        print('  MISS[%s] %s' % (b, n))
    ng += len(missing)

    # ②③④⑥
    BAN = ['生で浴び', 'あんた', 'みなさん', '皆さん', '両方おさえ', '両方押さえ',
           'とりあえず取', 'キープ', '確保しておく', 'これで全部', 'https://oshinavi',
           'oshinavi.jp?x=', 'oshinavi.jp/?x=']
    for i, b in enumerate(bodies, 1):
        hits = [w for w in BAN if w in b]
        head_ok = b.startswith(HEAD)
        cta_ok = '▼チケット情報はこちら\noshinavi.jp' in b
        tag_ok = b.rstrip().endswith('#OSHINAVI #明日発売 #チケット')
        # 「。」の直後が改行か（末尾と「モーニング娘。」は除く）
        kuten = []
        for m in re.finditer(r'。(?!\n)(.)', b):
            if b[max(0, m.start() - 6):m.start()].endswith('モーニング娘'):
                continue
            kuten.append(b[max(0, m.start() - 12):m.start() + 2].replace('\n', '⏎'))
        cnt = re.findall(r'\d+\s*(?:件|組)(?:発売|の発売|あるわ|以上)', b)
        ok = head_ok and cta_ok and tag_ok and not hits and not kuten
        print('post%d: len=%-5d head=%-5s cta=%-5s tag=%-5s ban=%-6s 句点改行NG=%d 件数表記=%s %s'
              % (i, len(b), head_ok, cta_ok, tag_ok, hits or 'none', len(kuten),
                 cnt or 'none', 'OK' if ok else '🚨'))
        for k in kuten[:4]:
            print('     句点のあと改行なし: …%s' % k)
        if not ok:
            ng += 1

    # ⑤ 曜日
    WD = '月火水木金土日'
    for i, b in enumerate(bodies, 1):
        for m in re.finditer(r'(\d{1,2})/(\d{1,2})\((.)\)', b):
            mm, dd, w = int(m.group(1)), int(m.group(2)), m.group(3)
            y = 2026 if mm >= 9 else 2027
            real = WD[datetime.date(y, mm, dd).weekday()]
            if real != w:
                print('  🚨post%d 曜日ちがい %d/%d(%s) → 正しくは(%s)' % (i, mm, dd, w, real))
                ng += 1

    # ⑦ 使い回し
    sents = {}
    for i, b in enumerate(bodies, 1):
        for s in re.split(r'\n+', b):
            s = s.strip()
            if len(s) >= 12 and not re.match(r'^(\d{1,2}:\d{2}|#|【|▼)', s):
                sents.setdefault(norm(s), []).append(i)
    dup = {k: v for k, v in sents.items() if len(set(v)) > 1}
    print('CROSS_POST_DUP=%d' % len(dup))
    for k, v in list(dup.items())[:8]:
        print('  DUP %s : %s' % (sorted(set(v)), k[:56]))
    ng += len(dup)

    print('\n=== NG合計 %d ===' % ng)
    return 0 if ng == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
