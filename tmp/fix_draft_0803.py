# -*- coding: utf-8 -*-
"""振り分け前の下書き補正＝_piaSub を更新した PIA_GENRE_MAP で引き直して _genre を直す。
memory: project_vendor_genre_autoassign（判断は投入時の下書き補正で済ませる。振り分け本体では判断しない）

・ぴあが分類しているものは**そのまま**（J-POP・ROCK→jpop 固定。rock/idol へ細分しない）
・人が見るのは _piaSub が「音楽その他」など fallback の分だけ
使い方: python tmp/fix_draft_0803.py [--apply]
"""
import re, io, json, sys, os, importlib.util
# build_pia_entries も import 時に sys.stdout を包む＝TextIOWrapperを二重に被せると閉じられる
sys.stdout.reconfigure(encoding='utf-8')
APPLY = '--apply' in sys.argv

s = importlib.util.spec_from_file_location('bpe', os.path.join('tools', 'build_pia_entries.py'))
bpe = importlib.util.module_from_spec(s)
s.loader.exec_module(bpe)

# 🚨ぴあが「会場の業態」でカテゴリを付けた/粒度が粗い分だけ、主役で読み直す（2026-08-01ユーザー明示）
MANUAL = {
    # id: (genre, extraGenres, 理由)
    3656: ('enka', [], '_piaSub=音楽その他→fes下書き。屋内の公開収録＝fesの定義(複数組+屋外)に合わない歌謡番組'),
    3643: ('dinnershow', ['enka'], '既存726 新浜レオンはenka＝主役で読むとenkaも要る(両方方式)'),
    3629: ('art', ['anime'], '細田守の原点/展＝アート展だがアニメ作品展(既存40ジブリパーク展はanime)'),
}

h = io.open('index.html', encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in h else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

changed = []
for e in EVENTS:
    if e.get('genre') != 'new':
        continue
    old = e.get('_genre')
    oldx = e.get('_extraGenres') or []
    sub = (e.get('_piaSub') or '').split('/')[-1]
    if e['id'] in MANUAL:
        g, x, why = MANUAL[e['id']]
    elif sub in bpe.PIA_GENRE_MAP:
        g, x2 = bpe.PIA_GENRE_MAP[sub]
        x = [x2] if x2 else []
        why = 'ぴあカテゴリ「%s」' % sub
    else:
        continue
    if g != old or x != oldx:
        changed.append((e['id'], e['name'][:30], old, g, x, why))
        if APPLY:
            e['_genre'] = g
            e['_extraGenres'] = x

print('=== 下書き補正 %d件 ===' % len(changed))
for i, n, o, g, x, why in changed:
    print('id%-5d %-30s %s → %s%s | %s' % (i, n, o, g, ('+' + ','.join(x)) if x else '', why))

if not APPLY:
    print('\n=== 表示のみ。適用は --apply ===')
    sys.exit(0)

io.open('index.html.bak_0803_fix_draft', 'w', encoding='utf-8', newline='').write(h)
arr = json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
io.open('index.html', 'w', encoding='utf-8', newline='').write(
    h[:m.start()] + m.group(1) + arr + m.group(3) + h[m.end():])
print('\n適用完了 (backup index.html.bak_0803_fix_draft)')
