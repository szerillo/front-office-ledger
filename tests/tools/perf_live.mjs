import { createRequire } from 'module'; import { execSync } from 'child_process';
const require = createRequire(import.meta.url); const { chromium, devices } = require(execSync('npm root -g').toString().trim() + '/playwright');
const b = await chromium.launch();
for(const [name, down, up, rtt, cpu] of [['4G', 9e6 / 8, 9e6 / 8, 170, 4], ['slow 4G', 1.6e6 / 8, 750e3 / 8, 300, 4]]){
  const ctx = await b.newContext({...devices['iPhone 13']}); const p = await ctx.newPage(); const c = await ctx.newCDPSession(p);
  await c.send('Network.enable'); await c.send('Network.emulateNetworkConditions', {offline: false, downloadThroughput: down, uploadThroughput: up, latency: rtt}); await c.send('Emulation.setCPUThrottlingRate', {rate: cpu});
  await p.route(/gc\.zgo\.at|goatcounter\.com/, r => r.abort());
  const t0 = Date.now(); const url = process.argv[2] || 'https://frontofficeledger.com/';
  await p.goto(url + '?cb=' + Date.now(), {waitUntil: 'commit', timeout: 180000});
  const res = await p.evaluate(() => new Promise(done => { const o = {}; const t = setInterval(() => {
    const fcp = performance.getEntriesByName('first-contentful-paint')[0]; if(fcp && !o.fcp) o.fcp = Math.round(fcp.startTime);
    const home = document.querySelector('#view-home'); if(!o.home && home && home.textContent.trim().length > 400) o.home = Math.round(performance.now());
    if(!o.dcl && document.readyState !== 'loading') o.dcl = Math.round(performance.now());
    if(!o.cards && typeof CARDS_READY !== 'undefined' && CARDS_READY) o.cards = Math.round(performance.now());
    if((o.cards && o.home) || performance.now() > 150000){ clearInterval(t); done(o); } }, 100); }));
  const sizes = await p.evaluate(() => performance.getEntriesByType('resource').concat(performance.getEntriesByType('navigation')).filter(e => e.transferSize > 20000).map(e => e.name.split('/').pop().split('?')[0] + ' ' + Math.round(e.transferSize / 1024) + 'KB'));
  console.log(name, JSON.stringify(res), sizes.join(', ')); await ctx.close();
}
await b.close();
