// retry vs merge: the second card part (a) delayed 6 s, longer than the 1.5 s retry wait, (b) failing once then
// served, (c) served and then executed a second time. cardsMerge must run exactly once with all 152 clubs.
import { createRequire } from 'module'; import { execSync } from 'child_process';
const require = createRequire(import.meta.url); const { chromium } = require(execSync('npm root -g').toString().trim() + '/playwright');
const SITE = process.argv[2];
for (const mode of ['delay6s', 'failOnce', 'runTwice']) {
  const b = await chromium.launch(); const p = await b.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message.slice(0, 90)));
  await p.addInitScript(() => { window.__merges = 0; window.addEventListener('cards-loaded', () => window.__merges++); });
  await p.route(/statsapi|goatcounter|abacus/, r => r.abort());
  let n = 0;
  await p.route(/cards2\.[0-9a-f]{10}\.js/, async r => { n++;
    if (mode === 'delay6s') { await new Promise(s => setTimeout(s, 6000)); return r.continue(); }
    if (mode === 'failOnce' && n === 1) return r.abort();
    return r.continue(); });
  await p.goto('file://' + SITE + '/index.html', {waitUntil: 'load', timeout: 120000});
  await p.waitForFunction(() => window.CARDS_READY === true, null, {timeout: 40000}).catch(() => {});
  if (mode === 'runTwice') { await p.evaluate(src => new Promise(res => { const c = document.createElement('script'); c.src = src; c.onload = c.onerror = res; document.body.appendChild(c); }), [...await p.evaluate(() => [...document.scripts].map(s => s.src).filter(s => /cards2\./.test(s)))][0]); await p.waitForTimeout(500); }
  const r = await p.evaluate(() => ({ready: window.CARDS_READY === true, parts: window.CARD_PARTS, clubs: Object.keys(window.CARD_DETAIL || {}).length, merges: window.__merges, banner: !!document.getElementById('cards-fail'), scripts: [...document.scripts].filter(s => /cards2\./.test(s.src)).length}));
  console.log(mode, 'requests', n, JSON.stringify(r), 'errors', errs.length);
  await b.close();
}
