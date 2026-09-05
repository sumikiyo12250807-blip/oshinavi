# -*- coding: utf-8 -*-
"""e+「受付中」ぶんのビルド結果を投入形に仕上げる（2026-09-05・第2便）。

やること:
 1. index.html の実データと突き合わせて **eid（/sf/detail/の数字）が既にあるものを落とす**
    （名前では落とさない＝[[feedback_harvest_name_dedup_blindspot]]）
 2. **同じ公演日×同じ会場の既存エントリ**を洗い出して `tmp/batch2_dupsuspect_0905.txt` に出す
    （ここは人が見る。畳む/足すの判断を自動でしない）
 3. id を index.html の最大id+1から振り直す
 4. `_genre` は**手がかりの当て**（e+にはぴあのようなカテゴリが無い）。
    確信が持てないものは `_genre: None` にして、振り分けの時に決める
 5. verifiedAt を今日にする

  python tmp/prep_batch2_0905.py            # 突合と下書き作成
"""
import json, io, re, datetime, unicodedata

TODAY = datetime.date.today().isoformat()
SRC = 'tmp/eplus_built.json'
OUT = 'tmp/eplus_batch2_0905.json'


def nz(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s　・･]', '', s).lower()


hh = io.open('index.html', encoding='utf-8', newline='').read()
db = json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);', hh, re.S).group(1))
maxid = max(int(e['id']) for e in db)
dbids = set(re.findall(r'/sf/detail/(\d+)', hh))

built = json.load(io.open(SRC, encoding='utf-8'))

# --- 1) eidで既出を落とす -------------------------------------------------
def eids_of(e):
    return set(re.findall(r'/sf/detail/(\d+)',
                          json.dumps(e, ensure_ascii=False)))


fresh, already = [], []
for e in built:
    (already if (eids_of(e) & dbids) else fresh).append(e)

# --- 2) 公演日×会場の重なりを洗う ----------------------------------------
idx = {}
for e in db:
    dates = {e['date']} if e.get('date') else set()
    for t in (e.get('tickets') or []):
        for m in re.finditer(r'(\d{1,2})/(\d{1,2})公演', t.get('type') or ''):
            dates.add('%02d-%02d' % (int(m.group(1)), int(m.group(2))))
    for v in re.split(r'[／/]', re.sub(r'^全国ツアー（|）$', '', e.get('venue') or '')):
        if nz(v):
            for d in dates:
                idx.setdefault((d[-5:], nz(v)), []).append(e['id'])

sus = io.open('tmp/batch2_dupsuspect_0905.txt', 'w', encoding='utf-8')
nsus = 0
for b in fresh:
    dates = set()
    for t in b.get('tickets', []):
        for m in re.finditer(r'(\d{1,2})/(\d{1,2})公演', t.get('type') or ''):
            dates.add('%02d-%02d' % (int(m.group(1)), int(m.group(2))))
    if not dates and b.get('date'):
        dates.add(b['date'][-5:])
    vs = [v for v in re.split(r'[／/]', re.sub(r'^全国ツアー（|）$', '', b.get('venue') or '')) if nz(v)]
    hit = set()
    for d in dates:
        for v in vs:
            for i in idx.get((d, nz(v)), []):
                hit.add((d, v, i))
    if hit:
        nsus += 1
        sus.write('■ %s ／ %s\n' % (b.get('artist'), b.get('name')))
        for d, v, i in sorted(hit):
            sus.write('    %s %s → 既存id%s\n' % (d, v, i))
sus.write('\n同じ公演日×会場の既存がある候補 %d件 / 新規候補 %d件\n' % (nsus, len(fresh)))
sus.close()

# --- 3〜5) 仕上げ ---------------------------------------------------------
GAKUSAI = re.compile(r'大学|学園|学院|短期大学|高専|祭>|＜.*祭')
JAZZ = re.compile(r'ジャズ|JAZZ|Jazz|ビッグバンド')
CLASSIC = re.compile(r'交響楽団|オーケストラ|フィルハーモニー|管弦楽|リサイタル|室内楽|弦楽四重奏')
OWARAI = re.compile(r'落語|独演会|寄席|お笑い|漫才|講談')


def genre_hint(e):
    t = (e.get('name') or '') + ' ' + (e.get('venue') or '')
    if GAKUSAI.search(t):
        return 'gakusai'
    if CLASSIC.search(t):
        return 'classic'
    if JAZZ.search(t):
        return 'jazz'
    if OWARAI.search(t):
        return 'owarai'
    return None          # 決めない＝振り分けの時に実物を見て決める


nid = maxid + 1
out = []
for e in fresh:
    e['id'] = nid
    nid += 1
    e['genre'] = 'new'
    e['_genre'] = genre_hint(e)
    e['_extraGenres'] = []
    e['_piaSub'] = None
    e['verified'] = True
    e['verifiedAt'] = TODAY
    out.append(e)

json.dump(out, io.open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

with io.open('tmp/eplus_batch2_0905.txt', 'w', encoding='utf-8') as f:
    f.write('ビルド %d件 → 既にDBにあるeid %d件を除外 → 投入候補 %d件（id%d〜%d）\n\n'
            % (len(built), len(already), len(out), out[0]['id'], out[-1]['id']) if out else 'なし\n')
    for e in out:
        f.write('id%d [%s] %s ／ %s\n   %s ｜ 枠%d\n'
                % (e['id'], e['_genre'] or '未定', e['artist'], e['name'], e['dateLabel'], len(e['tickets'])))

print('BUILT=%d ALREADY=%d NEW=%d (id%s..) DUPSUSPECT=%d'
      % (len(built), len(already), len(out), out[0]['id'] if out else '-', nsus))
