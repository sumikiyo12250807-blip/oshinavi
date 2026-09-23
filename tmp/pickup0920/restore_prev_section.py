# 9/20号は日曜朝に公開（ユーザー指示）＝土曜の昼・夜のpushで出ないよう、index.html の記事の段だけ公開中の版（origin/main）に戻す
import io, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
live = subprocess.run(['git', 'show', 'origin/main:index.html'], capture_output=True).stdout.decode('utf-8')
i = live.index('<section class="pickup"')
j = live.index('</section>', i) + len('</section>')
old = live[i:j].replace('\r\n', '\n')
src = io.open('index.html', encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in src else '\n'
a = src.index('<section class="pickup"')
b = src.index('</section>', a) + len('</section>')
out = src[:a] + old.replace('\n', nl) + src[b:]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
print('戻した（公開中の版）', '9/14(月)〜9/20(日)' in old)
