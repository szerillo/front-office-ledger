// old index.html (live before 8de35fd) + new data files, served over http like Pages (query strings ignored)
import { createRequire } from 'module'; import { execSync } from 'child_process';
const require = createRequire(import.meta.url); const { chromium } = require(execSync('npm root -g').toString().trim() + '/playwright');
const b = await chromium.launch(); const p = await b.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message.slice(0, 120)));
const got = []; p.on('response', r => { if(/\.(js|json)/.test(r.url()) && /127\.0\.0\.1/.test(r.url())) got.push(r.url().replace(/.*\//, '') + ' ' + r.status()); });
await p.route(/statsapi|goatcounter|abacus/, r => r.abort());
await p.goto(process.argv[2], {waitUntil: 'load', timeout: 120000});
await p.waitForFunction(() => window.CARDS_READY === true, null, {timeout: 40000}).catch(() => {});
await p.waitForTimeout(3000);
const r = await p.evaluate(() => { const c = AUTO_REGIMES.find(x => x.id === 'chc'); const ph = AUTO_REGIMES.find(x => x.id === 'phi');
  return {ready: window.CARDS_READY === true, banner: !!document.getElementById('cards-fail'), clubsInCards: Object.keys(window.CARD_DETAIL || {}).length,
    chc: {overall: c.forGrade, waiverNet: c.chan.waiver.net, waiverG: c.chan.waiver.g, ledgerRows: (c.chanLedgers && c.chanLedgers.waiver || []).length},
    phi: {overall: ph.forGrade, waiverNet: ph.chan.waiver.net}, tradeBookTrades: TRADE_BOOK.trades.length}; });
console.log(JSON.stringify(r), '| errors', errs.length, errs.slice(0, 3), '| loaded', got.filter(x => /cards|book|moves|offseasons/.test(x)).join(', '));
await b.close();
