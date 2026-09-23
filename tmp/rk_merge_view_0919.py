# 足し込み先の既存エントリの枠を見る（楽天の枠と同じ県・公演日の枠が既にあるか）
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
h = open('index.html', encoding='utf-8').read()
E = {e['id']: e for e in json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\n\]);', h, re.S).group(1))}
pairs = {'GLAY': (4436, '福岡'), 'さだ': (1, '大阪'), 'ラフ': (7502, '東京'), 'アニー': (7886, '東京'),
         'DOC': (1722, ''), 'DOI': (52, '千葉')}
for k, (i, pref) in pairs.items():
    e = E[i]
    print(f"■ id{i} {e['name'][:40]} genre={e['genre']} 枠{len(e['tickets'])}")
    for t in e['tickets']:
        if pref in t['type'] or not pref:
            u = t.get('url', '')
            print('    ', t['type'][:60], '|', t.get('date'), '|', 'rakuten' if 'rakuten' in u else u[:45])
