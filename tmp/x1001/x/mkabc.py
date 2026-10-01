"""予約JSを3段に分けて作る（本文は日本語のまま埋め込む）。python tmp/x1001/x/mkabc.py NN H M
  A: 本文欄に paste → 本文を丸ごと照合 → 🕐 を押す
  B: 予約画面の月日時分を入れて Will send on を照合 → Confirm
  C: 本文（頭の印・締めの印・見出し1回・末尾#チケット）と Will send on とボタン文字 Schedule を確かめて1回押す → トースト
  出力: tmp/x1001/x/abc_NN.txt（A/B/C を ==== で区切って並べる）"""
import io, json, sys
n, H, M = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
t = io.open(f'tmp/x1001/x/post{n}.txt', encoding='utf-8').read().replace('\r\n', '\n')
t = t.split('\n【動画】')[0].rstrip('\n') + '\n'   # 動画を付けるメモ行は本文に入れない
lines = [l for l in t.split('\n') if l.strip()]
mark = t.split('\n')[2][:14]
tailmark = lines[-3][:12]
want = 'Thu, Oct 1, 2026 at %d:%02d PM' % (H - 12, M)
A = '''const T=%s;
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const norm=s=>s.replace(/\\s+/g,'');
let box; for(let i=0;i<25&&!(box=document.querySelector('[role="dialog"] [data-testid="tweetTextarea_0"][contenteditable="true"]')||document.querySelector('[data-testid="tweetTextarea_0"][contenteditable="true"]'));i++) await sleep(300);
if(!box) throw 'NO_BOX';
if(box.innerText.trim().length>0 && norm(box.innerText)!==norm(T)) throw 'BOX_NOT_EMPTY:'+box.innerText.slice(0,40);
if(norm(box.innerText)!==norm(T)){ box.focus(); const dt=new DataTransfer(); dt.setData('text/plain',T);
box.dispatchEvent(new ClipboardEvent('paste',{clipboardData:dt,bubbles:true,cancelable:true})); await sleep(1800);}
if(norm(box.innerText)!==norm(T)) throw 'TEXT_MISMATCH len='+box.innerText.length;
let root=box; while(root&&!root.querySelector('[data-testid="scheduleOption"]')) root=root.parentElement;
if(!root) throw 'NO_ROOT'; root.querySelector('[data-testid="scheduleOption"]').click(); 'A_OK '+box.innerText.length;''' % json.dumps(t, ensure_ascii=False)
B = '''const sleep=ms=>new Promise(r=>setTimeout(r,ms));
let sels=[]; for(let i=0;i<30;i++){const dd=[...document.querySelectorAll('[role="dialog"]')].find(x=>x.innerText.includes('Will send on')); sels=dd?[...dd.querySelectorAll('select')]:[]; if(sels.length>=5) break; await sleep(300);}
if(sels.length<5) throw 'NO_SELECTS';
const setv=(s,v)=>{Object.getOwnPropertyDescriptor(Object.getPrototypeOf(s),'value').set.call(s,String(v));s.dispatchEvent(new Event('change',{bubbles:true}));};
setv(sels[0],'10'); setv(sels[1],'1'); setv(sels[3],%d); setv(sels[4],%d); await sleep(800);
const will=(document.body.innerText.match(/Will send on[^\\n]*/)||[''])[0];
if(!will.includes(%s)) throw 'WILL_MISMATCH '+will;
[...document.querySelectorAll('[role="button"],button')].find(b=>b.innerText.trim()==='Confirm').click(); await sleep(3000); 'B_OK';''' % (H, M, json.dumps(want))
C = '''const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const MARK=%s, TAILMARK=%s;
const will=(document.body.innerText.match(/Will send on[^\\n]*/)||[''])[0];
if(!will.includes(%s)) throw 'WILL '+will;
const box=[...document.querySelectorAll('[data-testid="tweetTextarea_0"]')].find(b=>b.innerText.includes(MARK));
if(!box) throw 'NO_BOX';
if(!box.innerText.includes(TAILMARK)) throw 'NO_TAILMARK';
if((box.innerText.match(/ピックアップ🎫/g)||[]).length!==1) throw 'HEAD_COUNT';
if(!box.innerText.trim().endsWith('#チケット')) throw 'TAIL';
let r2=box; while(r2&&!r2.querySelector('[data-testid="tweetButton"],[data-testid="tweetButtonInline"]')) r2=r2.parentElement;
const btn=r2&&r2.querySelector('[data-testid="tweetButton"],[data-testid="tweetButtonInline"]');
if(!btn||btn.innerText.trim()!=='Schedule') throw 'BTN '+(btn&&btn.innerText);
btn.click(); await sleep(3000);
'DONE | '+[...document.querySelectorAll('[data-testid="toast"],[role="alert"]')].map(t=>t.innerText).join(' | ')+' | url='+location.href;''' % (
    json.dumps(mark, ensure_ascii=False), json.dumps(tailmark, ensure_ascii=False), json.dumps(want))
io.open(f'tmp/x1001/x/abc_{n}.txt', 'w', encoding='utf-8').write(A + '\n====\n' + B + '\n====\n' + C + '\n')
print(n, want, 'mark ok' if mark and tailmark else 'NG')
