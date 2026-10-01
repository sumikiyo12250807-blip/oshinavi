// 日付検索の試し：index.html の本体スクリプトを vm で動かし、searchQuery に日付を入れて matchEvent で何件出るか数える
const fs = require('fs'), vm = require('vm');
const src = fs.readFileSync('C:/Users/user/oshinavi/index.html', 'utf8');
let js = null; const re = /<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g; let m;
while ((m = re.exec(src))) { if (m[1].includes('const EVENTS') && m[1].includes('function matchEvent')) { js = m[1]; break; } }
function stub() { let p; const h = { get(t, k) { if (k === Symbol.toPrimitive) return () => ''; if (k === Symbol.iterator) return function* () {}; if (k === 'then') return undefined; if (k === 'length') return 0; return p; }, set() { return true; }, has() { return true; }, apply() { return p; }, construct() { return p; } }; p = new Proxy(function () {}, h); return p; }
const s = stub();
const ctx = vm.createContext({ console: { log() {}, warn() {}, error() {} }, Date, Math, JSON, Object, Array, String, Number, Boolean, RegExp, Map, Set, WeakMap, Symbol, Promise, Proxy, Reflect, Error, TypeError, parseInt, parseFloat, isNaN, encodeURIComponent, decodeURIComponent, Intl, URL, URLSearchParams,
  setTimeout: () => 0, clearTimeout() {}, setInterval: () => 0, requestAnimationFrame: () => 0, queueMicrotask() {},
  document: s, localStorage: s, sessionStorage: s, fetch: s, navigator: s, location: s, history: s, performance: s, matchMedia: s, gtag: s, dataLayer: s, IntersectionObserver: s, MutationObserver: s, ResizeObserver: s, Image: s, Event: s, CustomEvent: s, HTMLElement: s, getComputedStyle: s, alert: s, confirm: s, open: s, scrollTo: s, addEventListener: s, removeEventListener: s, innerWidth: 1280, innerHeight: 800, scrollY: 0 });
ctx.window = ctx; ctx.self = ctx; ctx.globalThis = ctx;
try { new vm.Script(js).runInContext(ctx, { timeout: 600000 }); } catch (e) { }
const out = [];
for (const q of ['10/12', '10/12発売', '10/12公演', '10月12日', '10/5', 'GLAY']) {
  const r = vm.runInContext(`activeGenre='all';activeStatus='all';activeRegion='all';searchQuery=${JSON.stringify(q)};(function(){const _r=EVENTS.filter(matchEvent);return [_r.length,_r.slice(0,6).map(e=>e.id+' '+(e.name||'').slice(0,24)+' | '+(e.dateLabel||'').slice(0,26))];})()`, ctx);
  out.push(`「${q}」→ ${r[0]}件\n   ` + r[1].join('\n   '));
}
fs.writeFileSync('C:/Users/user/oshinavi/tmp/x1001/test_date_search.txt', out.join('\n'));
