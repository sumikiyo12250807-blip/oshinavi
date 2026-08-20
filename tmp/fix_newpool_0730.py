# -*- coding: utf-8 -*-
"""7/30チェックで見つけた不備を現物編集で直す（id据え置き・丸ごと作り直さない）

 ①Amazonリンクの全角クエリ → 半角化した artist で作り直す
 ②_genre 下書きの補正（ぴあカテゴリ「祭り・花火大会」「博覧会・展示会・見本市」の対応表漏れ）
 ③3457 ギラヴァンツ北九州の席種ラベル復元（〔テーブルシート販売〕が落ちていた）
 ④券種名末尾の余計なピリオド「一般発売.」を除去
"""
import io, json, re, sys, datetime
sys.path.insert(0, 'tools')
from build_pia_entries import amazon_cd, MUSIC_GENRES

GENRE_FIX = {3435: 'fes', 3455: 'fes', 3465: 'art', 3466: 'art'}

h = io.open('index.html', encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in h else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

log = []
for ev in EVENTS:
    if ev.get('genre') != 'new':
        continue
    eid = ev['id']
    # ① Amazon
    lk = ev.get('links') or {}
    if lk.get('amazon'):
        new_amz = amazon_cd(ev['artist'])          # artist は投入時に半角化済み
        if new_amz and new_amz != lk['amazon']:
            lk['amazon'] = new_amz
            log.append('id=%d Amazonリンク作り直し' % eid)
        elif not new_amz:
            lk.pop('amazon')
            log.append('id=%d Amazonリンク削除(キーワード無し)' % eid)
    # ② _genre
    if eid in GENRE_FIX and ev.get('_genre') != GENRE_FIX[eid]:
        log.append('id=%d _genre %s→%s (%s)' % (eid, ev.get('_genre'), GENRE_FIX[eid], ev.get('_piaSub')))
        ev['_genre'] = GENRE_FIX[eid]
    # ③④ チケット券種名
    for t in ev.get('tickets', []):
        ty = t['type']
        new_ty = re.sub(r'(一般発売|一般販売|先行|当日券)\.', r'\1', ty)
        if new_ty != ty:
            log.append('id=%d 券種名のピリオド除去: %s' % (eid, ty))
            t['type'] = new_ty

# ③ ギラヴァンツ＝2枠目に席種ラベルを戻す（ぴあ実ページ＝一般発売〔テーブルシート販売〕）
for ev in EVENTS:
    if ev['id'] != 3457:
        continue
    ts = ev['tickets']
    assert len(ts) == 2, '想定外の枠数 %d' % len(ts)
    assert ts[0]['type'] == ts[1]['type'], '既に区別されている: %r' % [t['type'] for t in ts]
    ts[1]['type'] = ts[1]['type'].replace('一般発売（', '一般発売【テーブルシート販売】（', 1)
    log.append('id=3457 席種ラベル復元: %s' % ts[1]['type'])

bak = 'index.html.bak_%s_newpool_fix' % datetime.date.today().strftime('%m%d')
io.open(bak, 'w', encoding='utf-8', newline='').write(h)
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
io.open('index.html', 'w', encoding='utf-8', newline='').write(
    h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])

io.open('tmp/out_fix_newpool_0730.txt', 'w', encoding='utf-8').write('\n'.join(log))
print('修正 %d件 (backup %s) → tmp/out_fix_newpool_0730.txt' % (len(log), bak))
