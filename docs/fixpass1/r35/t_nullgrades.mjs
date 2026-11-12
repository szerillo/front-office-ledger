// Nov 12 (round 35): a missing grade never prints as a letter. Unit checks on the letter helpers, then every
// front-office grade set to null and the views that show them re-rendered: no grade chip, tile or GM line may show
// a letter. (Round 35 found live printing "F" for an ungraded development tile.)
import { open, report } from './_common.mjs';
const {browser, page, errors} = await open();
const r = await page.evaluate(async () => {
  const isL = t => /^(A\+|A−|A|B\+|B|C\+|C|D\+|D|F)$/.test(String(t).trim());
  const o = {};
  o.g2letterNull = [null, undefined, NaN].every(g => !isL(g2letter(g)));
  o.gradeClassNull = [null, undefined, NaN].every(g => gradeClass(g) === 'gnone');
  o.deskLetterNaN = !isL(deskLetter(NaN, 1));
  const all = [...AUTO_REGIMES, ...LB_HIST];
  all.forEach(x => { x.forGrade = null; if(x.success) x.success.g = null; if(x.dev) x.dev.g = null; Object.values(x.chan || {}).forEach(c => { if(c){ c.g = null; if('g2' in c) c.g2 = null; } }); });
  const bad = [];
  const scan = where => document.querySelectorAll('.tile, .hub-row, .hub-lb, #lb tr, .agm-list li, .agm-list div').forEach(e => {
    if(!e.offsetParent) return;   // only what is on screen now
    const lbl = (e.querySelector('.lbl') || {}).textContent || '';
    if(e.classList.contains('tile') && !/Overall grade|Team success|Player development|On the field/.test(lbl)) return;
    e.querySelectorAll('.grade, .stamp').forEach(g => { if(isL(g.textContent)) bad.push(where + ': ' + (lbl || e.className) + ' ' + g.textContent); }); });
  switchView('home'); scan('home'); switchView('leaderboard'); if(typeof renderLB === 'function') renderLB(); scan('leaderboard');
  for(const x of all.slice(0, 60)){ switchView('report', x.id); scan('report ' + x.id); }
  const clubs = Object.keys(DESK.teams || {}).sort(); const P = c => DESK.players.find(x => x[2] === c && Math.abs(x[5]) + Math.abs(x[6]) + Math.abs(x[7]) >= 1.5);
  for(let i = 0; i < clubs.length; i++){ const a = clubs[i], c = clubs[(i + 1) % clubs.length]; if(!P(a) || !P(c)) continue;
    Object.assign(dkState, {mode: 'trade', you: a, them: c, send: [{kind: 'player', p: P(a), ctrl: gmCtrlOf(P(a))}], recv: [{kind: 'player', p: P(c), ctrl: gmCtrlOf(P(c))}]});
    const h = dkTradeVerdict({done: true}); const m = h.match(/trade grade (A\+|A−|A|B\+|B|C\+|C|D\+|D|F) over/); if(m) bad.push('desk ' + a + '-' + c + ': ' + m[0]); }
  o.noLetterForNullGrade = bad.length === 0; o._examples = bad.slice(0, 5); o._count = bad.length;
  return o; });
await browser.close();
report('t_nullgrades', r, errors);
