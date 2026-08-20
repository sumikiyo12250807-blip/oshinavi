# -*- coding: utf-8 -*-
import re, json, sys
sys.path.insert(0, 'tools')
import check_expired as ce

PATH = 'index.html'
text = open(PATH, encoding='utf-8').read()
entries = ce.extract_events_array(PATH)
by_id = {e['id']: e for e in entries}

def find_span(txt, eid):
    """Return (start,end) char span of the entry object {...} (no trailing comma) for given id."""
    m = re.search(r'\n( *)\{\n *"id": ' + str(eid) + r',', txt)
    if not m:
        raise RuntimeError(f'id {eid} not found')
    bp = txt.index('{', m.start())
    depth = 0
    i = bp
    while i < len(txt):
        c = txt[i]
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return (bp, i + 1)
        i += 1
    raise RuntimeError('brace match failed for ' + str(eid))

def dump_entry(d):
    s = json.dumps(d, indent=6, ensure_ascii=False)
    return '\n'.join('      ' + ln for ln in s.split('\n'))

def backfill_url(e):
    pia = (e.get('links') or {}).get('pia')
    out = []
    for t in e.get('tickets', []):
        t = dict(t)
        if not t.get('url') and pia:
            t['url'] = pia
        out.append(t)
    return out

def is_future(t, today='2026-06-12'):
    d = t.get('date') or ''
    return d >= today  # keep today and future

# --- merge specs: base_id, others, overrides, drop_expired ---
MERGES = [
    dict(base=617, others=[618,619], drop_expired=False,
         ov=dict(prefecture='全国',
                 venue='ＢＲＩＣＫ ＢＬＯＣＫ（大分）／日向市文化交流センター 小ホール（宮崎）／相模原メイプルホール（神奈川）',
                 dateLabel='2026年9月12日(土)大分／9月13日(日)宮崎／10月11日(日)神奈川')),
    dict(base=620, others=[621], drop_expired=False,
         ov=dict(dateLabel='2026年6月27日〜11月3日 全国ツアー')),
    dict(base=623, others=[624,625,626], drop_expired=False,
         ov=dict(prefecture='全国', venue='全国ツアー',
                 dateLabel='2026年10月〜12月 全国ツアー')),
    dict(base=627, others=[628], drop_expired=False,
         ov=dict(prefecture='全国',
                 venue='福岡市民ホール 中ホール（福岡）／ロームシアター京都 サウスホール（京都）',
                 dateLabel='2026年11月14日(土)福岡／11月29日(日)京都')),
    dict(base=632, others=[633,634,635,636,637,638,639], drop_expired=False,
         ov=dict(prefecture='全国', venue='全国ツアー',
                 dateLabel='2026年10月〜12月 全国ツアー')),
    dict(base=640, others=[641], drop_expired=False,
         ov=dict(prefecture='全国',
                 venue='サンシティ越谷市民ホール 大ホール（埼玉）／東広島芸術文化ホールくらら 大ホール（広島）',
                 dateLabel='2026年9月12日(土)埼玉／9月27日(日)広島')),
    dict(base=643, others=[644], drop_expired=False,
         ov=dict(prefecture='全国', venue='全国ツアー',
                 dateLabel='2026年10月〜11月 全国ツアー')),
    dict(base=646, others=[647], drop_expired=True,
         ov=dict(prefecture='全国', venue='全国ツアー',
                 dateLabel='2026年6月〜9月 全国ツアー', date='2026-09-18')),
    dict(base=648, others=[649], drop_expired=False,
         ov=dict(prefecture='全国', venue='仙台 ｄａｒｗｉｎ（宮城）／全国ツアー（大阪・東京）',
                 name='君島大空 夜会ツアー2026「SUPER BLUE TRANQUILIZER」',
                 dateLabel='2026年8月27日(木)宮城／9月4日(金)大阪／9月15-16日 東京')),
]

removed_ids = []
new_entry_text = {}  # base_id -> text

for mg in MERGES:
    base = dict(by_id[mg['base']])  # shallow copy
    tickets = backfill_url(by_id[mg['base']])
    for oid in mg['others']:
        tickets += backfill_url(by_id[oid])
        removed_ids.append(oid)
    if mg['drop_expired']:
        tickets = [t for t in tickets if is_future(t)]
    base.update(mg['ov'])
    base['tickets'] = tickets
    new_entry_text[mg['base']] = dump_entry(base)

# Apply replacements. Do removals and base replacement by editing text.
# Collect all spans first (on original text), then apply from end to start.
ops = []  # (start, end, replacement_or_None)
for mg in MERGES:
    s, e = find_span(text, mg['base'])
    ops.append((s, e, new_entry_text[mg['base']]))
for oid in removed_ids:
    s, e = find_span(text, oid)
    # extend to swallow trailing comma + following whitespace/newline
    j = e
    while j < len(text) and text[j] in ' \t':
        j += 1
    if j < len(text) and text[j] == ',':
        j += 1
    # also swallow the trailing newline + indent up to next entry's indent line start
    # remove following blank line(s)
    while j < len(text) and text[j] in '\r\n':
        j += 1
        break
    ops.append((s, j, None))

ops.sort(key=lambda x: x[0], reverse=True)
for s, e, rep in ops:
    if rep is None:
        # also remove leading indentation/newline before the object to avoid blank lines
        ks = s
        while ks > 0 and text[ks-1] in ' \t':
            ks -= 1
        if ks > 0 and text[ks-1] == '\n':
            ks -= 1
        text = text[:ks] + text[e:]
    else:
        text = text[:s] + rep + text[e:]

open(PATH, 'w', encoding='utf-8').write(text)
print('removed ids:', sorted(removed_ids))
print('merged bases:', [m['base'] for m in MERGES])
