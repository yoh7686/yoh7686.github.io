document.documentElement.classList.add('js');
const menu = document.querySelector('.menu-toggle');
menu?.addEventListener('click', () => { const open = menu.getAttribute('aria-expanded') !== 'true'; menu.setAttribute('aria-expanded', String(open)); document.querySelector('.nav').classList.toggle('open', open); });
const query = document.querySelector('#query');
const year = document.querySelector('#year');
const kind = document.querySelector('#kind');
function filterEntries(){
 const term = (query?.value || '').normalize('NFKC').toLocaleLowerCase().trim(); let count=0;
 document.querySelectorAll('[data-entry]').forEach(entry=>{ const matches = (!term || entry.textContent.normalize('NFKC').toLocaleLowerCase().includes(term)) && (!year?.value || entry.dataset.year===year.value) && (!kind?.value || entry.dataset.kind===kind.value); entry.hidden=!matches; if(matches) count++; });
 document.querySelectorAll('[data-group]').forEach(group=>{group.hidden=![...group.querySelectorAll('[data-entry]')].some(entry=>!entry.hidden)});
 const status=document.querySelector('#result-count'); if(status)status.textContent=count+'件を表示';
 const empty=document.querySelector('#empty'); if(empty)empty.hidden=count>0;
}
[query,year,kind].forEach(input=>input?.addEventListener('input',filterEntries));
function revealAnchor(){
 const id=decodeURIComponent(location.hash.slice(1)); if(!id)return;
 const target=document.getElementById(id); if(!target)return;
 if(query)query.value='';if(year)year.value='';if(kind)kind.value='';filterEntries();
 requestAnimationFrame(()=>target.scrollIntoView({block:'start'}));
}
window.addEventListener('hashchange',revealAnchor); if(location.hash)revealAnchor();
document.querySelectorAll('.thumb img').forEach(img=>img.addEventListener('error',()=>{img.hidden=true;const fallback=document.createElement('span');fallback.textContent=img.alt;fallback.style.cssText='display:block;padding:25px;font-size:13px';img.parentElement.prepend(fallback)},{once:true}));
// Keep links from the former single-page activity archive working.
const routeData=document.querySelector('#activity-routes');
if(routeData&&location.hash){const routes=JSON.parse(routeData.textContent);const destination=routes[decodeURIComponent(location.hash.slice(1))];if(destination?.startsWith('/activities/'))location.replace(destination);}
