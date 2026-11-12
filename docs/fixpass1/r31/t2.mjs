import { createRequire } from 'module'; import { execSync } from 'child_process'; import fs from 'fs';
const require = createRequire(import.meta.url); const { chromium } = require(execSync('npm root -g').toString().trim() + '/playwright');
const b = await chromium.launch(); const ctx = await b.newContext(); const p = await ctx.newPage();
// no routing: Playwright turns the HTTP cache off when routes are set
const probe = async () => { await p.waitForTimeout(5000); return await p.evaluate(async () => {
  const chc = AUTO_REGIMES.find(x => x.id === 'chc');
  const u = (document.documentElement.innerHTML.match(/offseasons\.json\?v=[0-9a-f]+/) || ['offseasons.json?v=1'])[0]; const o = await fetch(u).then(r => r.json()); const w = o.rows.find(r => r[0] === 'WSH' && r[1] === 2019);
  return {chcWaiver: chc.chan.waiver.net, wsh2019: w[9]}; }); };
await p.goto('http://127.0.0.1:8766/?visit=1'); console.log('old site', JSON.stringify(await probe()));
fs.unlinkSync('/tmp/cachetest/cur'); fs.symlinkSync(process.env.NEW, '/tmp/cachetest/cur');
await p.goto('http://127.0.0.1:8766/?visit=2'); console.log('after swap, same browser', JSON.stringify(await probe()));
const p2 = await (await b.newContext()).newPage(); await p2.route('**/statsapi.mlb.com/**', r => r.abort());
await b.close();
