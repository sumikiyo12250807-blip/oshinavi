# 深掘りの頭（見出しの次〜最初の「公式の言葉はこうよ。」の前）を、ユーザーの書き出しの調子で書き直した版に差し替える
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
p = 'tmp/pickup0920/draft.md'
s = io.open(p, encoding='utf-8').read()
head = io.open('tmp/pickup0920/dq_tone_head.md', encoding='utf-8').read().rstrip('\n') + '\n'
t = '**「ドラゴンクエスト」ウインドオーケストラコンサート——12/30と1/1、「I〜IX」9つの物語を4公演で**\n\n'
i = s.index(t) + len(t)
j = s.index('公式の言葉はこうよ。\n「あの感動が蘇る！」', i)
s = s[:i] + head + '\n' + s[j:]
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
