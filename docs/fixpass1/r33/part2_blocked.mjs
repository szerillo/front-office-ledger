// what a visitor sees when the second part never arrives (blocked), v1 vs v2, after 25 s
import { createRequire } from 'module'; import { execSync } from 'child_process'; import fs from 'fs';
const require = createRequire(import.meta.url); const { chromium } = require(execSync('npm root -g').toString().trim() + '/playwright');
const [SITE] = process.argv.slice(2);
fs.rmSync('/tmp/cachetest/cur', {force: true}); fs.symlinkSync('/tmp/cachetest/' + SITE, '/tmp/cachetest/cur');
const b = await chromium.launch(); const ctx = await b.newContext({viewport: {width: 1400, height: 900}}); const p = await ctx.newPage();
const errs = []; p.on('pageerror', e => errs.push(e.message.slice(0, 100)));
const cdp = await ctx.newCDPSession(p); await cdp.send('Network.enable'); await cdp.send('Network.setBlockedURLs', {urls: ['*cards2*', '*statsapi*', '*goatcounter*']});
const t0 = Date.now(); await p.goto('http://127.0.0.1:8766/?visit=' + Date.now() + '#view=card&id=chc');
let bannerAt = null; for(let i = 0; i < 26; i++){ await p.waitForTimeout(1000); if(bannerAt === null && await p.evaluate(() => !!document.getElementById('cards-fail'))) bannerAt = ((Date.now() - t0) / 1000).toFixed(1); }
const r = await p.evaluate(() => ({ready: window.CARDS_READY === true, merged: AUTO_REGIMES.filter(r => r.chanLedgers).length, loading: (document.body.innerText.match(/Loading[^\n]{0,60}/g) || []).slice(0, 3)}));
await p.screenshot({path: `/tmp/cachetest/blocked_${SITE}.png`});
console.log(SITE, 'banner at', bannerAt, 's', JSON.stringify(r), 'errors', errs.length);
await b.close();
