# -*- coding: utf-8 -*-
"""X投稿のCTAリンク（?genre=…&status=…）が、実際に何件を出すのかを数える。2026-09-23 夜。
ユーザー指摘「５件しか出てこない／絞り込みが何の絞り込みか分かりにくいとクリックした後しんどい」。

🚨画面のロジックを読んで再現する（[[feedback_check_existing_logic]]）。
   `status=urgent` は eventReleaseStatus(ev)==="urgent" ＝**発売開始日が7日以内の枠を持つ公演だけ**。
   `status=soon` は urgent+soon（31日以内）、`upcoming` は normal（32日以上先）。
   判定は**発売前（発売開始日が未来）のチケットだけ**で行う＝もう売っている枠は数に入らない。
使い方: python tmp/x0923/count_cta.py
"""
import datetime
import io
import json
import re

TODAY = datetime.date.today()
text = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[)', text)
events, _ = json.JSONDecoder().raw_decode(text, m.start(1))
mg = re.search(r'const GENRE_GROUPS\s*=\s*(\{.*?\});', text, re.S)


def d(s):
    try:
        return datetime.date(*map(int, s.split('-')))
    except Exception:
        return None


def rel_status(ev):
    """発売前の枠だけを見て urgent/soon/normal を返す。発売前が無ければ None。"""
    best = None
    for t in ev.get('tickets') or []:
        sd = d(t.get('startDate') or '')
        if not sd or sd < TODAY:
            continue                      # もう売っている枠は発売フィルタの対象外
        diff = (sd - TODAY).days
        s = 'urgent' if diff <= 7 else ('soon' if diff <= 31 else 'normal')
        rank = {'urgent': 0, 'soon': 1, 'normal': 2}[s]
        if best is None or rank < best[0]:
            best = (rank, s)
    return best[1] if best else None


def genres_of(ev):
    return [ev.get('genre')] + list(ev.get('extraGenres') or [])


def match_genre(ev, g):
    if g == 'all':
        return True
    if ev.get('genre') == g or g in (ev.get('extraGenres') or []):
        return True
    if g == 'engeki' and ev.get('genre') in ('2.5ji', 'seiyuu', 'musical'):
        return True
    if g == 'anime' and ev.get('genre') == 'seiyuu':
        return True
    return False


def count(genre='all', status='all'):
    n = 0
    for ev in events:
        if ev.get('verified') is not True:
            continue
        if not match_genre(ev, genre):
            continue
        if status != 'all':
            r = rel_status(ev)
            if status == 'urgent' and r != 'urgent':
                continue
            if status == 'soon' and r not in ('urgent', 'soon'):
                continue
            if status == 'upcoming' and r != 'normal':
                continue
        n += 1
    return n


rows = []
for g in ('all', 'kids', 'idol', 'jpop', 'rock', 'classic', 'jazz', 'owarai',
          'enka', 'seiyuu', 'fanevent', 'event', 'engeki', 'sports', 'movie'):
    rows.append((g, count(g, 'all'), count(g, 'urgent'), count(g, 'soon')))

out = io.open('tmp/x0923/count_cta.txt', 'w', encoding='utf-8')
out.write('CTAリンクが出す件数（today=%s）\n' % TODAY)
out.write('%-12s %8s %8s %8s\n' % ('ジャンル', '絞りなし', 'urgent', 'soon'))
for g, a, u, s in rows:
    out.write('%-12s %8d %8d %8d\n' % (g, a, u, s))
out.close()
print(io.open('tmp/x0923/count_cta.txt', encoding='utf-8').read())
