# -*- coding: utf-8 -*-
# 楽天の「未登録?」22件を、名前の核＋公演日で登録済みと突き合わせる
# （スラッグが無くても、同じ公演がぴあで登録されていることがある）
import json, io, re, unicodedata

d = json.load(open('tmp/rakuten_presale.json', encoding='utf-8'))
h = open('index.html', encoding='utf-8', newline='').read()
ev = json.loads(re.search(r'const EVENTS = (\[.*?\]);\r?\n', h, re.S).group(1))

slug_re = re.compile(r'/(rt[0-9a-z]{5})/')
slugs_in_html = set(re.findall(r'(rt[0-9a-z]{5})', h))


def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    s = re.sub(r'[\s　"\'’”・･\.。、,：:／/｜|\-–—〜~\[\]［］()（）【】<>＜＞「」『』!！?？*＊☆★#＃]', '', s)
    return s.lower()


def core(name):
    """楽天の名前から「アーティスト名らしい核」を取る（［］の前・記号で切る）"""
    n = re.split(r'[［\[]', name)[0]
    n = re.sub(r'<[^>]*>', '', n)
    return norm(n)[:14]


unreg = []
for r in d['onsale']:
    m = slug_re.search(r['url'])
    if m and m.group(1) in slugs_in_html:
        continue
    unreg.append(r)

out = io.open('tmp/rak_dedup_0918.txt', 'w', encoding='utf-8')
out.write(f"スラッグで未登録だった {len(unreg)}件を、名前の核＋公演日で当て直す\n")
for r in unreg:
    c = core(r['name'])
    dates = {x['date'] for x in (r.get('status_rows') or []) if x.get('date')}
    hits = []
    for e in ev:
        blob = norm(f"{e.get('artist','')}{e.get('name','')}")
        if c and c in blob:
            edates = set()
            s = json.dumps(e, ensure_ascii=False)
            for mm in re.finditer(r'(\d{4})-(\d{2})-(\d{2})', s):
                edates.add(mm.group(0))
            shared = dates & edates
            hits.append((e['id'], e.get('artist', '')[:34], e.get('date'), sorted(shared)[:3]))
    tag = '🚨本当に未登録' if not hits else '⚠️似た登録あり'
    out.write(f"\n{tag}\t{r['name'][:50]}\t公演{r['first']}〜{r['last']}\t核={c!r}\n  {r['url']}\n")
    for hh in hits[:6]:
        out.write(f"    → id{hh[0]} {hh[1]} 公演{hh[2]} 同じ日付{hh[3]}\n")
out.close()
print('ok', len(unreg))
