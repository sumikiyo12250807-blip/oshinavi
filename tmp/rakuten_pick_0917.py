import json, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
data = json.load(open('tmp/rakuten_presale.json', encoding='utf-8'))
print('keys', list(data.keys()) if isinstance(data, dict) else 'list')
items = data if isinstance(data, list) else (data.get('presale') or data.get('items'))
pick = [it for it in items if 'rtep121' in it.get('url', '')]
json.dump(pick, open('tmp/rakuten_fresh_0917.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(pick, ensure_ascii=False, indent=1)[:3000])
html = open('index.html', encoding='utf-8').read()
ids = [int(x) for x in re.findall(r'"id":\s*(\d+)', html)]
lb = json.load(open('.claude/state/last_batch.json', encoding='utf-8'))
print('max id index', max(ids), 'max id_to last_batch', max(b['id_to'] for b in lb['batches']))
