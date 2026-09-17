import json, re, sys, io, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ids = [int(x) for x in sys.argv[1].split(',')]
ref = sys.argv[2] if len(sys.argv) > 2 else None
def load(txt):
    return {e['id']: e for e in json.loads(re.search(r'const EVENTS\s*=\s*(\[[\s\S]*?\]);', txt).group(1))}
cur = load(open('index.html', encoding='utf-8').read())
old = load(subprocess.run(['git', 'show', f'{ref}:index.html'], capture_output=True).stdout.decode('utf-8')) if ref else {}
for i in ids:
    for label, db in (('HEAD', old), ('いま', cur)):
        if i not in db: continue
        print(f'--- id{i} {label} {db[i].get("artist")}')
        for t in db[i].get('tickets', []):
            flags = ' '.join(k for k in ('soldout', 'saleEnded', 'saleEndUnknown') if t.get(k))
            print(f'   {t.get("type")} | date={t.get("date")} start={t.get("startDate","")} {flags} | {t.get("url","")[-40:]}')
