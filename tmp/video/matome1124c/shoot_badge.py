# -*- coding: utf-8 -*-
# 「バッジをタップ」の場面用＝10/27発売のお笑い＝神田伯山一門会（28404・一般発売 10/27 10:00）のカードを、スマホの幅（487px・2倍）の本物の画面で撮る
#   matome1024j/shoot_badge.py の写し（CID・Q・MD・前の夜の時計だけ差し替え）。10/26 を含む箱（.ticket-item）の位置も測る
#   🚨 index.html には書かない（flash_storyboard.local_page の写しを撮るだけ）。測る時と撮る時は同じ窓の大きさ
import io, json, os, re, subprocess, sys, urllib.parse
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, 'C:/Users/user/oshinavi/tools')
os.chdir('C:/Users/user/oshinavi')
import flash_storyboard as F
from PIL import Image
D = 'tmp/video/matome1124c/cards/'
os.makedirs(D, exist_ok=True)
CID, Q, MD = 53841, 'N響大河ドラマ', '11/24'   # 11/17 尾崎裕哉Concert2027（一般発売（東京 R9年 3/14公演）11/17 10:00発売・板橋区立文化会館 大ホール）
WW, HH, S = 487, 2600, 2
url0 = F.local_page(['.ad-band', '.pickup', '#pickup', '.affiliate', 'iframe', '.promo'], D)
base = io.open(url0[8:], encoding='utf-8').read()
chrome = next(p for p in F.CHROME_CANDIDATES if os.path.exists(p))
js = """<script>(function(){var n=0;var iv=setInterval(function(){n++;
var c=document.querySelector('.event-card[data-id="%d"]');
if(!c&&n<80)return;clearInterval(iv);
document.querySelectorAll('.event-card').forEach(function(e){if(e!==c)e.style.display='none';});
if(!c)return;
var y0=window.scrollY,r=c.getBoundingClientRect(),out=[Math.round(r.top+y0),Math.round(r.height)];
c.querySelectorAll('.ticket-item').forEach(function(t){if((t.innerText||'').indexOf('%s')>=0){var b=t.getBoundingClientRect();
out=out.concat([Math.round(b.left),Math.round(b.top+y0),Math.round(b.width),Math.round(b.height)]);}});
document.documentElement.setAttribute('data-cardpos',out.join(','));
},100);})();</script>""" % (CID, MD)
h = base.replace('</body>', js + '</body>', 1)
# 撮るのは前の日＝X に出る 10/25 の夜の「明日発売」で写すため、画面の時計だけ 10/25 20:00 にする
FAKE = "<script>(function(){var D=Date,T=new D(2026,10,21,20,0).getTime();function F(){return arguments.length?new (Function.prototype.bind.apply(D,[null].concat([].slice.call(arguments))))():new D(T);}F.now=function(){return T;};F.prototype=D.prototype;F.UTC=D.UTC;F.parse=D.parse;window.Date=F;})();</script>"
h = h.replace('<head>', '<head>' + FAKE, 1)
p = os.path.abspath(D + 'shot_badge.html')
io.open(p, 'w', encoding='utf-8').write(h)
url = 'file:///' + p.replace('\\', '/') + '?q=' + urllib.parse.quote(Q)
r = subprocess.run([chrome, '--headless=new', '--window-size=%d,%d' % (WW, HH), '--virtual-time-budget=15000', '--dump-dom', url],
                   timeout=240, capture_output=True, text=True, encoding='utf-8', errors='replace')
v = [int(x) for x in re.search(r'data-cardpos="([\d,]+)"', r.stdout).group(1).split(',')]
top = v[0]
boxes = [v[i:i + 4] for i in range(2, len(v), 4)]
full = os.path.abspath(D + 'full_badge.png')
subprocess.run([chrome, '--headless=new', '--hide-scrollbars', '--window-size=%d,%d' % (WW, HH), '--force-device-scale-factor=%d' % S,
                '--virtual-time-budget=15000', '--screenshot=' + full, url], timeout=240, capture_output=True)
im = Image.open(full).convert('RGB')
HEAD = 70 * S
need = int(round(1920 * im.width / 1080))
a = (max(top - 20, boxes[0][1] - 380) if boxes else top - 20) * S   # 11/18 先行の枠が上に5つ並ぶカード＝11/18 発売のバッジが画面の外に出た → バッジが画面の4割あたりに来るよう下へずらす
head = im.crop((0, 0, im.width, HEAD))
body = im.crop((0, a, im.width, a + need - HEAD))
out = Image.new('RGB', (im.width, need), (10, 10, 10))
out.paste(head, (0, 0)); out.paste(body, (0, HEAD))
out = out.resize((1080, 1920), Image.LANCZOS)
out.save(D + 'screen_badge.png')
k = 1080 / im.width
bx = [[round(x * S * k), round((HEAD + y * S - a) * k), round((x + w) * S * k), round((HEAD + (y + hh) * S - a) * k)] for x, y, w, hh in boxes]
json.dump({'boxes': bx}, io.open(D + 'screen_badge.json', 'w'))
print('ok top', top, 'boxes', bx, 'full', im.size)
