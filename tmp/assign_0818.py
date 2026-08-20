# -*- coding: utf-8 -*-
"""2026-08-18 朝の振り分け（id4489-4538 の50件）。

・原則＝ぴあカテゴリ由来の `_genre` をそのまま genre へ移す（自分で再分類しない）
  [[project_vendor_genre_autoassign]]
・OVERRIDE は「bundleでぴあカテゴリが取れず名前fallbackに倒れた」ものだけ。
  根拠は別エージェントが実ページから独立に読んだぴあのパンくず表記。
・相談待ちの4件（4377/4400/4417/4418）は触らず新着プールに残す＝NEW_ORDER もその4件だけ残す。
"""
import re, json, sys, os
sys.stdout.reconfigure(encoding='utf-8')

APPLY = '--apply' in sys.argv

# 振り分けない（ユーザー相談待ち）
KEEP_IN_POOL = [4377, 4400, 4417, 4418]

# 下書きが名前fallbackで倒れていた分だけ是正する
OVERRIDE = {
    4506: ('jpop',     'ぴあカテゴリ無しのbundle。ハンブレッダーズ＝ロックバンド（下書きengeki）'),
    4514: ('jpop',     'ぴあカテゴリ無しのbundle。奇妙礼太郎BAND＝音楽（下書きengeki）'),
    4521: ('jpop',     'ぴあは「イベント＞学園祭」だが主役 yama はJ-POPアーティスト（下書きengeki）'),
    4527: ('fes',      '三井アウトレットパーク北陸小矢部の特設会場＝屋外・複数組の音楽フェス（下書きengeki）'),
    4528: ('musicetc', 'ぴあは「音楽＞民族音楽」。OSHINAVIに該当が無いので受け皿へ（下書きyougaku）'),
    4530: ('dento',    'ぴあは「音楽＞演歌・邦楽」だが DRUM TAO は和太鼓＝伝統（下書きenka）'),
}

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

moved, skipped, rows = 0, 0, []
for e in EVENTS:
    if e.get('genre') != 'new':
        continue
    if e['id'] in KEEP_IN_POOL:
        skipped += 1
        print('⏸ id%-5s 相談待ちで据置 %s' % (e['id'], (e.get('artist') or '')[:28]))
        continue
    g = e.get('_genre')
    note = ''
    if e['id'] in OVERRIDE:
        g, note = OVERRIDE[e['id']]
    if not g:
        print('⚠️ id%s は _genre が無い＝手当て要' % e['id'])
        continue
    ex = list(e.get('_extraGenres') or [])
    e['genre'] = g
    if ex:
        e['extraGenres'] = sorted(set((e.get('extraGenres') or []) + ex))
    for k in ('_genre', '_extraGenres', '_piaSub'):
        e.pop(k, None)
    moved += 1
    links = e.get('links') or {}
    rows.append((e['id'], (e.get('artist') or ''), g,
                 links.get('pia') or links.get('eplus') or links.get('rakuten') or '', note))
    print('id%-5s → %-9s %s%s' % (e['id'], g, (e.get('artist') or '')[:30],
                                  ('   ← ' + note) if note else ''))

print()
print('振り分け %d件 / 据置 %d件' % (moved, skipped))
if not APPLY:
    print('（判定のみ。適用は --apply）')
    sys.exit(0)

bak = 'index.html.bak_0818_assign'
if not os.path.exists(bak):
    open(bak, 'w', encoding='utf-8').write(h)

new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
h2 = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]

# NEW_ORDER は相談待ちの4件だけ残す（番号は据え置き・振り直さない）
m2 = re.search(r'(NEW_ORDER\s*=\s*)(\[.*?\])', h2, re.S)
if m2:
    h2 = h2[:m2.start()] + m2.group(1) + json.dumps(KEEP_IN_POOL) + h2[m2.end():]
    print('NEW_ORDER → %s' % KEEP_IN_POOL)

open('index.html', 'w', encoding='utf-8').write(h2)
print('=== 適用完了 (backup: %s) ===' % bak)

with open('logs/assigned_2026-08-18.md', 'w', encoding='utf-8') as f:
    f.write('# 2026-08-18 朝の振り分け %d件\n\n' % moved)
    f.write('前夜(8/17)に投入した id4489-4538 の50件。独立再照合＋別エージェント2本の再導出（登録値を見せずゼロから）を通してから振り分けた。\n\n')
    f.write('| id | 公演名 | ジャンル | URL | 備考 |\n|---|---|---|---|---|\n')
    for i, nm, g, url, note in rows:
        f.write('| %d | %s | %s | %s | %s |\n' % (i, nm, g, url, note))
    f.write('\n## 振り分けず新着プールに残した4件（ユーザー相談待ち）\n\n')
    f.write('4377 BE WONDERFUL!! ／ 4400 MASTERPIECE 2026 ／ 4417 LEE SANG JUN SHOW 45 ／ 4418 Osaka GLOW\n')
print('logs/assigned_2026-08-18.md に記録')
