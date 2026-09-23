# -*- coding: utf-8 -*-
"""まとめ投稿に並べた名前が、その投稿のCTA（?genre=◯◯）で本当に出るかを照合する（2026-09-23 夜）。
ユーザー指摘「09:00 下タ村祐輝（チェロ）守光明子（ピアノ）杏華（語り手）／愛知　これってJPOP？」
＝登録は musicetc・extraGenres=[engeki, classic] で、?genre=jpop では出てこない。

🚨サイトの絞り込みは index.html の matchGenre のとおり＝
   ev.genre が一致 **または** ev.extraGenres に含まれる（グループ指定は別扱い）。
   だから「載せた名前が、その投稿のリンクで出るか」はここで機械的に確かめられる。
出力: tmp/x0923/genre_land.txt
"""
import io
import re
import sys

sys.path.insert(0, 'tools')
from check_expired import extract_events_array

# 各まとめ投稿のCTAに書いてあるジャンル
CTA = {
    'post05': ['idol'],
    'post06': ['classic', 'jazz'],
    'post07': ['owarai'],
    'post08': ['jpop', 'rock', 'enka', 'musicetc'],
    'post09': [],   # ジャンルを外して ?status=urgent で着地させた（9ジャンルにまたがるため）
}
# index.html の matchGenre が持っている特例
ALIAS = {'engeki': ['2.5ji', 'seiyuu', 'musical'], 'anime': ['seiyuu']}

events = extract_events_array('index.html')


def lands(ev, gs):
    """その投稿のCTAジャンルのどれかで、このエントリが画面に出るか。
    🚨gs が空＝CTAにジャンルを書いていない（?status=urgent だけ）＝絞り込みが無いので**全部出る**。"""
    if not gs:
        return 'ジャンル指定なし（全部出る）'
    for g in gs:
        if ev.get('genre') == g:
            return g
        if g in (ev.get('extraGenres') or []):
            return g + '(extra)'
        if ev.get('genre') in ALIAS.get(g, []):
            return g + '(特例)'
    return None


out = io.open('tmp/x0923/genre_land.txt', 'w', encoding='utf-8')
for post, gs in sorted(CTA.items()):
    s = io.open('tmp/x0923/%s.txt' % post, encoding='utf-8', newline='').read()
    # 【M/D(曜)発売】の直後のブロックのうち、**明日(9/24)の分だけ**を見る
    m = re.search(r'【9/24\(木\)発売】\n(.*?)\n\n', s, re.S)
    lines = [l for l in m.group(1).splitlines() if re.match(r'^\d{2}:\d{2}\s', l)] if m else []
    out.write('=== %s （CTA: %s）／明日発売 %d行 ===\n' % (post, '+'.join(gs), len(lines)))
    for l in lines:
        nm = l.split(' ', 1)[1].split('／')[0].strip()
        # 名前の頭20字で登録を引く（表記ゆれに強くするため前方一致）
        hits = [e for e in events
                if nm[:14] and nm[:14] in ((e.get('artist') or '') + ' ' + (e.get('name') or ''))]
        if not hits:
            out.write('  ⚠️ 登録が引けない: %s\n' % l)
            continue
        ok = [h for h in hits if lands(h, gs)]
        if ok:
            out.write('  ✅ %s … %s\n' % (nm[:30], lands(ok[0], gs)))
        else:
            g = sorted({h.get('genre') for h in hits})
            ex = sorted({x for h in hits for x in (h.get('extraGenres') or [])})
            out.write('  🚨 %s … 登録genre=%s extra=%s ＝**このリンクでは出ない**\n' % (nm[:30], g, ex))
    out.write('\n')
out.close()
print('wrote tmp/x0923/genre_land.txt')
