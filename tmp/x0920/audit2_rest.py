# 総ざらい2本め（tmp/x0920/audit_posts2.txt）の本命のうち、まだ足していないもの＝いま売っている公演を組み立て候補にする
#  新日本プロレス（済）・新喜劇出前ツアー長崎（登録済みの枠）は外す。同名の既存が1つなら足し込み、無ければ新規
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
h = io.open('index.html', encoding='utf-8', newline='').read()
EV = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))
txt = io.open('tmp/x0920/audit_posts2.txt', encoding='utf-8').read().split('別名義・フェス出演の候補')[0]
SKIP_URL = {'https://ticket.pia.jp/pia/event.do?eventCd=2633600', 'https://ticket.pia.jp/pia/event.do?eventCd=2633661',
            'https://ticket.pia.jp/pia/event.do?eventCd=2637320'}
rows = re.findall(r'\[(.*?)\] (.*?)\n\s+公演日: .*?\n(?:\s+発売日: .*?\n)?\s+URL\s*:\s*(\S+)', txt)
merge, new = {}, {}
for kind, title, url in rows:
    if url in SKIP_URL:
        continue
    title = title.strip()
    hits = [e for e in EV if e.get('genre') != 'new' and (e.get('artist') or '').strip() == title]
    if len(hits) == 1:
        e = hits[0]
        d = merge.setdefault(e['id'], {'newid': e['id'], 'artist': e['artist'],
                                       'urls': [u for u in dict.fromkeys([(e.get('links') or {}).get('pia')] + [t.get('url') for t in e['tickets']]) if u and 'pia.jp' in u and 'w.pia.jp' not in u]})
        if url not in d['urls']:
            d['urls'].append(url)
    else:
        d = new.setdefault(url, {'newid': 90300 + len(new), 'artist': title, 'urls': [url]})
json.dump(list(merge.values()), io.open('tmp/x0920/cands_a2_merge.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(list(new.values()), io.open('tmp/x0920/cands_a2_new.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('足し込み', [d['artist'] for d in merge.values()])
print('新規', [d['artist'][:30] for d in new.values()])
