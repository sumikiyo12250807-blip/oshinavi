"""育成の安全な適用対象を決める
 安全 = 枠が増える & 「公演名がアーティスト名と完全一致でないヒット」を持たない
 危険 = リスクありアーティスト（別グループ/対バン/ジョイントが混ざる）→ 人が個別に見る
"""
import re, unicodedata

AUD = r'C:\Users\user\oshinavi\tmp\pia_missing_jpop_0802.txt'
GROW = r'C:\Users\user\oshinavi\tmp\grow_jpop_0802.txt'
OUT = r'C:\Users\user\oshinavi\tmp\grow_safe_0802.txt'


def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s　・･,，.。!！?？\-‐―ー~〜/／「」『』()（）\[\]【】"\'’]+', '', s).lower()


# --- リスクありアーティスト集合 ---
head = open(AUD, encoding='utf-8').read().split('■ 別名義・フェス出演の候補')[0]
risky_artists = set()
cur = None
for line in head.splitlines():
    m = re.match(r'● (.+?)\s+（ぴあのヒット', line)
    if m:
        cur = m.group(1).strip()
        continue
    m2 = re.match(r'\s+\[(.+?)\] (.+)$', line)
    if m2 and cur and norm(m2.group(2).strip()) != norm(cur):
        risky_artists.add(norm(cur))

# --- 育成ドライランの各ブロック ---
blocks = open(GROW, encoding='utf-8').read().split('=' * 72)
safe, risky, nogain = [], [], []
for b in blocks:
    m = re.search(r'id=(\d+)\s+(.*?)\s+ぴあURL', b)
    ms = re.search(r'枠 (\d+) → (\d+)', b)
    if not m or not ms:
        continue
    eid, name = int(m.group(1)), m.group(2).strip()
    before, after = int(ms.group(1)), int(ms.group(2))
    rec = (eid, name, before, after)
    if after <= before:
        nogain.append(rec)
    elif norm(name) in risky_artists:
        risky.append(rec)
    else:
        safe.append(rec)

# 既知の地雷は必ず除外
KNOWN_BAD = {3518}
safe2 = [r for r in safe if r[0] not in KNOWN_BAD]
moved = [r for r in safe if r[0] in KNOWN_BAD]
risky += moved

L = ['育成の仕分け  安全%d / 要目視%d / 増えない%d' % (len(safe2), len(risky), len(nogain))]
L.append('')
L.append('=== ✅ 安全に適用できる %d件（増加数順）===' % len(safe2))
for eid, name, b, a in sorted(safe2, key=lambda x: -(x[3] - x[2])):
    L.append('id=%d  %s  枠 %d→%d (+%d)' % (eid, name, b, a, a - b))
L.append('')
L.append('=== ⚠️ 要目視 %d件（別グループ/対バン/ジョイントが混ざる恐れ）===' % len(risky))
for eid, name, b, a in sorted(risky, key=lambda x: -(x[3] - x[2])):
    L.append('id=%d  %s  枠 %d→%d (+%d)' % (eid, name, b, a, a - b))
L.append('')
L.append('=== 増えない %d件（適用しない）===' % len(nogain))
for eid, name, b, a in nogain:
    L.append('id=%d  %s  枠 %d→%d' % (eid, name, b, a))
L.append('')
L.append('SAFE_IDS=' + ','.join(str(r[0]) for r in safe2))

open(OUT, 'w', encoding='utf-8').write('\n'.join(L))
print('safe=%d risky=%d nogain=%d' % (len(safe2), len(risky), len(nogain)))
