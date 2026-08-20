# -*- coding: utf-8 -*-
"""①Amazonが機械アクセスを許すか1本だけ試す ②クエリにイベント名が混入して
   「CDがヒットしない」疑いのあるリンクを全DBから洗う（memoryの既知バグ・未実装分）"""
import io, json, re, urllib.parse, urllib.request

# ① 実アクセス（1本だけ。memoryには「503でブロック」とあるが25日前の情報なので確認）
probe = 'https://www.amazon.co.jp/s?k=%E5%B2%A9%E5%B4%8E%E5%AE%8F%E7%BE%8E%20CD&i=specialty-aps'
try:
    req = urllib.request.Request(probe, headers={'User-Agent': 'Mozilla/5.0'})
    r = urllib.request.urlopen(req, timeout=20)
    body = r.read().decode('utf-8', 'replace')
    print('probe: HTTP %s / %d bytes' % (r.status, len(body)))
    print('  「該当する商品はありません」= %s' % ('該当する商品はありません' in body))
    print('  結果件数らしき表記: %s' % re.findall(r'([0-9,]+)\s*件の結果', body)[:2])
except Exception as ex:
    print('probe: ブロック or 失敗 → %s' % str(ex)[:120])

# ② イベント名混入の疑い（CD検索が成立しないクエリ）
EVENT_RE = re.compile(r'コンサート|リサイタル|演奏会|フェスティバル|フェス|記念|周年|第[0-9０-９]+回|'
                      r'公演|ツアー|ライブ|LIVE|祭|展|EXPO|大会|シリーズ|定期|ガラ|まつり|'
                      r'イン・|プロジェクト|教室|ショー')
raw = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[.*?\]);', raw, re.S)
ALL = json.loads(m.group(1))

sus, ok = [], 0
for ev in ALL:
    amz = (ev.get('links') or {}).get('amazon')
    if not amz:
        continue
    mk = re.search(r'[?&]k=([^&]+)', amz)
    kw = urllib.parse.unquote(mk.group(1)) if mk else ''
    if EVENT_RE.search(kw):
        sus.append((ev['id'], ev.get('genre'), kw, ev.get('name')))
    else:
        ok += 1

out = ['■Amazonリンク総数: %d件（クエリが素直＝%d件 / イベント名混入の疑い＝%d件）'
       % (ok + len(sus), ok, len(sus))]
for i, g, kw, nm in sus:
    out.append('  id=%s [%s] k=%s' % (i, g, kw))
io.open('tmp/out_amazon_sus_0730.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('疑い %d / 素直 %d → tmp/out_amazon_sus_0730.txt' % (len(sus), ok))
