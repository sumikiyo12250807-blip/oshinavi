# 9/20号の主役5組＋深掘りの「登録データ」を書き出す（9/21〜9/27に発売が始まる枠に★）
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
h = open('index.html', encoding='utf-8').read()
E = json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\n\]);', h, re.S).group(1))
KEYS = ['アイカツスターズ', '角野隼斗', '矢野顕子', '反田恭平', '斉藤和義', 'ウインドオーケストラ']
out = []
for k in KEYS:
    hits = [e for e in E if k in (e.get('name') or '') or k in (e.get('artist') or '')]
    out.append(f'## {k}（{len(hits)}エントリ）')
    for e in hits:
        out.append(f"- id{e['id']} [{e['genre']}] {e['name']} ／ {e.get('dateLabel')} ／ {e.get('venue')}")
        for t in e['tickets']:
            sd = t.get('startDate') or ''
            star = '★' if '2026-09-21' <= sd <= '2026-09-27' else '  '
            flags = ' 売切' if t.get('soldout') else ''
            out.append(f"    {star} {t['type']} | 締切{t.get('date')} 発売{sd}{flags} | {t.get('url', '')}")
open('tmp/pickup0920/reg_main.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('\n'.join(out))
