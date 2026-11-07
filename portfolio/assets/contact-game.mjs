import {scenes,inside,decodeDestination} from './contact-scenes.mjs';
const world=document.querySelector('#world'),item=document.querySelector('#world-item'),drop=document.querySelector('#world-target'),entrance=document.querySelector('#world-entrance'),status=document.querySelector('#contact-status');
let index=0,phase='idle',selected=false,destination=null,generation=0,drag=null,suppressClick=false,timer;
let idleTimer,audioContext,soundEnabled=true;
function audioReady(){
 if(!soundEnabled)return;
 try{const Audio=window.AudioContext||window.webkitAudioContext;if(!Audio)return;audioContext??=new Audio();if(audioContext.state==='suspended')audioContext.resume().catch(()=>{});}catch{}
}
function tone(frequency,when,duration,volume=.045){
 if(!soundEnabled||!audioContext||audioContext.state!=='running')return;
 const osc=audioContext.createOscillator(),gain=audioContext.createGain();osc.type='triangle';osc.frequency.value=frequency;
 gain.gain.setValueAtTime(0,when);gain.gain.linearRampToValueAtTime(volume,when+.012);gain.gain.exponentialRampToValueAtTime(.001,when+duration);
 osc.connect(gain);gain.connect(audioContext.destination);osc.start(when);osc.stop(when+duration+.02);osc.onended=()=>{osc.disconnect();gain.disconnect();};
}
function effect(kind){
 if(!soundEnabled||!audioContext)return;const t=audioContext.currentTime+.02;
 if(kind==='pick'){tone(440,t,.09);tone(660,t+.06,.1,.025);}
 if(kind==='place'){tone(330,t,.13,.035);}
 if(kind==='success'){[523.25,659.25,783.99,1046.5].forEach((f,i)=>tone(f,t+i*.12,.28,.045));tone(523.25,t+.48,.5,.025);tone(783.99,t+.48,.5,.025);}
}
function scheduleHint(){
 clearTimeout(idleTimer);status.textContent='';const token=generation;
 if(phase==='opening'||document.hidden)return;
 idleTimer=setTimeout(()=>{if(token!==generation||document.hidden)return;status.textContent=phase==='cleared'&&destination?'クリックして先へ進もう':phase==='idle'?'道はこの絵の中にある':status.textContent;},phase==='cleared'?8000:12000);
}
document.querySelector('.contact-game').addEventListener('pointerdown',()=>{audioReady();scheduleHint();});
document.querySelector('.contact-game').addEventListener('keydown',()=>{audioReady();scheduleHint();});
document.addEventListener('visibilitychange',()=>{if(document.hidden)clearTimeout(idleTimer);else scheduleHint();});

const palettes={r:'#b93d35',R:'#e76443',d:'#762b2e',g:'#637c3e',G:'#9baf5e',b:'#65462f',B:'#a27446',y:'#ffce69',w:'#f3dfad',o:'#df7b34',k:'#34372b'};
const sprites=[
 ['........g.......','.......gg.......','......b.GG......','......b.........','...rrr.rrr......','..rRRrrrrrr.....','.rRRrrrrrrrd....','.rRrrrrrrrrd....','.rrrrrrrrrrd....','.rrrrrrrrrrd....','..rrrrrrrrd.....','...rrddrrd......','....ddddd.......'],
 ['......y.........','.....yyy........','....ywwyo.......','....ywwyoo......','.....yyoo.......','.....BBB........','.....bBb........','.....bBb........','.....bBb........','.....bBb........','.....bBb........','.....bBb........','.....bbb........'],
 ['................','...dddddddddd...','..drRRRRRRRRdk..','.drRRRRRRRRddk..','.drrrrrrrrrddk..','.drwwwrrrrrddk..','.drrrrrrrrrddk..','.drrrrrrrrrddk..','.drrrrrrrrrddk..','.dddddddddddwk..','..wwwwwwwwwwkk..','..dddddddddddk..','................']
];
function art(which){if(which===2)return '<svg viewBox="1204 800 38 75" aria-hidden="true"><image href="/portfolio/assets/contact-worlds.png" width="1536" height="1024"/></svg>';if(which===0)return '<svg viewBox="216 235 58 62" aria-hidden="true"><defs><clipPath id="apple-cut"><path d="M244 239H251V237H272V245H268V250H260V254H266V263H268V276H264V285H259V291H249V294H233V291H225V286H220V278H217V260H221V253H230V250H241V245H244Z"/></clipPath></defs><image href="/portfolio/assets/contact-worlds.png" width="1536" height="1024" clip-path="url(#apple-cut)"/></svg>';return '<svg viewBox="0 0 16 14" aria-hidden="true" shape-rendering="crispEdges">'+sprites[which].flatMap((row,y)=>[...row].map((pixel,x)=>palettes[pixel]?`<rect x="${x}" y="${y}" width="1" height="1" fill="${palettes[pixel]}"/>`:'')).join('')+'</svg>';}
function place(el,box){el.style.left=box[0]+'%';el.style.top=box[1]+'%';if(box.length>2){el.style.width=box[2]+'%';el.style.height=box[3]+'%';}}
function choose(next){
 generation++;clearTimeout(timer);clearTimeout(idleTimer);index=next;phase='idle';selected=false;destination=null;drag=null;suppressClick=false;
 world.className='world';world.dataset.world=String(index);world.style.setProperty('--row',scenes[index].row);
 item.hidden=false;drop.hidden=false;entrance.hidden=true;item.disabled=false;
 item.style.transition='';item.className='world-item';item.innerHTML=art(index);item.setAttribute('aria-label',scenes[index].item+'を持つ');item.setAttribute('aria-pressed','false');
 drop.setAttribute('aria-label',scenes[index].target+'に置く');place(item,scenes[index].start);place(drop,scenes[index].drop);place(entrance,scenes[index].entrance);
 
 status.textContent='';
 scheduleHint();
}
function select(){if(phase!=='idle')return;if(!selected)effect('pick');selected=true;item.classList.add('selected');item.setAttribute('aria-pressed','true');world.classList.add('selecting');status.textContent='';}
async function loadForm(token){
 entrance.disabled=true;
 try{
  const response=await fetch('/portfolio/assets/contact-config.json',{cache:'no-store'});if(!response.ok)throw new Error('Unavailable');
  const url=decodeDestination(await response.json());if(token!==generation)return;
  destination=url;entrance.disabled=false;status.textContent='';entrance.focus({preventScroll:true});scheduleHint();
 }catch{if(token!==generation)return;destination=null;entrance.disabled=false;status.textContent='入口の準備ができませんでした。もう一度お試しください。';}
}
function solve(){
 if(phase!=='idle')return;clearTimeout(idleTimer);effect('place');phase='opening';selected=false;const token=generation;
 item.disabled=true;item.style.transition='left .22s ease, top .22s ease';place(item,scenes[index].drop.slice(0,2));drop.hidden=true;world.classList.remove('selecting');
 status.textContent='';
 if(index===1)world.classList.add('burning');
 const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
 timer=setTimeout(()=>{if(token!==generation)return;item.hidden=true;world.classList.add('revealed');world.classList.remove('burning');phase='cleared';effect('success');entrance.hidden=false;loadForm(token);},reduce?0:index===1?1800:300);
}
item.addEventListener('click',()=>{if(suppressClick){suppressClick=false;return;}select();});
drop.addEventListener('click',()=>{if(selected)solve();else status.textContent='';});
item.addEventListener('pointerdown',e=>{if(phase!=='idle'||e.button!==0)return;drag={id:e.pointerId,x:e.clientX,y:e.clientY,moved:false};item.setPointerCapture(e.pointerId);});
item.addEventListener('pointermove',e=>{if(!drag||e.pointerId!==drag.id)return;if(Math.hypot(e.clientX-drag.x,e.clientY-drag.y)>5){drag.moved=true;select();item.classList.add('dragging');const r=world.getBoundingClientRect();place(item,[(e.clientX-r.left)/r.width*100,(e.clientY-r.top)/r.height*100]);}});
item.addEventListener('pointerup',e=>{if(!drag||e.pointerId!==drag.id)return;const moved=drag.moved;drag=null;item.classList.remove('dragging');if(moved){suppressClick=true;const r=world.getBoundingClientRect();if(inside((e.clientX-r.left)/r.width*100,(e.clientY-r.top)/r.height*100,scenes[index].drop))solve();else{place(item,scenes[index].start);status.textContent='';}}});
item.addEventListener('pointercancel',()=>{drag=null;item.classList.remove('dragging');place(item,scenes[index].start);});
function enter(){if(phase!=='cleared')return;if(destination)location.assign(destination);else loadForm(generation);}
entrance.addEventListener('click',enter);
document.querySelector('#contact-reset').addEventListener('click',()=>choose(index));
choose(Math.floor(Math.random()*scenes.length));
