# -*- coding: utf-8 -*-
"""(d)(f) 同じ公演日×会場 の別idを探す。実ページから取り直した「公演日+会場」で全DBを走査。"""
import json, io, re, sys, unicodedata
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

EV = json.load(open(r'C:\Users\user\oshinavi\tmp\vfy_all_events_0905.json', encoding='utf-8'))

# 実ページから取り直した (id, 公演日, 会場, 都道府県)
REAL = [
 (6935, '2026-10-15', 'BlackHole', '東京都'),
 (6936, '2026-11-18', '赤羽ReNY alpha', '東京都'),
 (6936, '2026-11-24', 'OSAKA MUSE', '大阪府'),
 (6937, '2026-10-30', 'Live House 獅子王', '東京都'),
 (6938, '2026-09-17', '大阪RUIDO', '大阪府'),
 (6938, '2026-09-18', 'HOLIDAY NEXT NAGOYA', '愛知県'),
 (6938, '2026-09-24', '札幌Crazy Monkey', '北海道'),
 (6938, '2026-09-25', '札幌Crazy Monkey', '北海道'),
 (6938, '2026-10-07', '大塚 Live House Hearts+', '東京都'),
 (6939, '2026-10-28', '東高円寺二万電圧', '東京都'),
 (6940, '2026-11-01', '東海大学湘南キャンパス総合体育館', '神奈川県'),
 (6941, '2026-10-25', '駿河台大学 体育館', '埼玉県'),
 (6942, '2026-10-11', '駒沢学園 記念講堂', '東京都'),
 (6943, '2026-10-15', '高田馬場CLUB PHASE', '東京都'),
 (6944, '2026-12-02', '新宿文化センター 大ホール', '東京都'),
 (6945, '2026-12-09', 'F.A.D YOKOHAMA', '神奈川県'),
 (6103, '2026-10-18', '川崎祐宣記念講堂', '岡山県'),
 (6295, '2026-12-05', 'たけまるホール 大ホール', '奈良県'),
 (6080, '2027-01-13', '愛知県芸術劇場コンサートホール', '愛知県'),
 (583,  '2026-09-26', '池下CLUB UPSET', '愛知'),
]


def nrm(s):
    s = unicodedata.normalize('NFKC', s or '')
    s = re.sub(r'[\s　・･/／()（）\-‐−–—【】\[\]]', '', s).lower()
    return s


def dates_of(e):
    """エントリが持つ公演日候補: date + dateLabel中のYYYY年M月D日 + type中のM/D"""
    ds = set()
    if e.get('date'):
        ds.add(e['date'])
    for y, m, d in re.findall(r'(\d{4})年(\d{1,2})月(\d{1,2})日', e.get('dateLabel') or ''):
        ds.add('%04d-%02d-%02d' % (int(y), int(m), int(d)))
    return ds


out = []
for tid, d, v, p in REAL:
    vn = nrm(v)
    hits = []
    for e in EV:
        if e['id'] == tid:
            continue
        # 会場文字列（venue + dateLabel）に会場名が含まれるか（部分一致どちらの向きでも）
        cand = nrm((e.get('venue') or '') + '|' + (e.get('dateLabel') or ''))
        if not vn or len(vn) < 3:
            continue
        if vn in cand or (len(vn) > 6 and cand and vn[:8] in cand):
            if d in dates_of(e):
                hits.append(e)
    for h in hits:
        out.append('DUP候補: 対象id=%s (%s %s) ← 既存id=%s artist=%s name=%s date=%s venue=%s' % (
            tid, d, v, h['id'], h.get('artist'), h.get('name'), h.get('date'), h.get('venue')))

# ついでに: eplus のURL(数字ID)が別エントリでも使われていないか
epids = {}
for e in EV:
    for tk in (e.get('tickets') or []):
        for m in re.findall(r'/sf/detail/(\d+)', tk.get('url') or ''):
            epids.setdefault(m, set()).add(e['id'])
    ep = (e.get('links') or {}).get('eplus') or ''
    for m in re.findall(r'/sf/detail/(\d+)', ep):
        epids.setdefault(m, set()).add(e['id'])
for k, v in epids.items():
    if len(v) > 1:
        out.append('e+同一ID重複: %s -> ids=%s' % (k, sorted(v)))

# ぴあ eventCd 重複
pids = {}
for e in EV:
    s = json.dumps(e, ensure_ascii=False)
    for m in re.findall(r'eventCd=(\d+)', s):
        pids.setdefault(m, set()).add(e['id'])
for k, v in pids.items():
    if len(v) > 1:
        out.append('ぴあeventCd重複: %s -> ids=%s' % (k, sorted(v)))

io.open(r'C:\Users\user\oshinavi\tmp\vfy_dup_0905.txt', 'w', encoding='utf-8').write('\n'.join(out) or '(なし)')
print('ok', len(out))
