import re, sys, html
sys.stdout.reconfigure(encoding='utf-8')
for c in ['b2670957', 'b2669875', 'b2670960']:
    t = open(f'C:/Users/user/oshinavi/tmp/pia_chk_{c}.html', encoding='utf-8', errors='replace').read()
    t = re.sub(r'<script.*?</script>', ' ', t, flags=re.S)
    t = re.sub(r'<style.*?</style>', ' ', t, flags=re.S)
    txt = html.unescape(re.sub(r'<[^>]+>', '\n', t))
    lines = [l.strip() for l in txt.split('\n') if l.strip()]
    print('=' * 20, c, len(lines))
    print('\n'.join(lines))
