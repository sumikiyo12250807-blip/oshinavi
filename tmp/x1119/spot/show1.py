import json, sys
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(open(r'C:\Users\user\oshinavi\tmp\x1119\spot\sample_1.json', encoding='utf-8'))
print(type(d), len(d))
for e in d:
    print(json.dumps(e, ensure_ascii=False, indent=0))
    print('-----')
