# -*- coding: utf-8 -*-
"""既存DBの機械的に直せる2件を修正（表示フィールドは触らない・最小変更）
 A Amazonリンクの検索クエリ k= を半角化（全角のままだと検索0件＝リンクが死ぬ）
 C 券種名の余計なピリオド「一般発売.」→「一般発売」
"""
import io, json, re, sys, urllib.parse, unicodedata, datetime
sys.path.insert(0, 'tools')
from build_pia_entries import norm_fw

h = io.open('index.html', encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in h else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

FW = re.compile(r'[Ａ-Ｚａ-ｚ０-９．－]')
log = []
for ev in EVENTS:
    lk = ev.get('links') or {}
    amz = lk.get('amazon')
    if amz:
        mk = re.search(r'([?&]k=)([^&]+)', amz)
        if mk:
            kw = urllib.parse.unquote(mk.group(2))
            if FW.search(kw):
                kw2 = norm_fw(kw)
                if kw2 != kw:
                    lk['amazon'] = amz[:mk.start(2)] + urllib.parse.quote(kw2) + amz[mk.end(2):]
                    log.append('A id=%s %s → %s' % (ev['id'], kw, kw2))
    for t in ev.get('tickets', []):
        ty = t.get('type') or ''
        new = re.sub(r'(一般発売|一般販売|先行|当日券)\.', r'\1', ty)
        if new != ty:
            t['type'] = new
            log.append('C id=%s %s → %s' % (ev['id'], ty, new))

bak = 'index.html.bak_%s_legacy_fix' % datetime.date.today().strftime('%m%d')
io.open(bak, 'w', encoding='utf-8', newline='').write(h)
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
io.open('index.html', 'w', encoding='utf-8', newline='').write(
    h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])

io.open('tmp/out_fix_legacy_0730.txt', 'w', encoding='utf-8').write('\n'.join(log))
na = len([x for x in log if x.startswith('A ')])
nc = len([x for x in log if x.startswith('C ')])
print('Amazon %d件 / ピリオド %d件 修正 (backup %s)' % (na, nc, bak))
