# -*- coding: utf-8 -*-
"""新着プール(genre:"new")の再チェック。reconcileで拾えない型だけを見る。
 A) 同じバッジ文字列が2枚以上（席種違いが1枠に潰れる型・reconcileは枠数一致と出る）
 B) 全角ラテン/数字の残り（レビューの苦行防止）
 C) バッジの公演日が完全M/D形か（略記・欠落）
 D) 締切 > 公演日 の cap逆転
 E) 既存エントリとのeventCd重複・正規化名重複
 F) 発売前枠に saleUntilSoldOut が付いていないか
 G) startDate==date の隠れ枠予備軍
出力は tmp/newpool_qc_0731.md
"""
import re, json, io, unicodedata, datetime

TODAY = datetime.date.today().isoformat()

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
E = json.loads(m.group(2))
NEW = [e for e in E if e.get('genre') == 'new']
OLD = [e for e in E if e.get('genre') != 'new']

out = io.open('tmp/newpool_qc_0731.md', 'w', encoding='utf-8')
W = out.write
W('# 新着プール再チェック %s  対象 %d件\n\n' % (TODAY, len(NEW)))


def evcd(u):
    m = re.search(r'event(?:Bundle)?Cd=(\w+)', u or '')
    return m.group(1) if m else None


def all_cds(e):
    s = set()
    for k in ('pia',):
        c = evcd((e.get('links') or {}).get(k))
        if c:
            s.add(c)
    for t in e.get('tickets', []):
        c = evcd(t.get('url'))
        if c:
            s.add(c)
    return s


def norm_name(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s　・･!！?？「」『』【】\[\]（）()~〜ー\-]', '', s).lower()


# A) 同一バッジ文字列
W('## A) 同じバッジ文字列が2枚以上\n')
n = 0
for e in NEW:
    seen = {}
    for t in e.get('tickets', []):
        seen.setdefault(t.get('type'), []).append(t)
    for ty, ts in seen.items():
        if len(ts) > 1:
            W('- %s : 「%s」× %d\n' % (e['name'], ty, len(ts))); n += 1
W('（%d件）\n\n' % n)

# B) 全角ラテン/数字の残り
W('## B) 全角ラテン/数字の残り\n')
n = 0
FW = re.compile(r'[Ａ-Ｚａ-ｚ０-９]')
for e in NEW:
    fields = [('name', e.get('name')), ('artist', e.get('artist')),
              ('venue', e.get('venue')), ('dateLabel', e.get('dateLabel'))]
    fields += [('ticket', t.get('type')) for t in e.get('tickets', [])]
    for k, v in fields:
        if v and FW.search(v):
            W('- %s [%s] %s\n' % (e['name'], k, v)); n += 1
W('（%d件）\n\n' % n)

# C) バッジの公演日が完全M/D形か
W('## C) バッジ公演日の形（略記・日付なし）\n')
n = 0
for e in NEW:
    for t in e.get('tickets', []):
        ty = t.get('type') or ''
        mm = re.search(r'[（(]([^（）()]*公演[^（）()]*)[）)]', ty)
        if not mm:
            W('- %s : 公演日カッコ無し「%s」\n' % (e['name'], ty)); n += 1; continue
        inner = mm.group(1)
        if not re.search(r'\d{1,2}/\d{1,2}', inner):
            W('- %s : 公演日が数値でない「%s」\n' % (e['name'], ty)); n += 1
        elif re.search(r'\d{1,2}/\d{1,2}\s*[-‐−–—]\s*\d{1,2}(?!/)', inner):
            W('- %s : 略記の疑い「%s」\n' % (e['name'], ty)); n += 1
W('（%d件）\n\n' % n)

# D) cap逆転（締切 > 公演日）
W('## D) 締切が公演日より後（cap逆転）\n')
n = 0
for e in NEW:
    for t in e.get('tickets', []):
        if t.get('date') and e.get('date') and t['date'] > e['date']:
            W('- %s : 締切%s > 千秋楽%s 「%s」\n' % (e['name'], t['date'], e['date'], t.get('type'))); n += 1
W('（%d件）\n\n' % n)

# E) 既存との重複
W('## E) 既存エントリとの重複（eventCd / 正規化名）\n')
n = 0
old_cd = {}
for e in OLD:
    for c in all_cds(e):
        old_cd.setdefault(c, []).append(e)
old_nm = {}
for e in OLD:
    old_nm.setdefault(norm_name(e.get('name')), []).append(e)
for e in NEW:
    for c in all_cds(e):
        if c in old_cd:
            W('- eventCd重複 %s : 新着「%s」⇔ 既存「%s」\n' % (c, e['name'], old_cd[c][0]['name'])); n += 1
    k = norm_name(e.get('name'))
    if k in old_nm:
        W('- 名前重複 : 新着「%s」⇔ 既存「%s」\n' % (e['name'], old_nm[k][0]['name'])); n += 1
# 新着どうし
seen_cd = {}
for e in NEW:
    for c in all_cds(e):
        if c in seen_cd:
            W('- 新着どうしeventCd重複 %s : 「%s」⇔「%s」\n' % (c, e['name'], seen_cd[c]['name'])); n += 1
        else:
            seen_cd[c] = e
W('（%d件）\n\n' % n)

# F) 発売前枠のsaleUntilSoldOut
W('## F) 発売前枠に saleUntilSoldOut\n')
n = 0
for e in NEW:
    for t in e.get('tickets', []):
        if t.get('saleUntilSoldOut') and t.get('startDate') and t['startDate'] > TODAY:
            W('- %s : 「%s」\n' % (e['name'], t.get('type'))); n += 1
W('（%d件）\n\n' % n)

# G) 隠れ枠予備軍
W('## G) startDate==date（締切未取込）\n')
n = 0
for e in NEW:
    for t in e.get('tickets', []):
        if t.get('startDate') and t['startDate'] == t.get('date'):
            W('- %s : 「%s」 %s\n' % (e['name'], t.get('type'), t['date'])); n += 1
W('（%d件）\n\n' % n)

# H) 参考: ぴあ以外（reconcile_pia対象外）
W('## H) ぴあリンクが無い＝ぴあゲート対象外\n')
n = 0
for e in NEW:
    if not (e.get('links') or {}).get('pia'):
        ven = [k for k, v in (e.get('links') or {}).items() if v and k in ('rakuten', 'eplus', 'lawson')]
        W('- %s （%s）\n' % (e['name'], ','.join(ven) or 'リンク無し')); n += 1
W('（%d件）\n' % n)
out.close()
print('wrote tmp/newpool_qc_0731.md  新着%d件' % len(NEW))
