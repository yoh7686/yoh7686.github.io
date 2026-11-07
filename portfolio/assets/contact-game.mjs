import {solved, rotate, connected} from './contact-route.mjs';
const board = document.querySelector('#contact-board');
const status = document.querySelector('#contact-status');
const finish = document.querySelector('#contact-finish');
const action = document.querySelector('#contact-open');
const names = ['上', '右', '下', '左'];
let cells, cleared = false, target = null;
function draw() {
  board.replaceChildren();
  cells.forEach((mask, index) => {
    const button = document.createElement('button'); button.type = 'button';
    button.className = 'route-tile'; button.disabled = cleared;
    button.setAttribute('aria-label', `${Math.floor(index/3)+1}行${index%3+1}列：${names.filter((_,d)=>mask&(1<<d)).join('・')}。押すと右に90度回転`);
    const lines = ['M50 50V0','M50 50H100','M50 50V100','M50 50H0'].filter((_,d)=>mask&(1<<d)).join(' ');
    button.innerHTML = `<svg viewBox="0 0 100 100" aria-hidden="true"><path d="${lines}"/><circle cx="50" cy="50" r="6"/></svg>`;
    button.addEventListener('click', () => {
      cells[index] = rotate(cells[index]);
      if (connected(cells)) { cleared = true; draw(); unlock(); }
      else { draw(); board.children[index].focus(); }
    });
    board.append(button);
  });
}
async function unlock() {
  finish.hidden = false; action.disabled = true;
  status.textContent = 'つながりました。お問い合わせフォームを準備しています。';
  try {
    const response = await fetch('/portfolio/assets/contact-config.json', {cache:'no-store'});
    if (!response.ok) throw new Error('Configuration unavailable');
    const config = await response.json();
    const id = atob(config.formIdEncoded);
    if (!/^1FAIpQL[A-Za-z0-9_-]+$/.test(id)) throw new Error('Invalid form identifier');
    target = ['https:', '', ['docs','google','com'].join('.'), 'forms', 'd', 'e', id, 'viewform'].join('/');
    action.disabled = false; action.textContent = 'お問い合わせフォームへ ↗';
    status.textContent = 'つながりました。下のボタンからお問い合わせいただけます。';
    action.focus();
  } catch {
    target = null; action.disabled = false; action.textContent = 'もう一度読み込む';
    status.textContent = 'フォームを読み込めませんでした。もう一度お試しください。';
  }
}
action.addEventListener('click', () => { if (target) window.location.assign(target); else unlock(); });
function reset() {
  cleared = false; target = null; finish.hidden = true;
  cells = solved.map(mask => rotate(mask));
  status.textContent = '左の入口から右下の出口まで、線をつないでください。'; draw();
}
document.querySelector('#contact-reset').addEventListener('click', reset);
document.querySelector('#contact-hint').addEventListener('click', () => {
  document.querySelector('#contact-hint-text').hidden = false;
});
reset();
