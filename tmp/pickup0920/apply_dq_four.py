# 深掘りの「年末年始4公演の段」（2つ目の「公式の言葉はこうよ。」〜「…公式にはまだ出ていないわ。」）を、書き直した版に差し替える
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
p = 'tmp/pickup0920/draft.md'
s = io.open(p, encoding='utf-8').read()
new = io.open('tmp/pickup0920/dq_tone_four.md', encoding='utf-8').read().rstrip('\n') + '\n'
deep = s.index('## 深掘り')
i = s.index('公式の言葉はこうよ。\n「あの感動が蘇る！」', deep)
end_mark = '年末年始公演のくわしい曲目と曲順は、公式にはまだ出ていないわ。\n'
j = s.index(end_mark, i) + len(end_mark)
s = s[:i] + new + s[j:]
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
