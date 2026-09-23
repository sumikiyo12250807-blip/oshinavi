# 怪談らしいエントリを探す（genre が kaidan でも extraGenres に kaidan があるものでもない分）
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
E = json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\n\]);', open('index.html', encoding='utf-8').read(), re.S).group(1))
KW = re.compile(r'怪談|怪異|怖い話|怖語|こわ|コワ|ホラー|心霊|恐怖|オカルト|怪奇|百物語|稲川淳二|怪の|の怪|怪〜|怪～|怪\)|都市伝説|呪|祟')
for e in E:
    g = e.get('genre')
    if g == 'kaidan' or 'kaidan' in (e.get('extraGenres') or []):
        continue
    txt = (e.get('name') or '') + ' ' + (e.get('artist') or '')
    m = KW.search(txt)
    if m:
        print('%s\t%s\t[%s]\t%s' % (e['id'], g, m.group(0), txt[:90]))
print('--- 既に怪談', sum(1 for e in E if e.get('genre') == 'kaidan' or 'kaidan' in (e.get('extraGenres') or [])))
