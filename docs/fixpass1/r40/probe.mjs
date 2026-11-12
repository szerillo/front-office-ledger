import { createRequire } from 'module'; import { execSync } from 'child_process';
const require = createRequire(import.meta.url); const { chromium } = require(execSync('npm root -g').toString().trim() + '/playwright');
const b = await chromium.launch(); const p = await b.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message.slice(0, 100)));
const got = []; p.on('response', r => { if(/127\.0\.0\.1/.test(r.url()) && /\.(js|json)/.test(r.url())) got.push(r.url().replace(/.*\//, '').replace(/\?.*/, '') + ':' + r.status()); });
await p.route(/statsapi|goatcounter|abacus/, r => r.abort());
await p.goto(process.argv[2], {waitUntil: 'load', timeout: 120000});
await p.waitForFunction(() => window.CARDS_READY === true, null, {timeout: 40000}).catch(() => {});
await p.waitForTimeout(2500);
const r = await p.evaluate(async () => { const c = AUTO_REGIMES.find(x => x.id === 'chc');
  let offs = null; try { await offsLoad(); offs = (OFFS.data && OFFS.data.rows || OFFS.rows || []).length || 'loaded'; } catch(e){ offs = 'ERR ' + e.message; }
  const meg = JSON.stringify(window.CARD_DETAIL && window.CARD_DETAIL.chc || {}).match(/Megill/g);
  return {ready: window.CARDS_READY === true, banner: !!document.getElementById('cards-fail'), clubs: Object.keys(window.CARD_DETAIL || {}).length,
    chcOverall: c.forGrade, chcWaiverNet: c.chan.waiver.net, megillInChcCard: !!meg, trades: TRADE_BOOK.trades.length, offsErr: OFFS.err || null}; });
console.log(JSON.stringify(r), '| errors', errs.length, '| 404s', got.filter(x => /:404/.test(x)).join(',') || 'none', '| loaded', got.filter(x => /cards|book|moves|offseasons|deals/.test(x)).join(','));
await b.close();
