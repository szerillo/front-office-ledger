import { createRequire } from 'module'; import { execSync } from 'child_process';
const require = createRequire(import.meta.url); const { chromium } = require(execSync('npm root -g').toString().trim() + '/playwright');
const b = await chromium.launch(); const p = await b.newPage(); await p.route(/statsapi|goatcounter|abacus/, r => r.abort());
await p.goto(process.argv[2], {waitUntil: 'load', timeout: 120000}); await p.waitForFunction(() => window.CARDS_READY === true, null, {timeout: 40000}).catch(() => {});
const r = await p.evaluate(() => { const c = AUTO_REGIMES.find(x => x.id === 'chc'); const D = (window.CARD_DETAIL || {}).chc || {};
  const s = JSON.stringify(c); const m = s.match(/Megill[^\]]{0,80}/g); return {overall: c.forGrade, waiverNet: c.chan.waiver.net, detailKeys: Object.keys(D).slice(0, 12), megill: (m || []).slice(0, 2)}; });
console.log(JSON.stringify(r)); await b.close();
