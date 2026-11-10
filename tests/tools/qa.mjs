// user-eye sweep of the local build: every view, desktop and phone; text anomalies, overflow, dead buttons
import fs from 'fs'; import { createRequire } from 'module'; import { execSync } from 'child_process';
const require = createRequire(import.meta.url); const { chromium } = require(execSync('npm root -g').toString().trim() + '/playwright');
const b = await chromium.launch(); const out = [];
for(const [w, h] of [[1280, 900], [390, 844]]){
  const mobile = w < 600; const p = await b.newPage({viewport: {width: w, height: h}, isMobile: mobile, hasTouch: mobile});
  const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 140)));
  await p.route(/gc\.zgo\.at|goatcounter\.com/, r => r.abort());
  await p.route(/^https:\/\/fol\.test\//, r => { let u = new URL(r.request().url()).pathname.replace(/^\//, '') || 'index.html'; const f = u === 'index.html' ? '/home/claude/front-office-ledger-prototype.html' : '/home/claude/repo/' + u; if(!fs.existsSync(f)) return r.fulfill({status: 404, body: ''}); r.fulfill({status: 200, contentType: f.endsWith('.json') ? 'application/json' : f.endsWith('.js') ? 'text/javascript' : 'text/html', body: fs.readFileSync(f)}); });
  await p.goto('https://fol.test/', {waitUntil: 'load', timeout: 120000}); await p.waitForTimeout(5000);
  const res = await p.evaluate(async () => {
    const wait = ms => new Promise(z => setTimeout(z, ms)), R = [];
    const views = ['home', 'leaderboard', 'report', 'champs', 'dna', 'h2h', 'heists', 'trees', 'wire', 'stove', 'boards', 'pickem', 'horizon', 'offs', 'desk', 'gm', 'scen', 'quiz', 'dudes', 'method'];
    for(const v of views){
      try { switchView(v); } catch(e){ R.push(v + ': THROW ' + e.message); continue; }
      await wait(v === 'wire' || v === 'stove' || v === 'offs' || v === 'dudes' ? 1800 : 500);
      const el = document.getElementById('view-' + v), t = el.innerText;
      const bad = (t.match(/undefined|NaN|\[object|null\b|Infinity|\$-|\+-|--\d/g) || []).slice(0, 5);
      const over = document.documentElement.scrollWidth - document.documentElement.clientWidth;
      const empties = [...el.querySelectorAll('.card')].filter(c => c.offsetParent && c.innerText.trim().length < 3).length;
      const tiny = innerWidth < 600 ? [...el.querySelectorAll('button, a.actbtn, select')].filter(x => x.offsetParent && x.getBoundingClientRect().height > 0 && x.getBoundingClientRect().height < 28).length : 0;
      R.push(`${v}: chars ${t.length}${bad.length ? ' BAD[' + bad.join(',') + ']' : ''}${over > 2 ? ' OVERFLOW ' + over : ''}${empties ? ' emptyCards ' + empties : ''}${tiny ? ' smallTapTargets ' + tiny : ''}`);
    }
    return R;
  });
  out.push(`== ${w}px`, ...res, 'errors: ' + (errs.length ? errs.join(' | ') : 'none')); await p.close();
}
console.log(out.join('\n')); await b.close();
