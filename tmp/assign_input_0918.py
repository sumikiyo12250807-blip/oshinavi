# -*- coding: utf-8 -*-
# 振り分けの検証用＝ぴあ由来の新着プールを「判定案を伏せて」一覧にする
import re, json, io
h = open('index.html', encoding='utf-8', newline='').read()
ev = json.loads(re.search(r'const EVENTS = (\[.*?\]);', h, re.S).group(1))
new = [e for e in ev if e.get('genre') == 'new']

pia, nonpia = [], []
for e in sorted(new, key=lambda x: x['id']):
    L = e.get('links') or {}
    vends = [k for k in ('pia', 'rakuten', 'lawson', 'eplus') if L.get(k)]
    (pia if vends == ['pia'] else nonpia).append((e, vends))

# エージェントに渡す＝ジャンルの判定案（_genre）は入れない
q = io.open('tmp/assign_question_0918.txt', 'w', encoding='utf-8')
q.write(f"ぴあ由来の新着プール {len(pia)}件（判定案は伏せてある）\n")
q.write("形式: id / ぴあのカテゴリ（_piaSub） / 公演名 / 会場 / 公演日\n\n")
for e, v in pia:
    q.write(f"id{e['id']}\t{e.get('_piaSub') or '(空)'}\t{e.get('artist','')[:60]}\t{e.get('venue','')[:30]}\t{e.get('date','')}\n")
q.close()

# あたしの判定案（照合用・エージェントには渡さない）
mine = io.open('tmp/assign_mine_0918.txt', 'w', encoding='utf-8')
for e, v in pia:
    mine.write(f"id{e['id']}\t{e.get('_genre')}\t{e.get('_extraGenres')}\t{e.get('_piaSub')}\n")
mine.close()

npf = io.open('tmp/assign_nonpia_0918.txt', 'w', encoding='utf-8')
npf.write(f"ぴあ以外 {len(nonpia)}件（振り分けはユーザー確認後＝プールに残す）\n")
for e, v in nonpia:
    L = e.get('links') or {}
    url = next((L[k] for k in ('rakuten', 'lawson', 'eplus', 'pia') if L.get(k)), '')
    npf.write(f"id{e['id']}\t{'+'.join(v) or 'なし'}\t{e.get('artist','')[:46]}\t{e.get('venue','')[:26]}\t公演{e.get('date','')}\n  {url}\n")
npf.close()
print('pia', len(pia), 'nonpia', len(nonpia))
