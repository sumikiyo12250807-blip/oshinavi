# -*- coding: utf-8 -*-
"""X投稿5本の機械検品（素材の行がぜんぶ載っているか＋禁止語）。"""
import io, os, re, sys, unicodedata
sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAT = os.path.join(ROOT, 'tmp', 'x_material_0901.txt')
POSTS = [os.path.join(ROOT, 'tmp', 'x0901', 'post%d.txt' % i) for i in range(1, 6)]

# 素材の束 -> どの投稿に載るか
BUNDLE2POST = {'音楽': 0, 'クラシック': 1, '舞台・映画': 2, 'お笑い': 3, 'スポーツ': 4}


def norm(s):
    return re.sub(r'[\s　]+', '', unicodedata.normalize('NFKC', s or '')).lower()


def main():
    mat = io.open(MAT, encoding='utf-8').read().splitlines()
    bodies = [io.open(p, encoding='utf-8').read() for p in POSTS]
    nbodies = [norm(b) for b in bodies]

    cur_bundle = None
    total = 0
    missing = []
    for ln in mat:
        m = re.match(r'^【(.+?)】', ln.strip())
        if m:
            cur_bundle = m.group(1)
            continue
        m = re.match(r'^\s{2}(\d{1,2}:\d{2})\s(.+)$', ln)
        if not m or cur_bundle is None:
            continue
        total += 1
        name = m.group(2).strip()
        idx = BUNDLE2POST.get(cur_bundle)
        if idx is None:
            missing.append((cur_bundle, name, 'bundle unknown'))
            continue
        # 県の重複表記（／大阪／大阪）は投稿側で整えてよいので、先頭のイベント名部分で照合
        head = name.split('／')[0]
        if norm(head) not in nbodies[idx]:
            missing.append((cur_bundle, name, 'post%d' % (idx + 1)))
    print('MATERIAL_ROWS=%d  MISSING=%d' % (total, len(missing)))
    for b, n, w in missing:
        print('  MISS[%s] %s -> %s' % (b, n, w))

    BAN = ['生で浴び', 'あんた', 'みなさん', '皆さん', '両方おさえ', '両方押さえ',
           'とりあえず取', 'キープ', '確保しておく', 'これで全部', 'https://oshinavi']
    for i, b in enumerate(bodies, 1):
        hits = [w for w in BAN if w in b]
        head_ok = b.startswith('OSHINAVIの"9/2発売"ピックアップ🎫')
        cta_ok = ('▼チケット件はこちら' in b) or ('▼チケット情報はこちら\noshinavi.jp' in b)
        tag_ok = b.rstrip().endswith('#OSHINAVI #明日発売 #チケット')
        print('post%d: len=%d head=%s cta=%s tag=%s ban=%s'
              % (i, len(b), head_ok, cta_ok, tag_ok, hits or 'none'))

    # 投稿をまたいだ言い回しの使い回し（10文字以上の一致する文）
    sents = {}
    for i, b in enumerate(bodies, 1):
        for s in re.split(r'\n+', b):
            s = s.strip()
            if len(s) >= 12 and not s.startswith(('10:', '11:', '12:', '18:', '19:', '20:', '0:', '#', '【', '▼')):
                sents.setdefault(norm(s), []).append(i)
    dup = {k: v for k, v in sents.items() if len(set(v)) > 1}
    print('CROSS_POST_DUP_SENTENCES=%d' % len(dup))
    for k, v in list(dup.items())[:10]:
        print('  DUP in %s : %s' % (sorted(set(v)), k[:60]))
    return 0


if __name__ == '__main__':
    sys.exit(main())
