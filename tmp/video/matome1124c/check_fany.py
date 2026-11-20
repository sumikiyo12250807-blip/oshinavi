# -*- coding: utf-8 -*-
# 41806 の FANY 受付ページから受付期間・公演日の文を抜く（確かめるだけ）
import io, re, urllib.request, html
u = 'https://ticket.fany.lol/reception/72308/56917'
req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
b = urllib.request.urlopen(req, timeout=40).read().decode('utf-8', 'replace')
t = html.unescape(re.sub(r'<[^>]+>', ' ', re.sub(r'(?s)<script.*?</script>|<style.*?</style>', ' ', b)))
t = re.sub(r'\s+', ' ', t)
hits = []
for m in re.finditer(r'2026[/年.]\s*1[12][/月.]\s*\d{1,2}[^ ]{0,30}', t):
    hits.append(t[max(0, m.start() - 80):m.end() + 60])
io.open('C:/Users/user/oshinavi/tmp/video/matome1124c/check_fany.txt', 'w', encoding='utf-8').write('\n'.join(hits[:12]) or t[:3000])
