# -*- coding: utf-8 -*-
"""新着プール全件で「会場数 vs バッジの県数」「会場名から推定した県 vs バッジの県」を突き合わせ、
   ルシファー吉岡型の県取りこぼしを洗い出す。
"""
import sys, io, re, json, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PREFS = ['北海道', '青森', '岩手', '宮城', '秋田', '山形', '福島', '茨城', '栃木', '群馬',
         '埼玉', '千葉', '東京', '神奈川', '新潟', '富山', '石川', '福井', '山梨', '長野',
         '岐阜', '静岡', '愛知', '三重', '滋賀', '京都', '大阪', '兵庫', '奈良', '和歌山',
         '鳥取', '島根', '岡山', '広島', '山口', '徳島', '香川', '愛媛', '高知', '福岡',
         '佐賀', '長崎', '熊本', '大分', '宮崎', '鹿児島', '沖縄']

src = open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'const EVENTS = (\[.*?\n\s*\]);', src, re.S)
events = json.loads(m.group(1))
new = sorted([e for e in events if e.get('genre') == 'new'], key=lambda e: e['id'])

print(f'新着 {len(new)}件を点検\n')
flag = 0
for e in new:
    v = e.get('venue') or ''
    mm = re.match(r'全国ツアー（(.*)）$', v)
    if not mm:
        continue                      # 単一会場は対象外
    venues = [x for x in mm.group(1).split('／') if x]
    # バッジの県（（…県・県 M/D公演）の前半）
    badge_prefs = set()
    for t in e.get('tickets') or []:
        b = re.search(r'（([^（）]*?)\s+[^（）]*公演）', t.get('type') or '')
        if b:
            for p in b.group(1).split('・'):
                p = p.strip()
                if p:
                    badge_prefs.add(p)
    note = []
    if len(venues) > len(badge_prefs):
        note.append(f'会場{len(venues)} > バッジ県{len(badge_prefs)}')
    if note:
        flag += 1
        print(f'⚠️ id{e["id"]} {e["name"][:40]}')
        print(f'    会場({len(venues)}): {" / ".join(venues)}')
        print(f'    バッジ県({len(badge_prefs)}): {"・".join(sorted(badge_prefs))}')
        print(f'    → {" / ".join(note)}')
print('\n該当なし' if not flag else f'\n→ 要確認 {flag}件')
