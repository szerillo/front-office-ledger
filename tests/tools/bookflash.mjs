import fs from 'fs'; import { createRequire } from 'module'; import { execSync } from 'child_process';
const require = createRequire(import.meta.url); const { chromium } = require(execSync('npm root -g').toString().trim() + '/playwright');
const b = await chromium.launch();
for(const v of ['home', 'trees', 'champs', 'report', 'heists', 'quiz', 'h2h']){ const p = await b.newPage({viewport: {width: 1280, height: 900}}); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  await p.route(/gc\.zgo\.at|goatcounter\.com|abacus\.jasoncameron|statsapi\.mlb\.com/, r => r.abort());
  await p.route(/^https:\/\/fol\.test\//, async r => { let u = new URL(r.request().url()).pathname.replace(/^\//, '') || 'index.html'; const f = '/home/claude/repo/' + u; if(!fs.existsSync(f)) return r.fulfill({status: 404, body: ''}); if(u === 'book.js') await new Promise(z => setTimeout(z, 5000)); r.fulfill({status: 200, contentType: f.endsWith('.json') ? 'application/json' : f.endsWith('.js') ? 'text/javascript' : 'text/html', body: fs.readFileSync(f)}); });
  await p.goto('https://fol.test/#view=' + v, {waitUntil: 'domcontentloaded', timeout: 120000}); await p.waitForTimeout(2500);
  const t = await p.evaluate(() => { const el = [...document.querySelectorAll('section[id^="view-"]')].find(e => !e.hidden); const x = el ? el.innerText : ''; return {len: x.length, raw: (x.match(/\{(net|dec):[^}]*\}/g) || []).length, nf: (x.match(/not on file|n\/a|undefined|NaN/g) || []).length, ready: [window.BOOK_READY, window.CARDS_READY]}; });
  console.log(v, 'before book', JSON.stringify(t), errs.slice(0, 2).join(' | ')); await p.close(); }
await b.close();
