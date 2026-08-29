// index.html の renderCard を「写経せず実物のまま」動かして、画面に何が出るかを見る。
const fs=require('fs');
const src=fs.readFileSync('index.html','utf8');
const ev=JSON.parse(src.match(/  const EVENTS = (\[[\s\S]*?\]);/)[1]);
const blocks=[...src.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]);
const blk=blocks.find(b=>b.includes('function renderCard'));
if(!blk){console.log('renderCard を含む script が見つからない');process.exit(1)}

const stub=`
function El(){return new Proxy({},{get(t,k){
  if(k==='style')return {};
  if(k==='classList')return {add(){},remove(){},toggle(){},contains(){return false}};
  if(k==='dataset')return {};
  if(k==='children'||k==='childNodes')return [];
  if(k==='value'||k==='innerHTML'||k==='textContent')return '';
  if(k==='parentNode'||k==='firstChild'||k==='nextElementSibling')return El();
  if(typeof k==='symbol')return undefined;
  return function(){return El()};
},set(){return true}})}
var document={getElementById:()=>El(),querySelector:()=>El(),querySelectorAll:()=>[],
  addEventListener:()=>{},createElement:()=>El(),createTextNode:()=>El(),
  documentElement:El(),body:El(),head:El(),readyState:'complete'};
var window={addEventListener:()=>{},removeEventListener:()=>{},
  location:{href:'',search:'',hash:'',pathname:'/'},
  matchMedia:()=>({matches:false,addEventListener(){},addListener(){}}),
  localStorage:{getItem:()=>null,setItem:()=>{},removeItem:()=>{}},
  scrollTo:()=>{},scrollY:0,innerWidth:1200,innerHeight:800,
  requestAnimationFrame:()=>0,setTimeout:()=>0,history:{replaceState(){},pushState(){}}};
var localStorage=window.localStorage;
var navigator={userAgent:'node'};
var alert=()=>{};
var IntersectionObserver=function(){return {observe(){},unobserve(){},disconnect(){}}};
var gtag=function(){};
var __err=null;
try{
`;
const tail=`
}catch(e){__err=e.message}
return {renderCard:typeof renderCard!=="undefined"?renderCard:null,
        EVENTS:typeof EVENTS!=="undefined"?EVENTS:null, err:__err};
`;
let out;
try{ out=new Function(stub+blk+tail)(); }
catch(e){ console.log('評価エラー:',e.message); process.exit(1); }
if(out.err) console.log('(初期化は途中で止まった: '+out.err+') → renderCard 取得: '+!!out.renderCard);
if(!out.renderCard){console.log('renderCard を取り出せなかった');process.exit(1)}

const ids=process.argv.slice(2).map(Number);
for(const id of (ids.length?ids:[5432])){
  const e=(out.EVENTS||ev).find(x=>x.id===id);
  const html=out.renderCard(e);
  require('fs').writeFileSync('tmp/card_'+id+'.html',html,'utf8');
  console.log('id='+id+' HTML長 '+html.length+' → tmp/card_'+id+'.html');
}
