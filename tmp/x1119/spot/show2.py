import json
d = json.load(open(r'C:\Users\user\oshinavi\tmp\x1119\spot\sample_2.json', encoding='utf-8'))
with open(r'C:\Users\user\oshinavi\tmp\x1119\spot\sample_2_view.txt', 'w', encoding='utf-8') as f:
    for e in d:
        e2 = dict(e)
        e2.get('links', {}).pop('amazon', None)
        f.write(json.dumps(e2, ensure_ascii=False, indent=1) + '\n---\n')
