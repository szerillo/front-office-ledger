// render every view that shows front-office grades (home, both leaderboard eras, every report card, DNA, boards,
// Deal Desk GM lines for every club) and collect each letter-helper call that got a null grade.
// NULLALL=1 first sets every regime grade to null (the seed).
import { createRequire } from 'module'; import { execSync } from 'child_process'; import fs from 'fs';
const require = createRequire(import.meta.url); const { chromium } = require(execSync('npm root -g').toString().trim() + '/playwright');
const dir = process.argv[2];
const b = await chromium.launch(); const p = await b.newPage({viewport: {width: 1400, height: 900}}); const errs = [];
p.on('pageerror', e => errs.push(e.message.slice(0, 120)));
await p.route(/statsapi|goatcounter|abacus/, r => r.abort());
await p.goto('file://' + dir + '/index.html', {waitUntil: 'load', timeout: 120000});
await p.waitForFunction(() => window.CARDS_READY === true && window.MOVES_READY === true, null, {timeout: 90000}).catch(() => {});
const res = await p.evaluate(async (nullAll) => {
  const all = [...AUTO_REGIMES, ...LB_HIST];
  if(nullAll) all.forEach(r => { r.forGrade = null; if(r.success) r.success.g = null; if(r.dev) r.dev.g = null;
    Object.values(r.chan || {}).forEach(c => { if(c){ c.g = null; if('g2' in c) c.g2 = null; } }); });
  window.__nullLog = [];
  const tick = () => new Promise(r => setTimeout(r, 0)); const views = {};
  const run = async (name, fn) => { const n0 = window.__nullLog.length; try { fn(); } catch(e){ views[name + ' ERROR'] = String(e).slice(0, 80); } await tick(); views[name] = (views[name] || 0) + window.__nullLog.length - n0; };
  await run('home', () => switchView('home'));
  for(const v of ['leaderboard', 'dna', 'boards', 'heists', 'offs']) await run(v, () => switchView(v));
  if(typeof setv === 'function' && typeof renderLB === 'function'){ await run('leaderboard hist', () => { setv('erasel', 'hist'); renderLB(); }); }
  for(const r of all) await run('report cards', () => switchView('report', r.id));
  // Deal Desk GM lines: one trade per club pair (club i with club i+1)
  const clubs = Object.keys(DESK.teams || {}).sort(); const P = c => DESK.players.find(x => x[2] === c && Math.abs(x[5]) + Math.abs(x[6]) + Math.abs(x[7]) >= 1.5);
  for(let i = 0; i < clubs.length; i++){ const a = clubs[i], c = clubs[(i + 1) % clubs.length], pa = P(a), pc = P(c); if(!pa || !pc) continue;
    await run('desk GM lines', () => { Object.assign(dkState, {mode: 'trade', you: a, them: c, send: [{kind: 'player', p: pa, ctrl: gmCtrlOf(pa)}], recv: [{kind: 'player', p: pc, ctrl: gmCtrlOf(pc)}]}); dkTradeVerdict({done: true}); }); }
  const lines = document.documentElement.outerHTML; // not used
  return {views, log: window.__nullLog};
}, !!process.env.NULLALL);
const src = fs.readFileSync(dir + '/index.html', 'utf8').split('\n');
const by = {};
for(const [fn, ln, out] of res.log){ const k = `${fn} line ${ln}: ${(src[+ln - 1] || '').trim().slice(0, 70)} => "${out}"`; by[k] = (by[k] || 0) + 1; }
console.log(JSON.stringify({views: res.views, calls: by, errors: errs.slice(0, 5)}, null, 1));
await b.close();
