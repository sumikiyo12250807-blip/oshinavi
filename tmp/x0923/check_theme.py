# -*- coding: utf-8 -*-
"""まとめ投稿に並べた名前が、その投稿の「見出しで名乗ったジャンル」に本当に当てはまるかを見る。
ユーザー指摘（2026-09-23）「ジャンルの間違いはもう大丈夫なの？　しっかり直してから投稿してよ」。
🚨リンク（?genre=）が通るかとは別の話＝**投稿が「J-POPのまとめ」と名乗っているのに
   チェロとピアノのコンサートが載っている**のがおかしい、という話。
出力: tmp/x0923/theme.txt
"""
import io
import re
import sys
import unicodedata

sys.path.insert(0, 'tools')
from check_expired import extract_events_array

# 投稿が見出しで名乗っているジャンル（＝そこに載ってよい登録ジャンル）
THEME = {
    'post05': (['idol'], 'アイドル'),
    'post06': (['classic', 'jazz'], 'クラシックとジャズ'),
    'post07': (['owarai'], 'お笑いと落語'),
    'post08': (['jpop', 'rock', 'enka'], 'J-POPとロック'),
    'post09': (['event', 'engeki', 'movie', 'sports', 'musical', 'kids',
                'gakusai', 'dinnershow', 'fanevent', 'anime',
                'musicetc'],  # ⑨は残り全部を引き受ける枠＝番組の公開収録なども入る
               'イベントや舞台、映画、スポーツ'),
}


def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s　　]+', '', s).lower()


events = extract_events_array('index.html')
idx = [(norm((e.get('artist') or '') + (e.get('name') or '')), e) for e in events]

out = io.open('tmp/x0923/theme.txt', 'w', encoding='utf-8')
ng = 0
for post in sorted(THEME):
    gs, label = THEME[post]
    s = io.open('tmp/x0923/%s.txt' % post, encoding='utf-8', newline='').read()
    m = re.search(r'【9/24\(木\)発売】\n(.*?)\n\n', s, re.S)
    lines = [l for l in m.group(1).splitlines() if re.match(r'^\d{2}:\d{2}\s', l)] if m else []
    out.write('=== %s 「%sのまとめ」／%d行 ===\n' % (post, label, len(lines)))
    for l in lines:
        nm = l.split(' ', 1)[1].split('／')[0].strip()
        key = norm(nm)[:12]
        hits = [e for k, e in idx if key and key in k]
        if not hits:
            out.write('  ⚠️ 登録が引けない: %s\n' % l)
            continue
        # その日に発売がある登録を優先
        # 🚨同じ名前で登録が複数あることがある（例＝チキン ガーリック ステーキは
        #    jpopの公演3件＋ZAIKOの生配信1件が新着プールにいる）。
        #    **9/24に発売があって、かつ振り分け済み（genre != new）**のものを先に見る。
        sell = [h for h in hits if any((t.get('startDate') == '2026-09-24') for t in (h.get('tickets') or []))]
        cand = [h for h in sell if h.get('genre') != 'new'] or sell or hits
        e = cand[0]
        g = e.get('genre')
        ex = e.get('extraGenres') or []
        fit = (g in gs) or any(x in gs for x in ex)
        mark = '✅' if fit else '🚨'
        if not fit:
            ng += 1
        out.write('  %s %-34s genre=%-11s extra=%s\n' % (mark, nm[:34], g, ex or '-'))
    out.write('\n')
out.write('見出しのジャンルから外れている行 %d\n' % ng)
out.close()
print('wrote tmp/x0923/theme.txt / ng=%d' % ng)
