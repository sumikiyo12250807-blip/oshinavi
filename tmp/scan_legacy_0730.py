# -*- coding: utf-8 -*-
"""今日見つけた2バグの既存DB被害を洗う
 A Amazonリンクのクエリが全角のまま（検索0件＝リンクが死んでいる）
 B 同一エントリ内で ticket.type が完全重複（席種ラベルが落ちて1枠に潰れて見える）
 C 券種名の余計なピリオド「一般発売.」
"""
import io, json, re, urllib.parse, collections

raw = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[.*?\]);', raw, re.S)
ALL = json.loads(m.group(1))

FW = re.compile(r'[Ａ-Ｚａ-ｚ０-９．－]')
A, B, C = [], [], []
for ev in ALL:
    amz = (ev.get('links') or {}).get('amazon')
    if amz:
        m2 = re.search(r'[?&]k=([^&]+)', amz)
        kw = urllib.parse.unquote(m2.group(1)) if m2 else ''
        if FW.search(kw):
            A.append((ev['id'], ev.get('artist'), kw))
    tys = [t.get('type') for t in ev.get('tickets', [])]
    dup = [k for k, v in collections.Counter(tys).items() if v > 1]
    if dup:
        B.append((ev['id'], ev.get('artist'), dup))
    for ty in tys:
        if ty and re.search(r'(発売|販売|先行|当日券)\.', ty):
            C.append((ev['id'], ev.get('artist'), ty))

out = []
out.append('■A Amazonリンクが全角クエリ: %d件' % len(A))
for i, a, kw in A[:60]:
    out.append('   id=%s %s | k=%s' % (i, a, kw))
if len(A) > 60:
    out.append('   …ほか %d件' % (len(A) - 60))
out.append('')
out.append('■B 同一エントリ内で券種名が完全重複: %d件' % len(B))
for i, a, dup in B[:60]:
    out.append('   id=%s %s | %s' % (i, a, dup))
if len(B) > 60:
    out.append('   …ほか %d件' % (len(B) - 60))
out.append('')
out.append('■C 券種名に余計なピリオド: %d件' % len(C))
for i, a, ty in C[:40]:
    out.append('   id=%s %s | %s' % (i, a, ty))
if len(C) > 40:
    out.append('   …ほか %d件' % (len(C) - 40))

io.open('tmp/out_legacy_0730.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('A=%d B=%d C=%d → tmp/out_legacy_0730.txt' % (len(A), len(B), len(C)))
