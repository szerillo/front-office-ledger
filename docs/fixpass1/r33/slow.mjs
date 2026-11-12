// cold visit under network throttling: time to CARDS_READY and whether the "did not finish loading" banner appears
import { createRequire } from 'module'; import { execSync } from 'child_process';
const require = createRequire(import.meta.url); const { chromium } = require(execSync('npm root -g').toString().trim() + '/playwright');
const [site, prof] = process.argv.slice(2);
const P = {slow4g: {latency: 150, downloadThroughput: 1.6e6 / 8 * 0.9, uploadThroughput: 750e3 / 8 * 0.9}, slow3g: {latency: 400, downloadThroughput: 400e3 / 8 * 0.9, uploadThroughput: 400e3 / 8 * 0.9}}[prof];
const b = await chromium.launch(); const ctx = await b.newContext(); const p = await ctx.newPage();
const cdp = await ctx.newCDPSession(p); await cdp.send('Network.enable');
await cdp.send('Network.emulateNetworkConditions', {offline: false, ...P}); await cdp.send('Emulation.setCPUThrottlingRate', {rate: 4});
await cdp.send('Network.setBlockedURLs', {urls: ['*statsapi*', '*goatcounter*', '*abacus*']});
const t0 = Date.now(); p.goto(`http://127.0.0.1:8767/${site}/?t=${t0}`, {timeout: 180000}).catch(() => {});
let banner = null, ready = null;
while(Date.now() - t0 < 150000 && ready === null){ await new Promise(r => setTimeout(r, 500));
  const s = await p.evaluate(() => ({b: !!document.getElementById('cards-fail'), r: window.CARDS_READY === true})).catch(() => ({}));
  if(s.b && banner === null) banner = ((Date.now() - t0) / 1000).toFixed(1); if(s.r) ready = ((Date.now() - t0) / 1000).toFixed(1); }
const left = await p.evaluate(() => !!document.getElementById('cards-fail')).catch(() => null);
console.log(site, prof, 'cards ready at', ready, 's; banner shown at', banner, '; banner still up after ready:', left);
await b.close();
