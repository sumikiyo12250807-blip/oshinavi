# -*- coding: utf-8 -*-
"""pia_days_list.py の結果（eventCdで見て「その日の枠なし」）を、名前＋県＋発売日でもう一度確かめて、
本当に抜けているものだけを出す（読むだけ）。統合で別URLのまま入っている枠を「抜け」と数えないため。
使い方: python tmp/x0912/true_missing.py tmp/x0912/pia_days_01.txt
出力: 画面 ＋ tmp/x0912/true_missing_<lg>.json（url・どのエントリに足すか）"""
import io, json, re, sys, unicodedata
sys.stdout.reconfigure(encoding='utf-8')
SRC = sys.argv[1]
lg = re.search(r'pia_days_(\d+)', SRC).group(1)


def n(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s　・／/&＆\-‐―〜～!！?？「」『』【】（）()]', '', s).lower()


PREFS = '北海道 青森 岩手 宮城 秋田 山形 福島 茨城 栃木 群馬 埼玉 千葉 東京 神奈川 新潟 富山 石川 福井 山梨 長野 岐阜 静岡 愛知 三重 滋賀 京都 大阪 兵庫 奈良 和歌山 鳥取 島根 岡山 広島 山口 徳島 香川 愛媛 高知 福岡 佐賀 長崎 熊本 大分 宮崎 鹿児島 沖縄'.split()
src = open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
rows = []
for ln in io.open(SRC, encoding='utf-8'):
    m = re.match(r'^\s+(2026-\d\d-\d\d) (.+?) \| (.+?) \| (.+?) \| (.+)$', ln.rstrip('\n'))
    if m:
        rows.append(m.groups())
out = []
for iso, artist, saletype, venue, tail in rows:
    prefs = [p for p in PREFS if p in venue]
    key = n(artist)
    cands = [e for e in ev if key and (key in n(e.get('artist')) or key in n(e.get('name')))]
    found = False
    for e in cands:
        for t in e.get('tickets') or []:
            if t.get('startDate') == iso and any(p in (t.get('type') or '') for p in prefs):
                found = True
    url = re.search(r'(https://\S+)', tail)
    idm = re.search(r'id(\d+)', tail)
    if not found:
        tgt = int(idm.group(1)) if idm else (cands[0]['id'] if len(cands) == 1 else None)
        out.append({'date': iso, 'artist': artist, 'saletype': saletype, 'venue': venue, 'prefs': prefs,
                    'url': url.group(1) if url else None, 'target': tgt,
                    'cands': [c['id'] for c in cands][:6]})
print('確かめた %d件 → 本当に抜けている %d件' % (len(rows), len(out)))
for o in out:
    print('  %s %s | %s | %s | 足す先=%s 候補=%s %s' % (o['date'], o['artist'], o['saletype'], '・'.join(o['prefs']),
          o['target'], o['cands'], o['url'] or ''))
json.dump(out, io.open('tmp/x0912/true_missing_%s.json' % lg, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
