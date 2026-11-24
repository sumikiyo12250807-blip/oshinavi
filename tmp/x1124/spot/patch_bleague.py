# -*- coding: utf-8 -*-
# 抜き打ち 🔴57757 の根っこ＝build_bleague_entries がシーズンシート・席パック（販売用の器。売り場「1/19に試合はございません」）を
#   「ホーム対ホーム」の試合として組み、器の日付に「試合開始」を付けていた → セット販売として組む
import io
p = 'C:/Users/user/oshinavi/tools/build_bleague_entries.py'
s = io.open(p, encoding='utf-8').read()
R = [
("""    if '駐車' in name:""",
"""    # 2026-11-24 抜き打ち 57757：シーズンシート・席パック＝販売用の器（器の日付に試合は無い）＝試合として出さない
    SEASON = bool(re.search(r'シーズンシート|シーズンチケット|シーズンパス|年間シート|パック|プラン', name)) or (home and away and home == away)
    if SEASON:
        artist = home or artist.split('／')[0]
        name = re.sub(r'^.+?対.+?（.*?）\\s*', '', name).strip() or name
        if artist not in name:
            name = artist + ' ' + name
    if '駐車' in name:"""),
("""    head = '一般販売（%s公演）' % ('%s %s' % (pref, show) if pref else show)""",
"""    head = '一般販売（%s公演）' % ('%s %s' % (pref, show) if pref else show)
    if SEASON:
        head = '一般販売（シーズンシート・席のセット）'"""),
("""        'dateLabel': jp(date) + (' %s試合開始' % stime if stime else ''),""",
"""        'dateLabel': ('ホームゲームの席のセット販売（%s）' % (pref or venue or '')) if SEASON else (jp(date) + (' %s試合開始' % stime if stime else '')),"""),
]
for a, b in R:
    assert s.count(a) == 1, a
    s = s.replace(a, b)
# 器の日付でなく販売の締切でカードを終える
a = "    e = {\n        'artist': artist,"
assert s.count(a) == 1
s = s.replace(a, "    if SEASON:\n        date = tk['date']\n" + a)
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
