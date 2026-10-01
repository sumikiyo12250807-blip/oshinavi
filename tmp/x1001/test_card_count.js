// カード丸ごとの描画でバッジ（ticket-item）が何枚出るか数える：node test_card_count.js <id,id>
const fs = require('fs'), vm = require('vm');
const src = fs.readFileSync('C:/Users/user/oshinavi/index.html', 'utf8');
let js = null; const re = /<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g; let m;
while ((m = re.exec(src))) { if (m[1].includes('const EVENTS') && m[1].includes('function renderCard')) { js = m[1]; break; } }
function stub() { let p; const h = { get(t, k) { if (k === Symbol.toPrimitive) return () => ''; if (k === Symbol.iterator) return function* () {}; if (k === 'then') return undefined; if (k === 'length') return 0; return p; }, set() { return true; }, has() { return true; }, apply() { return p; }, construct() { return p; } }; p = new Proxy(function () {}, h); return p; }
const s = stub();
const ctx = vm.createContext({ console: { log() {}, warn() {}, error() {} }, Date, Math, JSON, Object, Array, String, Number, Boolean, RegExp, Map, Set, WeakMap, Symbol, Promise, Proxy, Reflect, Error, TypeError, parseInt, parseFloat, isNaN, encodeURIComponent, decodeURIComponent, Intl, URL, URLSearchParams,
  setTimeout: () => 0, clearTimeout() {}, setInterval: () => 0, requestAnimationFrame: () => 0, queueMicrotask() {},
  document: s, localStorage: s, sessionStorage: s, fetch: s, navigator: s, location: s, history: s, performance: s, matchMedia: s, gtag: s, dataLayer: s, IntersectionObserver: s, MutationObserver: s, ResizeObserver: s, Image: s, Event: s, CustomEvent: s, HTMLElement: s, getComputedStyle: s, alert: s, confirm: s, open: s, scrollTo: s, addEventListener: s, removeEventListener: s, innerWidth: 1280, innerHeight: 800, scrollY: 0 });
ctx.window = ctx; ctx.self = ctx; ctx.globalThis = ctx;
try { new vm.Script(js).runInContext(ctx, { timeout: 600000 }); } catch (e) { }
const ids = (process.argv[2] || '').split(',').map(Number);
const out = [];
for (const id of ids) {
  const r = vm.runInContext(`(function(){const ev=EVENTS.find(e=>e.id===${id});const h=renderCard(ev);const n=(h.match(/class="ticket-item/g)||[]).length;const pe=(h.match(/先行終了/g)||[]).length;return [ev.name,ev.tickets.length,n,pe];})()`, ctx);
  out.push(`id${id} ${r[0]}：データの枠${r[1]} → 画面のバッジ${r[2]}（うち先行終了${r[3]}）`);
}
fs.writeFileSync('C:/Users/user/oshinavi/tmp/x1001/test_card_count.txt', out.join('\n'));
