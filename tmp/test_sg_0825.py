# -*- coding: utf-8 -*-
"""sg(サブジャンル) / rg(地域) が rlsInfo.do の絞り込みとして効くかを件数で確かめる。
効けば「音楽の受付中4437件が1000件で頭打ち」問題を割って全部見られる。"""
import re, sys, time, html, http.client
sys.stdout.reconfigure(encoding='utf-8')

conn = http.client.HTTPSConnection('t.pia.jp', timeout=30)


def get(path):
    conn.request('GET', path, headers={'User-Agent': 'Mozilla/5.0',
                                       'Connection': 'keep-alive',
                                       'Accept-Encoding': 'identity'})
    r = conn.getresponse()
    return r.status, r.read().decode('utf-8', 'replace')


def total(f, lg='01'):
    st, b = get('/pia/rlsInfo.do?lg=%s&%s&page=1' % (lg, f))
    m = re.search(r'全\s*([0-9,]+)\s*件', b)
    if not m:
        m = re.search(r'([0-9,]+)\s*件', b)
    return int(m.group(1).replace(',', '')) if m else None


# フォームから音楽(lg=01)のsg一覧を取る
st, form = get('/pia/search_dtl_input.do')
sgs = []
for m in re.finditer(r'<input[^>]*name="sg"[^>]*value="(01\d+)"[^>]*>', form):
    v = m.group(1)
    # ラベル＝直後の<label>か、value属性を含むタグの近傍テキスト
    idx = m.end()
    lab = re.search(r'>([^<>]{1,30})<', form[idx:idx + 300])
    sgs.append((v, html.unescape(lab.group(1)).strip() if lab else ''))

print('音楽(lg=01)のsg候補:', len(sgs))
base = total('rlsStatus=0101')
print('絞り無し 受付中 =', base)
print()
s = 0
for v, lab in sgs:
    n = total('rlsStatus=0101&sg=%s' % v)
    print('sg=%-9s %-22s %s' % (v, lab[:22], n))
    if n:
        s += n
    time.sleep(1.0)
print('合計 =', s, ' / 絞り無し =', base)

print()
for rg in ('01', '02', '03', '05'):
    n = total('rlsStatus=0101&rg=%s' % rg)
    print('rg=%s -> %s' % (rg, n))
    time.sleep(1.0)
