import fs from 'fs'; import { createRequire } from 'module'; import { execSync } from 'child_process';
const require = createRequire(import.meta.url); const { chromium } = require(execSync('npm root -g').toString().trim() + '/playwright');
const b = await chromium.launch(); const views = (process.argv[2] || 'home,heists,trees,quiz,h2h,report,wire,leaderboard,champs,dna,offs,stove,desk,scen,pickem,horizon,boards').split(',');
const grab = async (split, v) => { const p = await b.newPage({viewport: {width: 1280, height: 900}}); const errs = []; p.on('pageerror', e => errs.push(String(e).slice(0, 160)));
  await p.route(/gc\.zgo\.at|goatcounter\.com|abacus\.jasoncameron|statsapi\.mlb\.com/, r => r.abort());
  await p.route(/^https:\/\/fol\.test\//, async r => { let u = new URL(r.request().url()).pathname.replace(/^\//, '') || 'index.html'; const f = u === 'index.html' ? (split ? '/home/claude/repo/index.html' : '/home/claude/front-office-ledger-prototype.html') : '/home/claude/repo/' + u; if(!fs.existsSync(f)) return r.fulfill({status: 404, body: ''}); if(u === 'book.js') await new Promise(z => setTimeout(z, 4000)); r.fulfill({status: 200, contentType: f.endsWith('.json') ? 'application/json' : f.endsWith('.js') ? 'text/javascript' : 'text/html', body: fs.readFileSync(f)}); });
  await p.goto('https://fol.test/#view=' + v, {waitUntil: 'load', timeout: 120000}); await p.waitForFunction(() => window.CARDS_READY, null, {timeout: 60000}); await p.waitForTimeout(2500);
  const t = await p.evaluate(() => { const el = [...document.querySelectorAll('section[id^="view-"]')].find(e => !e.hidden); return (el ? el.innerText : '').replace(/Updated [\d:]+ [AP]M/g, '').replace(/\d+ (days?|hours?|minutes?|seconds?)/g, 'N').replace(/\s+/g, ' '); });
  await p.close(); return {t, errs}; };
for(const v of views){ const a = await grab(false, v), c = await grab(true, v); let i = 0; while(i < a.t.length && a.t[i] === c.t[i]) i++;
  console.log(v, a.t.length, c.t.length, a.t === c.t ? 'SAME' : 'DIFF at ' + i + ': [' + a.t.slice(Math.max(0, i - 60), i + 90) + '] vs [' + c.t.slice(Math.max(0, i - 60), i + 90) + ']', c.errs.length ? 'ERRS ' + c.errs.slice(0, 2).join(' | ') : ''); }
await b.close();
