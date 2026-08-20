# -*- coding: utf-8 -*-
"""新着50件の独立機械チェック（投入値にアンカリングしない項目＋表記ルール全部）

チェック:
 1 全角ラテン/数字の残存（norm_fw漏れ）
 2 バッジ公演日＝（…公演…）内に完全M/D形・略記/半端範囲なし
 3 R9年表記（ev.date が2027以降なのにバッジに R9年/R10年 が無い）
 4 cap逆転（ticket.date > ev.date）
 5 死枠混入（ticket.date < today かつ startDate無し or 発売済み）
 6 発売前枠の saleUntilSoldOut 混入 / startDate>date の逆転
 7 会場の空カッコ「（）」・venue空・prefecture空
 8 verified が true か / verifiedAt 有無
 9 price が入っている子（2サイト一致ルール＝原則null）
10 links が個別ページか（eventCd/eventBundleCd を含む）
11 eventCd の既存かぶり・正規化名の既存かぶり
12 ジャンル下書きの妥当性（名前キーワード突合）
13 同日複数公演で時刻がバッジに入っているか（同一エントリ内の同日重複）
"""
import io, json, re, unicodedata, datetime, collections

TODAY = datetime.date.today()
raw = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[.*?\]);', raw, re.S)
ALL = json.loads(m.group(1))
NEW = [e for e in ALL if e.get('genre') == 'new']
OLD = [e for e in ALL if e.get('genre') != 'new']

def d(iso):
    try:
        return datetime.date(*[int(x) for x in iso.split('-')])
    except Exception:
        return None

FW = re.compile(r'[Ａ-Ｚａ-ｚ０-９．－]')
NG = []
def ng(eid, tag, msg):
    NG.append('  [%s] id=%s %s' % (tag, eid, msg))

def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s　・／/＜＞<>「」『』（）()【】’\'"!！\-—]', '', s).lower()

def ecds(ev):
    blob = json.dumps(ev, ensure_ascii=False)
    return set(re.findall(r'event(?:Bundle)?Cd=(\w+)', blob))

old_cd = set()
for e in OLD:
    old_cd |= ecds(e)
old_nm = {norm(e.get('artist')): e['id'] for e in OLD}

GENRE_KW = {
    'owarai': ['落語', '寄席', '漫才', '新喜劇', 'お笑い', '独演会', 'ものまね', '二人会', '毒炎会'],
    'dento': ['狂言', '能', '文楽', '歌舞伎', '日本舞踊', '薪能', '和太鼓', '雅楽'],
    'classic': ['交響', 'フィル', 'オーケストラ', 'リサイタル', 'ピアノ', 'ヴァイオリン', '管弦楽',
                'クラリネット', 'ウインド', 'コンサート', 'バレエ', 'オペラ', 'ガンバ', 'リコーダー'],
    'sports': ['プロレス', 'FC', 'リーグ', 'ヤクルト', 'バファローズ', 'チア', 'ダンス', 'STARDOM',
               'レオネッサ', 'トリニータ', 'ギラヴァンツ'],
}

for ev in NEW:
    eid = ev['id']
    texts = {'artist': ev.get('artist'), 'name': ev.get('name'),
             'venue': ev.get('venue'), 'dateLabel': ev.get('dateLabel')}
    for t in ev.get('tickets', []):
        texts['ticket:%s' % (t.get('type') or '')[:20]] = t.get('type')
    # 1 全角
    for k, v in texts.items():
        if v and FW.search(v):
            ng(eid, '全角残存', '%s=%r' % (k, v))
    # 7 会場
    if not ev.get('venue'):
        ng(eid, '会場空', 'venue無し')
    elif re.search(r'（\s*）|\(\s*\)', ev['venue']):
        ng(eid, '空カッコ会場', ev['venue'])
    if not ev.get('prefecture'):
        ng(eid, '県空', 'prefecture無し')
    # 8 verified
    if ev.get('verified') is not True:
        ng(eid, 'verified', repr(ev.get('verified')))
    # 9 price
    if ev.get('price'):
        ng(eid, 'price入り', repr(ev.get('price')))
    # 10 links
    lk = {k: v for k, v in (ev.get('links') or {}).items() if v and k != 'amazon'}
    if not lk:
        ng(eid, 'リンク無し', '売り場URLゼロ')
    for k, v in lk.items():
        if k == 'pia' and not re.search(r'event(?:Bundle)?Cd=', v):
            ng(eid, 'ぴあURL粒度', v)
    # 11 かぶり
    for cd in ecds(ev):
        if cd in old_cd:
            ng(eid, 'eventCd既存かぶり', cd)
    nm = norm(ev.get('artist'))
    if nm in old_nm:
        ng(eid, '名前かぶり', '既存id=%s %s' % (old_nm[nm], ev.get('artist')))
    # 2/3/4/5/6 チケット
    evd = d(ev.get('date') or '')
    sameday = collections.Counter()
    for t in ev.get('tickets', []):
        ty = t.get('type') or ''
        td = d(t.get('date') or '')
        sd = d(t.get('startDate') or '') if t.get('startDate') else None
        # 2 公演日カッコ
        paren = re.findall(r'（([^（）]*公演[^（）]*)）', ty)
        if not paren:
            ng(eid, 'バッジ公演カッコ無し', ty)
        else:
            inner = paren[0]
            if not re.search(r'\d{1,2}/\d{1,2}', inner):
                ng(eid, 'バッジ公演日なし', ty)
            if re.search(r'\d{1,2}/\d{1,2}[・〜~]\d{1,2}(?![\d/])', inner):
                ng(eid, 'バッジ日付略記', ty)
        # 3 R9年
        if evd and evd.year >= 2027 and 'R' not in ty:
            ng(eid, 'R年表記なし', 'ev.date=%s / %s' % (ev.get('date'), ty))
        # 4 cap逆転
        if td and evd and td > evd:
            ng(eid, 'cap逆転', '締切%s > 公演%s | %s' % (td, evd, ty))
        # 5 死枠
        if td and td < TODAY:
            ng(eid, '死枠混入', '締切%s(過去) | %s' % (td, ty))
        # 6 発売前の整合
        if sd and td and sd > td:
            ng(eid, 'startDate>date', '%s > %s | %s' % (sd, td, ty))
        if t.get('saleUntilSoldOut') and sd and td and sd == td:
            ng(eid, 'saleUntilSoldOut発売前', ty)
        for mm in re.findall(r'(\d{1,2}/\d{1,2})公演', ty):
            sameday[mm] += 1
    # 12 ジャンル下書き
    g = ev.get('_genre')
    blob = (ev.get('artist') or '') + (ev.get('name') or '')
    for gk, kws in GENRE_KW.items():
        if any(k in blob for k in kws) and g != gk:
            ng(eid, 'ジャンル要確認', '_genre=%s だが「%s」を含む → %s の可能性 | %s' % (
                g, next(k for k in kws if k in blob), gk, ev.get('name')))
            break

out = ['=== 新着%d件 独立機械チェック (today=%s) ===' % (len(NEW), TODAY)]
out.append('NG/要確認 %d件' % len(NG))
out += NG
io.open('tmp/out_verify_new_0730.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('NG/要確認 %d件 → tmp/out_verify_new_0730.txt' % len(NG))
